from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.storage.state import state

load_dotenv()

logger = logging.getLogger(__name__)

_MODEL = os.getenv("REPOLENS_SUMMARY_MODEL", "gemini-3.5-flash")
_BATCH_SIZE = int(os.getenv("REPOLENS_BATCH_SIZE", "10"))

_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client()
    return _client

_NODE_PROMPT = """\
You are an expert code reviewer. You will be given {count} code snippets, \
each tagged with a unique id. For every snippet, write a detailed but concise \
summary (1–3 sentences) that explains what it does, its purpose, and any \
notable behaviour or edge cases.

Respond with ONLY a JSON object mapping each snippet id to its summary string, \
and nothing else. Example: {{"id1": "summary", "id2": "summary"}}

Snippets:
{snippets}
"""

_SNIPPET_BLOCK = "--- id:{id} name:{name} type:{type} ---\n{code}\n"


def _read_snippet(path: str, start_line: int, end_line: int) -> str:
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        return "".join(lines[start_line - 1:end_line])
    except OSError:
        return ""


def _summarize_node_batch(batch: list[dict]) -> dict[str, str]:
    snippets = "\n".join(
        _SNIPPET_BLOCK.format(
            id=node["id"],
            name=node.get("title") or "unknown",
            type=node.get("node_type") or "unknown",
            code=_read_snippet(node["path"], node["start_line"], node["end_line"]),
        )
        for node in batch
    )
    prompt = _NODE_PROMPT.format(count=len(batch), snippets=snippets)

    response = _get_client().models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    try:
        data = json.loads(response.text)
        return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}
    except (json.JSONDecodeError, TypeError):
        logger.warning("Failed to parse LLM response for node batch")
        return {}

def _concat_summaries(summaries: list[str], labels: list[str] | None = None) -> str:
    if not summaries:
        return ""

    if labels and len(labels) == len(summaries):
        parts = [
            f"{label}: {summary.strip()}"
            for label, summary in zip(labels, summaries)
            if summary and summary.strip()
        ]
        return "\n".join(parts)

    cleaned = [s.strip() for s in summaries if s and s.strip()]
    return "\n".join(cleaned)

def _stage1_summarize_nodes(nodes: list[dict]) -> None:
    pending = [n for n in nodes if not n.get("summary")]

    if not pending:
        logger.info("Stage 1: all nodes already summarized, skipping")
        return

    logger.info("Stage 1: summarizing %d code nodes in batches of %d", len(pending), _BATCH_SIZE)

    all_summaries: dict[str, str] = {}
    for start in range(0, len(pending), _BATCH_SIZE):
        batch = pending[start: start + _BATCH_SIZE]
        all_summaries.update(_summarize_node_batch(batch))
        logger.debug("  batch %d–%d done", start, start + len(batch) - 1)

    for node in nodes:
        if node["id"] in all_summaries:
            node["summary"] = all_summaries[node["id"]]

    logger.info("Stage 1 complete: %d node summaries populated", len(all_summaries))


def _stage2_file_summaries(structure: dict, node_index: dict[str, dict]) -> None:
    if structure.get("type") == "file":
        node_ids: list[str] = structure.get("node_ids", [])
        summaries = [node_index[nid]["summary"] for nid in node_ids if nid in node_index and node_index[nid].get("summary")]
        labels = [node_index[nid].get("title") or nid for nid in node_ids if nid in node_index and node_index[nid].get("summary")]
        structure["summary"] = _concat_summaries(summaries, labels)
        return

    for child in structure.get("children", []):
        _stage2_file_summaries(child, node_index)


def _stage3_folder_summaries(entry: dict) -> str:
    if entry.get("type") == "file":
        return entry.get("summary", "")

    child_summaries = []
    child_labels = []
    for child in entry.get("children", []):
        child_summary = _stage3_folder_summaries(child)
        if child_summary and child_summary.strip():
            child_summaries.append(child_summary)
            child_labels.append(child["name"])

    entry["summary"] = _concat_summaries(child_summaries, child_labels)
    return entry["summary"]

def run_summary_pipeline() -> dict:
    nodes_path = (state.out_dir / "nodes.json").resolve()
    structure_path = (state.out_dir / "filestructure.json").resolve()

    if not nodes_path.exists():
        raise RuntimeError("nodes.json not found. Call POST /nodes first.")
    if not structure_path.exists():
        raise RuntimeError("filestructure.json not found. Call POST /tree first.")

    nodes: list[dict] = json.loads(nodes_path.read_text(encoding="utf-8"))["nodes"]
    structure: dict = json.loads(structure_path.read_text(encoding="utf-8"))

    logger.info("Summary Stage 1: LLM node summaries")
    _stage1_summarize_nodes(nodes)
    nodes_path.write_text(json.dumps({"nodes": nodes}, indent=2), encoding="utf-8")

    logger.info("Summary Stage 2: Concatenating file summaries (no LLM)")
    node_index = {n["id"]: n for n in nodes}
    _stage2_file_summaries(structure, node_index)

    logger.info("Summary Stage 3: Concatenating folder/repository summaries (no LLM)")
    _stage3_folder_summaries(structure)

    structure_path.write_text(json.dumps(structure, indent=2), encoding="utf-8")

    summarized_nodes = sum(1 for n in nodes if n.get("summary"))
    logger.info(
        "Summary pipeline complete: %d/%d nodes summarized, root summary length %d",
        summarized_nodes, len(nodes), len(structure.get("summary", "")),
    )

    return {
        "total_nodes": len(nodes),
        "summarized_nodes": summarized_nodes,
        "root_summary_length": len(structure.get("summary", "")),
    }
