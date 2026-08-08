from __future__ import annotations

import json
import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.prompts import build_rag_prompt, build_deep_rag_prompt
from app.services import vectorstore
from app.services import content as content_svc

load_dotenv()

logger = logging.getLogger(__name__)

_RAG_MODEL = os.getenv("REPOLENS_RAG_MODEL", "gemini-3.1-flash-lite")
_TOP_K = int(os.getenv("REPOLENS_RAG_TOP_K", "8"))

SUMMARY_NODE_COUNT = int(os.getenv("REPOLENS_SUMMARY_NODE_COUNT", "8"))
CODE_NODE_COUNT = int(os.getenv("REPOLENS_CODE_NODE_COUNT", "5"))

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


def _build_deep_code_context(nodes: list[dict], limit: int) -> list[dict]:
    code_nodes: list[dict] = []
    for node in nodes[:limit]:
        node_id = node.get("id")
        if not node_id:
            continue
        try:
            data = content_svc.get_node_code(node_id)
        except (LookupError, ValueError, FileNotFoundError):
            continue
        code = (data.get("code") or "").strip()
        if not code:
            continue
        code_nodes.append({
            "id": node_id,
            "kind": data.get("node_type") or node.get("kind"),
            "title": data.get("title") or node.get("title"),
            "node_type": data.get("node_type"),
            "language": data.get("language") or node.get("language"),
            "path": data.get("path") or node.get("path"),
            "start_line": data.get("start_line") or node.get("start_line"),
            "end_line": data.get("end_line") or node.get("end_line"),
            "summary": data.get("summary") or node.get("summary"),
            "code": code,
        })
    return code_nodes


def answer_query(query: str, top_k: int | None = None, deep: bool = False) -> dict:
    top_k = top_k or SUMMARY_NODE_COUNT
    retrieved = vectorstore.search_nodes(query, top_k=top_k)

    if deep:
        code_nodes = _build_deep_code_context(retrieved, CODE_NODE_COUNT)
        prompt = build_deep_rag_prompt(query, retrieved, code_nodes)
    else:
        code_nodes = []
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
        "mode": "deep" if deep else "semantic",
        "answer": answer_text,
        "citations": citations,
        "retrieved": [_format_citation(node) for node in retrieved],
    }
