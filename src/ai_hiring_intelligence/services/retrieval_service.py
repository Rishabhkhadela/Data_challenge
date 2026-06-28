"""FAISS retrieval for embedded candidate profiles."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from ai_hiring_intelligence.services.embedding_service import EmbeddingService


Metric = Literal["cosine", "inner_product", "l2"]


@dataclass(frozen=True)
class RetrievalResult:
    """One candidate returned from vector search."""

    candidate_id: str
    score: float
    rank: int
    metadata: dict[str, Any]


class FaissCandidateRetriever:
    """Build, save, load, and query a FAISS candidate index."""

    def __init__(
        self,
        *,
        metric: Metric = "cosine",
        index: Any | None = None,
        metadata: Sequence[Mapping[str, Any]] | None = None,
    ) -> None:
        if metric not in ("cosine", "inner_product", "l2"):
            raise ValueError("metric must be one of: cosine, inner_product, l2")

        self.metric = metric
        self.index = index
        self.metadata = [dict(item) for item in metadata] if metadata is not None else []

    @classmethod
    def from_embeddings(
        cls,
        embeddings: Any,
        metadata: Sequence[Mapping[str, Any]],
        *,
        metric: Metric = "cosine",
    ) -> "FaissCandidateRetriever":
        """Create a FAISS index from candidate embeddings and aligned metadata."""

        retriever = cls(metric=metric)
        retriever.build(embeddings, metadata)
        return retriever

    def build(self, embeddings: Any, metadata: Sequence[Mapping[str, Any]]) -> None:
        """Build an in-memory FAISS index."""

        vectors = _as_float32_matrix(embeddings)
        if vectors.shape[0] != len(metadata):
            raise ValueError("metadata length must match number of embeddings")

        indexed_vectors = _prepare_vectors(vectors, self.metric)
        faiss = _import_faiss()
        if self.metric == "l2":
            self.index = faiss.IndexFlatL2(indexed_vectors.shape[1])
        else:
            self.index = faiss.IndexFlatIP(indexed_vectors.shape[1])

        self.index.add(indexed_vectors)
        self.metadata = [dict(item) for item in metadata]

    def search(self, query_embedding: Any, *, top_k: int = 10) -> list[RetrievalResult]:
        """Return top K candidates for a query embedding."""

        if self.index is None:
            raise RuntimeError("FAISS index has not been built or loaded")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        query = _as_float32_matrix(query_embedding)
        if query.shape[0] != 1:
            raise ValueError("query_embedding must contain exactly one vector")

        query = _prepare_vectors(query, self.metric)
        search_k = min(top_k, len(self.metadata))
        distances, indices = self.index.search(query, search_k)

        results: list[RetrievalResult] = []
        for rank, (index, distance) in enumerate(zip(indices[0], distances[0], strict=True), start=1):
            if index < 0:
                continue
            item_metadata = dict(self.metadata[int(index)])
            candidate_id = str(item_metadata.get("candidate_id", ""))
            results.append(
                RetrievalResult(
                    candidate_id=candidate_id,
                    score=_score_from_distance(float(distance), self.metric),
                    rank=rank,
                    metadata=item_metadata,
                )
            )
        return results

    def search_text(
        self,
        query_text: str,
        embedding_service: EmbeddingService,
        *,
        top_k: int = 10,
        show_progress_bar: bool = False,
    ) -> list[RetrievalResult]:
        """Embed query text with the configured embedding service and return top K candidates."""

        query_embedding = embedding_service.embed_texts(
            [query_text],
            batch_size=1,
            show_progress_bar=show_progress_bar,
        )
        return self.search(query_embedding, top_k=top_k)

    def save(self, output_dir: str | Path) -> None:
        """Persist the FAISS index, metadata, and manifest."""

        if self.index is None:
            raise RuntimeError("FAISS index has not been built or loaded")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        faiss = _import_faiss()
        index_path = output_path / "candidates.faiss"
        metadata_path = output_path / "candidate_metadata.jsonl"
        manifest_path = output_path / "retrieval_manifest.json"

        faiss.write_index(self.index, str(index_path))
        with metadata_path.open("w", encoding="utf-8") as metadata_file:
            for index, item in enumerate(self.metadata):
                row = dict(item)
                row.setdefault("embedding_index", index)
                metadata_file.write(json.dumps(row, ensure_ascii=False) + "\n")

        manifest = {
            "metric": self.metric,
            "index_file": index_path.name,
            "metadata_file": metadata_path.name,
            "candidate_count": len(self.metadata),
            "dimension": int(self.index.d),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, index_dir: str | Path) -> "FaissCandidateRetriever":
        """Load a persisted FAISS candidate index."""

        index_path = Path(index_dir)
        manifest = json.loads((index_path / "retrieval_manifest.json").read_text(encoding="utf-8"))
        faiss = _import_faiss()
        index = faiss.read_index(str(index_path / manifest["index_file"]))

        metadata: list[dict[str, Any]] = []
        with (index_path / manifest["metadata_file"]).open("r", encoding="utf-8") as metadata_file:
            for line in metadata_file:
                if line.strip():
                    metadata.append(json.loads(line))

        if index.ntotal != len(metadata):
            raise ValueError("Loaded FAISS index size does not match metadata length")

        return cls(metric=manifest["metric"], index=index, metadata=metadata)


def _as_float32_matrix(values: Any) -> Any:
    np = _import_numpy()
    matrix = np.asarray(values, dtype="float32")
    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)
    if matrix.ndim != 2:
        raise ValueError("embeddings must be a 2D matrix or a single 1D vector")
    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise ValueError("embeddings cannot be empty")
    return matrix


def _prepare_vectors(vectors: Any, metric: Metric) -> Any:
    if metric != "cosine":
        return vectors

    faiss = _import_faiss()
    normalized = vectors.copy()
    faiss.normalize_L2(normalized)
    return normalized


def _score_from_distance(distance: float, metric: Metric) -> float:
    if metric == "l2":
        return -distance
    return distance


def _import_faiss() -> Any:
    try:
        import faiss
    except ImportError as exc:
        raise RuntimeError(
            "faiss is required for candidate retrieval. Install faiss-cpu or faiss-gpu first."
        ) from exc
    return faiss


def _import_numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("numpy is required for FAISS retrieval.") from exc
    return np
