from __future__ import annotations

import json
import logging
from pathlib import Path

from app.storage.state import state

logger = logging.getLogger(__name__)

def _collect_raw_nodes(tree_entry: dict, file_entry_id: str, acc: list[dict]) -> None:
    if tree_entry.get("type") == "file":
        for node in tree_entry.get("nodes", []):
            node["parent_id"] = file_entry_id  # file's tree-entry id
            acc.append(node)
        return

    for child in tree_entry.get("children", []):
        _collect_raw_nodes(child, child.get("id", ""), acc)


def _compute_children_ids(nodes: list[dict]) -> None:

    by_file: dict[str, list[dict]] = {}
    for node in nodes:
        by_file.setdefault(node["path"], []).append(node)

    for file_nodes in by_file.values():
        sorted_nodes = sorted(file_nodes, key=lambda n: (n["start_line"], -n["end_line"]))
        id_to_node = {n["id"]: n for n in sorted_nodes}

        for node in sorted_nodes:
            node["children_ids"] = []

        for i, node in enumerate(sorted_nodes):
            for j in range(i + 1, len(sorted_nodes)):
                candidate = sorted_nodes[j]
                if candidate["start_line"] >= node["start_line"] and \
                   candidate["end_line"] <= node["end_line"]:
                    # all this to make sure 
                    # that we are not overlapping the 
                    # node code content
                    already_claimed = any(
                        cid != node["id"] and
                        id_to_node[cid]["start_line"] <= candidate["start_line"] and
                        id_to_node[cid]["end_line"] >= candidate["end_line"]
                        for cid in node["children_ids"]
                        if cid in id_to_node
                    )
                    if not already_claimed:
                        node["children_ids"].append(candidate["id"])

def generate_nodes() -> Path:
    filestructure_path = (state.repo_dir / "filestructure.json").resolve()
    if not filestructure_path.exists():
        raise RuntimeError(
            "filestructure.json not found. Call POST /tree first."
        )
    # ".raw_nodes.json" is just json with every file
    # code content and no children mapping
    raw_nodes: list[dict] = []
    if state.raw_nodes:
        raw_nodes = json.loads(json.dumps(state.raw_nodes))
    else:
        raw_nodes_cache = (state.repo_dir / ".raw_nodes.json").resolve()
        if raw_nodes_cache.exists():
            raw_nodes = json.loads(raw_nodes_cache.read_text(encoding="utf-8"))
        else:
            logger.info("Reading %s", filestructure_path)
            structure: dict = json.loads(filestructure_path.read_text(encoding="utf-8"))
            _collect_raw_nodes(structure, structure.get("id", ""), raw_nodes)

    for node in raw_nodes:
        node.setdefault("children_ids", [])
        node.setdefault("summary", "")

    _compute_children_ids(raw_nodes)

    nodes_path = (state.repo_dir / "nodes.json").resolve()
    nodes_path.parent.mkdir(parents=True, exist_ok=True)
    nodes_path.write_text(
        json.dumps({"nodes": raw_nodes}, indent=2), encoding="utf-8"
    )

    logger.info("nodes.json written: %d nodes", len(raw_nodes))
    return nodes_path
