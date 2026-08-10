from __future__ import annotations

import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from app.api.init import init_embedder
from google.genai import Client,types
from dotenv import load_dotenv
from app.storage.state import state

EMBED_MODEL_NAME = "Alibaba-NLP/gte-modernbert-base"
EMBED_DIM = 768
_CACHE_DIR = "./_models"

_model: SentenceTransformer | None = None

client = Client(state.gemini_api_key)
def embed_using_gemini(text):
    response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=text,
    config=types.EmbedContentConfig(output_dimensionality=768),
    )
    return response.embeddings[0].values

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
       _model = init_embedder()
       if not _model:
           
        _model = SentenceTransformer(
            EMBED_MODEL_NAME,
            cache_folder=_CACHE_DIR,
            local_files_only=True,
            device="cpu",
            trust_remote_code=True,
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
    user_choice = state.user_choice
    if user_choice  == "local":
        vector = _get_model().encode(query, prompt_name="query")
        return vector.tolist()
    return embed_using_gemini(query)