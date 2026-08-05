from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logger = logging.getLogger(__name__)

_EMBED_MODEL = os.getenv("REPOLENS_EMBED_MODEL", "gemini-embedding-001")
EMBED_MODEL_NAME = _EMBED_MODEL
_EMBED_DIM = 768
_BATCH_SIZE = 64

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


import time

def _embed(contents: list[str], task_type: str) -> list[list[float]]:
    if not contents:
        return []
    client = _get_client()
    for attempt in range(5):
        try:
            response = client.models.embed_content(
                model=_EMBED_MODEL,
                contents=contents,
                config=types.EmbedContentConfig(
                    output_dimensionality=_EMBED_DIM,
                    task_type=task_type,
                ),
            )
            return [
                embedding.values
                for embedding in (response.embeddings or [])
                if embedding.values is not None
            ]
        except Exception as e:
            if attempt < 4 and ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower()):
                sleep_time = 15 * (attempt + 1)
                logger.warning(f"Rate limit hit in embed. Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                raise
    return []


def embed_texts(texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for start in range(0, len(texts), _BATCH_SIZE):
        batch = texts[start:start + _BATCH_SIZE]
        vectors.extend(_embed(batch, "RETRIEVAL_DOCUMENT"))
    return vectors


def embed_query(query: str) -> list[float]:
    vectors = _embed([query], "RETRIEVAL_QUERY")
    return vectors[0] if vectors else []
