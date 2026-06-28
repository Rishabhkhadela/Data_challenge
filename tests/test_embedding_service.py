import json

from ai_hiring_intelligence.services.embedding_service import EmbeddingService


class FakeEmbeddingModel:
    def __init__(self) -> None:
        self.calls = []

    def encode(
        self,
        sentences,
        *,
        batch_size,
        convert_to_numpy,
        normalize_embeddings,
        show_progress_bar,
    ):
        self.calls.append(
            {
                "sentences": sentences,
                "batch_size": batch_size,
                "convert_to_numpy": convert_to_numpy,
                "normalize_embeddings": normalize_embeddings,
                "show_progress_bar": show_progress_bar,
            }
        )
        return [[float(index), float(len(sentence))] for index, sentence in enumerate(sentences)]


def test_embedding_service_batches_and_normalizes_documents() -> None:
    model = FakeEmbeddingModel()
    service = EmbeddingService(model=model, device="cpu", batch_size=8)

    result = service.embed_documents(
        [
            {
                "candidate_id": "CAND_0000001",
                "text": "Candidate profile one",
                "metadata": {"current_title": "ML Engineer"},
            },
            {"candidate_id": "CAND_0000002", "text": "Candidate profile two"},
        ],
        batch_size=2,
        show_progress_bar=False,
    )

    assert model.calls == [
        {
            "sentences": ["Candidate profile one", "Candidate profile two"],
            "batch_size": 2,
            "convert_to_numpy": True,
            "normalize_embeddings": True,
            "show_progress_bar": False,
        }
    ]
    assert result.embeddings == [[0.0, 21.0], [1.0, 21.0]]
    assert result.metadata == [
        {"current_title": "ML Engineer", "candidate_id": "CAND_0000001"},
        {"candidate_id": "CAND_0000002"},
    ]


def test_embedding_service_saves_embeddings_metadata_and_manifest(tmp_path) -> None:
    model = FakeEmbeddingModel()
    service = EmbeddingService(model=model, device="cpu", batch_size=4)
    result = service.embed_documents(
        [{"candidate_id": "CAND_0000001", "text": "semantic text"}],
        show_progress_bar=False,
    )

    service.save_embeddings(result, tmp_path, include_text=True)

    assert (tmp_path / "embeddings.npy").exists()
    metadata_lines = (tmp_path / "metadata.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(metadata_lines[0]) == {
        "candidate_id": "CAND_0000001",
        "embedding_index": 0,
        "text": "semantic text",
    }

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["model_name"] == "BAAI/bge-large-en-v1.5"
    assert manifest["device"] == "cpu"
    assert manifest["embedding_count"] == 1
    assert manifest["embedding_dimension"] == 2
