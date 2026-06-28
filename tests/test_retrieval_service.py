from pathlib import Path

import numpy as np

from ai_hiring_intelligence.services.retrieval_service import FaissCandidateRetriever


class FakeEmbeddingService:
    def embed_texts(self, texts, *, batch_size=None, show_progress_bar=True):
        assert texts == ["machine learning engineer"]
        assert batch_size == 1
        assert show_progress_bar is False
        return np.array([[1.0, 0.0]], dtype="float32")


def test_faiss_retriever_returns_top_k_candidates() -> None:
    embeddings = np.array(
        [
            [1.0, 0.0],
            [0.8, 0.2],
            [0.0, 1.0],
        ],
        dtype="float32",
    )
    metadata = [
        {"candidate_id": "CAND_0000001", "current_title": "ML Engineer"},
        {"candidate_id": "CAND_0000002", "current_title": "Data Engineer"},
        {"candidate_id": "CAND_0000003", "current_title": "Designer"},
    ]
    retriever = FaissCandidateRetriever.from_embeddings(embeddings, metadata)

    results = retriever.search(np.array([1.0, 0.0], dtype="float32"), top_k=2)

    assert [result.candidate_id for result in results] == ["CAND_0000001", "CAND_0000002"]
    assert [result.rank for result in results] == [1, 2]
    assert results[0].score > results[1].score
    assert results[0].metadata["current_title"] == "ML Engineer"


def test_faiss_retriever_searches_text_with_embedding_service() -> None:
    retriever = FaissCandidateRetriever.from_embeddings(
        np.array([[1.0, 0.0], [0.0, 1.0]], dtype="float32"),
        [{"candidate_id": "CAND_0000001"}, {"candidate_id": "CAND_0000002"}],
    )

    results = retriever.search_text(
        "machine learning engineer",
        FakeEmbeddingService(),
        top_k=1,
        show_progress_bar=False,
    )

    assert len(results) == 1
    assert results[0].candidate_id == "CAND_0000001"


def test_faiss_retriever_saves_and_loads_index(tmp_path: Path) -> None:
    retriever = FaissCandidateRetriever.from_embeddings(
        np.array([[1.0, 0.0], [0.0, 1.0]], dtype="float32"),
        [{"candidate_id": "CAND_0000001"}, {"candidate_id": "CAND_0000002"}],
    )

    retriever.save(tmp_path)
    loaded = FaissCandidateRetriever.load(tmp_path)
    results = loaded.search(np.array([[0.0, 1.0]], dtype="float32"), top_k=1)

    assert (tmp_path / "candidates.faiss").exists()
    assert (tmp_path / "candidate_metadata.jsonl").exists()
    assert (tmp_path / "retrieval_manifest.json").exists()
    assert results[0].candidate_id == "CAND_0000002"
