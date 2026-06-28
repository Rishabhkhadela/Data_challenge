"""Embedding service for candidate semantic-search documents."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


BGE_LARGE_MODEL_NAME = "BAAI/bge-large-en-v1.5"


class EmbeddingModel(Protocol):
    """Minimal SentenceTransformer-compatible encoder protocol."""

    def encode(
        self,
        sentences: Sequence[str],
        *,
        batch_size: int,
        convert_to_numpy: bool,
        normalize_embeddings: bool,
        show_progress_bar: bool,
    ) -> Any:
        """Encode text into dense embeddings."""


@dataclass(frozen=True)
class EmbeddingResult:
    """Embeddings and aligned document metadata."""

    embeddings: Any
    metadata: list[dict[str, Any]]
    texts: list[str]
    model_name: str
    normalized: bool


class EmbeddingService:
    """Build, batch, and persist BGE-large candidate embeddings."""

    def __init__(
        self,
        model_name: str = BGE_LARGE_MODEL_NAME,
        *,
        device: str | None = None,
        batch_size: int = 32,
        normalize_embeddings: bool = True,
        model: EmbeddingModel | None = None,
    ) -> None:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")

        self.model_name = model_name
        self.device = device or _auto_device()
        self.batch_size = batch_size
        self.normalize_embeddings = normalize_embeddings
        self._model = model

    @property
    def model(self) -> EmbeddingModel:
        """Load the underlying embedding model lazily."""

        if self._model is None:
            self._model = _load_sentence_transformer(self.model_name, self.device)
        return self._model

    def embed_texts(
        self,
        texts: Sequence[str],
        *,
        batch_size: int | None = None,
        show_progress_bar: bool = True,
    ) -> Any:
        """Embed raw text strings with batched BGE-large inference."""

        clean_texts = [_clean_text(text) for text in texts]
        return self.model.encode(
            clean_texts,
            batch_size=batch_size or self.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize_embeddings,
            show_progress_bar=show_progress_bar,
        )

    def embed_documents(
        self,
        documents: Iterable[Mapping[str, Any]],
        *,
        batch_size: int | None = None,
        show_progress_bar: bool = True,
    ) -> EmbeddingResult:
        """Embed candidate documents created by candidate_builder.build_candidate_documents."""

        materialized = list(documents)
        texts = [_clean_text(document.get("text", "")) for document in materialized]
        metadata = [_document_metadata(document) for document in materialized]
        embeddings = self.embed_texts(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
        )
        return EmbeddingResult(
            embeddings=embeddings,
            metadata=metadata,
            texts=texts,
            model_name=self.model_name,
            normalized=self.normalize_embeddings,
        )

    def save_embeddings(
        self,
        result: EmbeddingResult,
        output_dir: str | Path,
        *,
        include_text: bool = False,
    ) -> None:
        """Save embeddings, metadata, and a manifest to disk."""

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        embeddings_path = output_path / "embeddings.npy"
        metadata_path = output_path / "metadata.jsonl"
        manifest_path = output_path / "manifest.json"

        np = _import_numpy()
        embeddings = np.asarray(result.embeddings, dtype="float32")
        np.save(embeddings_path, embeddings)

        with metadata_path.open("w", encoding="utf-8") as metadata_file:
            for index, metadata in enumerate(result.metadata):
                row = dict(metadata)
                row["embedding_index"] = index
                if include_text:
                    row["text"] = result.texts[index]
                metadata_file.write(json.dumps(row, ensure_ascii=False) + "\n")

        manifest = {
            "model_name": result.model_name,
            "device": self.device,
            "batch_size": self.batch_size,
            "normalized": result.normalized,
            "embedding_count": int(embeddings.shape[0]),
            "embedding_dimension": int(embeddings.shape[1]) if embeddings.ndim == 2 else None,
            "embeddings_file": embeddings_path.name,
            "metadata_file": metadata_path.name,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def embed_and_save_documents(
        self,
        documents: Iterable[Mapping[str, Any]],
        output_dir: str | Path,
        *,
        batch_size: int | None = None,
        show_progress_bar: bool = True,
        include_text: bool = False,
    ) -> EmbeddingResult:
        """Embed documents and persist the resulting vector store files."""

        result = self.embed_documents(
            documents,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
        )
        self.save_embeddings(result, output_dir, include_text=include_text)
        return result


def _document_metadata(document: Mapping[str, Any]) -> dict[str, Any]:
    metadata = document.get("metadata")
    if isinstance(metadata, Mapping):
        output = dict(metadata)
    else:
        output = {}

    candidate_id = document.get("candidate_id")
    if candidate_id is not None:
        output.setdefault("candidate_id", candidate_id)
    return output


def _clean_text(text: Any) -> str:
    return str(text or "").strip()


def _auto_device() -> str:
    try:
        import torch
    except ImportError:
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def _load_sentence_transformer(model_name: str, device: str) -> EmbeddingModel:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "sentence-transformers is required to build BGE embeddings. "
            "Install project dependencies before running the embedding service."
        ) from exc

    return SentenceTransformer(model_name, device=device)


def _import_numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "numpy is required to save embeddings. Install project dependencies first."
        ) from exc
    return np
