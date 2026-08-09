from __future__ import annotations

import json
import logging
import secrets
from pathlib import Path

from tree_sitter_language_pack import get_parser

from app.services.treesitter import _detect_language
from app.storage.state import state

logger = logging.getLogger(__name__)

# we will have to expand this as well , to support multiple languages
PYTHON_IMPORT_TYPES: frozenset[str] = frozenset({
    "import_statement",
    "import_from_statement",
    "future_import_statement",
})

_used_edge_ids: set[str] = set()

def _reset_edge_ids() -> None:
    _used_edge_ids.clear()

def _new_edge_id() -> str:
    while True:
        candidate = secrets.token_hex(3)
        if candidate not in _used_edge_ids:
            _used_edge_ids.add(candidate)
            return f"edge_{candidate}"


def _parse_python_import_node(node) -> list[dict]:
    text = node.text.decode("utf-8", errors="replace").strip()
    start_line = node.start_point[0] + 1
    end_line = node.end_point[0] + 1
    imports: list[dict] = []

    if node.type in ("import_statement", "future_import_statement"):
        for child in node.children:
            if child.type == "dotted_name":
                imports.append({
                    "module": child.text.decode("utf-8", errors="replace"),
                    "imported_symbols": [],
                    "aliases": [],
                    "start_line": start_line,
                    "end_line": end_line,
                    "raw": text,
                })
            elif child.type == "aliased_import":
                name_node = child.child_by_field_name("name")
                alias_node = child.child_by_field_name("alias")
                module_str = name_node.text.decode("utf-8", errors="replace") if name_node else child.text.decode("utf-8", errors="replace")
                alias_str = alias_node.text.decode("utf-8", errors="replace") if alias_node else None
                imports.append({
                    "module": module_str,
                    "imported_symbols": [],
                    "aliases": [alias_str] if alias_str else [],
                    "start_line": start_line,
                    "end_line": end_line,
                    "raw": text,
                })

    elif node.type == "import_from_statement":
        module_name = ""
        symbols: list[str] = []
        aliases: list[str] = []
        in_import = False

        for child in node.children:
            if child.type == "from":
                continue
            if child.type == "import":
                in_import = True
                continue

            if not in_import:
                if child.type in ("dotted_name", "relative_import"):
                    module_name = child.text.decode("utf-8", errors="replace")
            else:
                if child.type == "dotted_name":
                    symbols.append(child.text.decode("utf-8", errors="replace"))
                elif child.type == "aliased_import":
                    name_node = child.child_by_field_name("name")
                    alias_node = child.child_by_field_name("alias")
                    if name_node:
                        symbols.append(name_node.text.decode("utf-8", errors="replace"))
                    if alias_node:
                        aliases.append(alias_node.text.decode("utf-8", errors="replace"))
                elif child.type == "wildcard_import":
                    symbols.append("*")

        imports.append({
            "module": module_name,
            "imported_symbols": symbols,
            "aliases": aliases,
            "start_line": start_line,
            "end_line": end_line,
            "raw": text,
        })

    return imports


def _extract_file_imports(file_path: Path, language: str) -> list[dict]:
    if language != "python":
        return []

    try:
        parser = get_parser(language)
        ts_tree = parser.parse(file_path.read_bytes())
    except Exception:
        return []

    imports: list[dict] = []
    stack = [ts_tree.root_node]

    while stack:
        node = stack.pop()
        if node.type in PYTHON_IMPORT_TYPES:
            imports.extend(_parse_python_import_node(node))
        else:
            stack.extend(reversed(node.children))

    return imports


def _resolve_internal_target(
    module_name: str,
    symbols: list[str],
    source_file_path: Path,
    repo_path: Path,
    path_to_id: dict[str, str],
) -> tuple[bool, str | None, str | None]:
    if not module_name and not symbols:
        return False, None, None

    repo_path = repo_path.resolve()
    candidates: list[Path] = []

    if module_name.startswith("."):
        dots_count = len(module_name) - len(module_name.lstrip("."))
        rel_mod = module_name.lstrip(".")
        rel_path_str = rel_mod.replace(".", "/")
        
        base_dir = source_file_path.parent
        for _ in range(dots_count - 1):
            base_dir = base_dir.parent

        if rel_path_str:
            candidates.append(base_dir / f"{rel_path_str}.py")
            candidates.append(base_dir / rel_path_str / "__init__.py")
        else:
            candidates.append(base_dir / "__init__.py")
    else:
        mod_path_str = module_name.replace(".", "/")
        candidates.append(repo_path / f"{mod_path_str}.py")
        candidates.append(repo_path / mod_path_str / "__init__.py")

        for sym in symbols:
            if sym != "*":
                candidates.append(repo_path / f"{mod_path_str}/{sym}.py")
                candidates.append(repo_path / mod_path_str / sym / "__init__.py")

    for cand in candidates:
        try:
            resolved_cand = cand.resolve()
            cand_str = str(resolved_cand)
            if cand_str in path_to_id:
                return True, cand_str, path_to_id[cand_str]
        except Exception:
            continue

    return False, None, None


def _collect_file_entries(entry: dict, acc: list[dict]) -> None:
    if entry.get("type") == "file":
        acc.append(entry)
        return
    for child in entry.get("children", []):
        _collect_file_entries(child, acc)


def generate_edges() -> Path:
    filestructure_path = (state.repo_dir / "filestructure.json").resolve()
    if not filestructure_path.exists():
        raise RuntimeError(
            "filestructure.json not found. Call POST /tree first."
        )

    if state.repo_path is None:
        raise RuntimeError("No repository cloned. Call POST /repo first.")

    _reset_edge_ids()
    structure: dict = json.loads(filestructure_path.read_text(encoding="utf-8"))

    file_entries: list[dict] = []
    _collect_file_entries(structure, file_entries)

    path_to_id: dict[str, str] = {
        str(Path(f["path"]).resolve()): f["id"]
        for f in file_entries
        if "path" in f and "id" in f
    }

    edges: list[dict] = []

    for file_entry in file_entries:
        file_path = Path(file_entry["path"])
        if not file_path.exists():
            continue

        language = _detect_language(file_path)
        if not language:
            continue

        raw_imports = _extract_file_imports(file_path, language)
        source_file_id = file_entry["id"]
        source_path_str = str(file_path.resolve())

        for imp in raw_imports:
            is_internal, target_path, target_file_id = _resolve_internal_target(
                module_name=imp["module"],
                symbols=imp["imported_symbols"],
                source_file_path=file_path,
                repo_path=state.repo_path,
                path_to_id=path_to_id,
            )

            edge = {
                "id": _new_edge_id(),
                "type": "import",
                "source_file_id": source_file_id,
                "source_path": source_path_str,
                "target_file_id": target_file_id,
                "target_path": target_path,
                "module": imp["module"],
                "imported_symbols": imp["imported_symbols"],
                "aliases": imp["aliases"],
                "is_internal": is_internal,
                "start_line": imp["start_line"],
                "end_line": imp["end_line"],
                "raw": imp["raw"],
            }
            edges.append(edge)

    edges_path = (state.repo_dir / "edges.json").resolve()
    edges_path.parent.mkdir(parents=True, exist_ok=True)
    edges_path.write_text(
        json.dumps({"edges": edges}, indent=2), encoding="utf-8"
    )

    logger.info("edges.json written: %d import edges", len(edges))
    return edges_path
