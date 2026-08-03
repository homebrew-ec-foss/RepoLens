from __future__ import annotations

import json
import logging
from pathlib import Path

from app.storage.state import state

logger = logging.getLogger(__name__)


def _read_snippet(path: str, start_line: int, end_line: int) -> str:
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        return "".join(lines[start_line - 1:end_line])
    except OSError:
        return ""


def _find_node(node_id: str) -> dict | None:
    nodes_path = (state.out_dir / "nodes.json").resolve()
    if not nodes_path.exists():
        return None
    data = json.loads(nodes_path.read_text(encoding="utf-8"))
    for node in data.get("nodes", []):
        if node.get("id") == node_id:
            return node
    return None


def _find_file_entry(node_id: str) -> dict | None:
    structure_path = (state.out_dir / "filestructure.json").resolve()
    if not structure_path.exists():
        return None
    structure = json.loads(structure_path.read_text(encoding="utf-8"))
    stack = [structure]
    while stack:
        entry = stack.pop()
        if entry.get("id") == node_id and entry.get("type") == "file":
            return entry
        stack.extend(entry.get("children", []))
    return None


def get_node_content(node_id: str) -> dict | None:
    node = _find_node(node_id)
    if node is not None:
        return {
            "id": node_id,
            "kind": "node",
            "title": node.get("title"),
            "node_type": node.get("node_type"),
            "language": node.get("language"),
            "path": node.get("path"),
            "start_line": node.get("start_line"),
            "end_line": node.get("end_line"),
            "content": _read_snippet(node["path"], node["start_line"], node["end_line"]),
        }

    file_entry = _find_file_entry(node_id)
    if file_entry is not None:
        path = file_entry.get("path", "")
        content = _read_snippet(path, 1, 10**9)
        return {
            "id": node_id,
            "kind": "file",
            "title": file_entry.get("name"),
            "node_type": "file",
            "language": "",
            "path": path,
            "start_line": 1,
            "end_line": content.count("\n") + 1,
            "content": content,
        }

    return None
