from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.treesitter import should_summarize_node
from app.storage.state import state

load_dotenv()

logger = logging.getLogger(__name__)

_MODEL = os.getenv("REPOLENS_SUMMARY_MODEL", "gemini-3.1-flash-lite")
_BATCH_SIZE = int(os.getenv("REPOLENS_BATCH_SIZE", "1000"))
_PARENT_BATCH_SIZE = int(os.getenv("REPOLENS_PARENT_BATCH_SIZE", "5"))

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

_PARENT_PROMPT = """\
You are summarizing a parent node in a software repository.

The following are summaries of the child nodes contained inside this parent.

Based ONLY on these child summaries, write a concise and coherent summary of the parent.

The summary should explain:
- what this parent contains
- its overall purpose/responsibility
- the major functionality represented by its children

Do not simply concatenate or list the child summaries.
Synthesize them into one meaningful summary.

Keep the summary concise and useful to a developer who wants to understand what this parent contains without opening every child.

Child summaries:

{child_summaries}
"""

_PARENT_PROMPT_BATCH = """\
You are summarizing parent nodes in a software repository. Each parent is tagged with a unique id and is followed by the summaries of the child nodes contained inside it.

For each parent, based ONLY on its child summaries, write a concise and coherent summary that explains:
- what this parent contains
- its overall purpose/responsibility
- the major functionality represented by its children

Do not simply concatenate or list the child summaries. Synthesize them into one meaningful summary per parent.

Respond with ONLY a JSON object mapping each parent id to its summary string, and nothing else. Example: {{"id1": "summary", "id2": "summary"}}

Parents:
{parents}
"""

_PARENT_BLOCK = """\
--- id:{id} name:{name} ---
{child_summaries}
"""


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

    client = _get_client()
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            logger.info(response.text)
            data = json.loads(response.text)
            return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}
        except Exception as e:
            if attempt < 4 and ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower()):
                sleep_time = 15 * (attempt + 1)
                logger.warning(f"Rate limit hit in summary. Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                if attempt == 4 or isinstance(e, (json.JSONDecodeError, TypeError)):
                    logger.warning("Failed to parse LLM response for node batch")
                    return {}
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


def _summarize_parent_batch(parents: list[dict]) -> dict[str, str]:
    if not parents:
        return {}

    blocks = "\n".join(
        _PARENT_BLOCK.format(
            id=p["id"],
            name=p.get("name") or "unknown",
            child_summaries=p.get("child_summaries") or "(no child summaries)",
        )
        for p in parents
    )
    prompt = _PARENT_PROMPT_BATCH.format(parents=blocks)

    client = _get_client()
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            data = json.loads(response.text)
            return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}
        except Exception as e:
            if attempt < 4 and ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower()):
                sleep_time = 15 * (attempt + 1)
                logger.warning(f"Rate limit hit in parent summary. Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                if attempt == 4 or isinstance(e, (json.JSONDecodeError, TypeError)):
                    logger.warning("Failed to parse LLM response for parent batch")
                    return {}
    return {}


def generate_parent_summary(child_summaries: list[str]) -> str:
    if not child_summaries:
        return ""
    text = "\n".join(s.strip() for s in child_summaries if s and s.strip())
    if not text:
        return ""
    result = _summarize_parent_batch([
        {"id": "_parent", "name": "", "child_summaries": text},
    ])
    return result.get("_parent", "")


def _stage1_summarize_nodes(nodes: list[dict]):
    pending = [n for n in nodes if not n.get("summary") and should_summarize_node(n)]
    
    for n in nodes:
        if not n.get("summary") and not should_summarize_node(n):
            n["summary"] = None

    if not pending:
        logger.info("Stage 1: all summarizable nodes already summarized, skipping")
        return

    logger.info("Stage 1: summarizing %d semantic nodes in batches of %d", len(pending), _BATCH_SIZE)

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
    file_entries: list[dict] = []

    def walk(entry: dict) -> None:
        if entry.get("type") == "file":
            file_entries.append(entry)
            return
        for child in entry.get("children", []):
            walk(child)

    walk(structure)
    if not file_entries:
        return

    logger.info(
        "Stage 2: synthesizing %d file summaries from node summaries (batch=%d)",
        len(file_entries), _PARENT_BATCH_SIZE,
    )

    for start in range(0, len(file_entries), _PARENT_BATCH_SIZE):
        batch = file_entries[start:start + _PARENT_BATCH_SIZE]
        batch_by_id = {entry["id"]: entry for entry in batch}
        requests: list[dict] = []
        for entry in batch:
            node_ids = entry.get("node_ids", [])
            summaries = [
                node_index[nid]["summary"]
                for nid in node_ids
                if nid in node_index and node_index[nid].get("summary")
            ]
            labels = [
                node_index[nid].get("title") or nid
                for nid in node_ids
                if nid in node_index and node_index[nid].get("summary")
            ]
            child_text = _concat_summaries(summaries, labels)
            if child_text:
                requests.append({
                    "id": entry["id"],
                    "name": entry.get("name"),
                    "child_summaries": child_text,
                })

        results = _summarize_parent_batch(requests) if requests else {}
        for req in requests:
            entry = batch_by_id.get(req["id"])
            summary = results.get(req["id"])
            if entry and summary:
                entry["summary"] = summary

            for snode in entry.get("nodes", []):
                nid = snode.get("id")
                if nid in node_index:
                    snode["summary"] = node_index[nid].get("summary") or ""


def _stage3_folder_summaries(structure: dict) -> None:
    entries_by_depth: list[tuple[int, dict]] = []

    def walk(entry: dict, depth: int) -> None:
        if entry.get("type") != "file":
            entries_by_depth.append((depth, entry))
        for child in entry.get("children", []):
            walk(child, depth + 1)

    walk(structure, 0)
    entries_by_depth.sort(key=lambda t: t[0], reverse=True)
    parents = [entry for _, entry in entries_by_depth]

    logger.info(
        "Stage 3: synthesizing %d folder/repository summaries (batch=%d)",
        len(parents), _PARENT_BATCH_SIZE,
    )

    for start in range(0, len(parents), _PARENT_BATCH_SIZE):
        batch = parents[start:start + _PARENT_BATCH_SIZE]
        batch_by_id = {entry["id"]: entry for entry in batch}
        requests: list[dict] = []
        for entry in batch:
            child_summaries: list[str] = []
            child_labels: list[str] = []
            for child in entry.get("children", []):
                child_summary = child.get("summary", "")
                if child_summary and child_summary.strip():
                    child_summaries.append(child_summary)
                    child_labels.append(child.get("name", ""))
            child_text = _concat_summaries(child_summaries, child_labels)
            if child_text:
                requests.append({
                    "id": entry["id"],
                    "name": entry.get("name"),
                    "child_summaries": child_text,
                })

        results = _summarize_parent_batch(requests) if requests else {}
        for req in requests:
            entry = batch_by_id.get(req["id"])
            summary = results.get(req["id"])
            if entry and summary:
                entry["summary"] = summary


def run_summary_pipeline() -> dict:
    nodes_path = (state.repo_dir / "nodes.json").resolve()
    structure_path = (state.repo_dir / "filestructure.json").resolve()

    if not nodes_path.exists():
        raise RuntimeError("nodes.json not found. Call POST /nodes first.")
    if not structure_path.exists():
        raise RuntimeError("filestructure.json not found. Call POST /tree first.")

    nodes: list[dict] = json.loads(nodes_path.read_text(encoding="utf-8"))["nodes"]
    structure: dict = json.loads(structure_path.read_text(encoding="utf-8"))

    def _set_progress(done: int, total: int) -> None:
        state.pipeline_progress = {"phase": "summary", "done": done, "total": max(total, 1)}

    pending_nodes = [n for n in nodes if not n.get("summary") and should_summarize_node(n)]

    logger.info("Summary Stage 1: LLM node summaries")
    _set_progress(0, len(pending_nodes))
    _stage1_summarize_nodes(nodes)
    _set_progress(sum(1 for n in nodes if n.get("summary")), len(nodes))
    nodes_path.write_text(json.dumps({"nodes": nodes}, indent=2), encoding="utf-8")

    logger.info("Summary Stage 2: LLM file summaries (batched)")
    node_index = {n["id"]: n for n in nodes}
    _stage2_file_summaries(structure, node_index)

    logger.info("Summary Stage 3: LLM folder/repository summaries (batched)")
    _stage3_folder_summaries(structure)

    structure_path.write_text(json.dumps(structure, indent=2), encoding="utf-8")

    summarized_nodes = sum(1 for n in nodes if n.get("summary"))
    state.pipeline_progress = {"phase": "summary", "done": len(nodes), "total": len(nodes)}
    logger.info(
        "Summary pipeline complete: %d/%d nodes summarized, root summary length %d",
        summarized_nodes, len(nodes), len(structure.get("summary", "")),
    )

    return {
        "total_nodes": len(nodes),
        "summarized_nodes": summarized_nodes,
        "root_summary_length": len(structure.get("summary", "")),
    }
