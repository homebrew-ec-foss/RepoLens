from __future__ import annotations

import json
import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.prompts import build_rag_prompt
from app.services import vectorstore

load_dotenv()

logger = logging.getLogger(__name__)

_RAG_MODEL = os.getenv("REPOLENS_RAG_MODEL", "gemini-3.1-flash-lite")
_TOP_K = int(os.getenv("REPOLENS_RAG_TOP_K", "8"))

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


def _format_citation(node: dict, score: float | None = None) -> dict:
    return {
        "id": node.get("id"),
        "kind": node.get("kind"),
        "title": node.get("title"),
        "node_type": node.get("node_type"),
        "language": node.get("language"),
        "path": node.get("path"),
        "start_line": node.get("start_line"),
        "end_line": node.get("end_line"),
        "chain": node.get("chain") or [],
        "summary": node.get("summary"),
        "score": score,
    }


def answer_query(query: str, top_k: int | None = None) -> dict:
    top_k = top_k or _TOP_K
    retrieved = vectorstore.search_nodes(query, top_k=top_k)

    prompt = build_rag_prompt(query, retrieved)

    response = _get_client().models.generate_content(
        model=_RAG_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    text = getattr(response, "text", "") or ""

    answer_text = text
    citation_ids: list[str] = []
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            answer_text = str(data.get("answer") or data.get("response") or text)
            citation_ids = [str(i) for i in (data.get("citations") or []) if i]
    except (json.JSONDecodeError, TypeError):
        logger.warning("RAG response was not valid JSON; returning raw text")

    id_to_node = {node.get("id"): node for node in retrieved}
    citations = [
        _format_citation(id_to_node[cid])
        for cid in citation_ids
        if cid in id_to_node
    ]
    if not citations and retrieved:
        citations = [_format_citation(node) for node in retrieved[:3]]

    return {
        "query": query,
        "mode": "semantic",
        "answer": answer_text,
        "citations": citations,
        "retrieved": [_format_citation(node) for node in retrieved],
    }
