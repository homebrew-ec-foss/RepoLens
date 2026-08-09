from __future__ import annotations

import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
from tqdm import tqdm

EMBED_MODEL_NAME = "Alibaba-NLP/gte-modernbert-base"
EMBED_DIM = 768
_CACHE_DIR = "./models"

_model: SentenceTransformer | None = None


def _resolve_device() -> str:
    return "cpu"


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(
            EMBED_MODEL_NAME,
            cache_folder=_CACHE_DIR,
            local_files_only=True,
            device=_resolve_device(),
        )
    return _model


def embed_texts(texts: list[str], on_progress=None) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    vectors: list[list[float]] = []
    for i, text in enumerate(tqdm(texts, desc="Embedding documents", unit="doc")):
        vectors.append(model.encode(text).tolist())
        if on_progress is not None:
            on_progress(i + 1, len(texts))
    return vectors


def embed_query(query: str) -> list[float]:
    vector = _get_model().encode(query, prompt_name="query")
    return vector.tolist()
