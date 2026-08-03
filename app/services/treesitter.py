from __future__ import annotations

import json
import logging
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from magika import Magika
from tree_sitter_language_pack import SupportedLanguage, get_parser

from app.storage.state import state

logger = logging.getLogger(__name__)

IGNORED_DIR_NAMES: frozenset[str] = frozenset({
    ".git", ".hg", ".svn",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".venv", "venv", "env",
    "node_modules", "dist", "build", "out",
    ".idea", ".vscode",
})

# Magika content-type labels -> tree-sitter language names.
# None means the file is code-ish but has no available grammar..so skip.
MAGIKA_TO_TS: dict[str, Optional[str]] = {
    "cs": "csharp",
    "shell": "bash",
    "makefile": "make",
    "objectivec": "objc",
    "lisp": "commonlisp",
    "coffeescript": None,
    "javabytecode": None,
    "pythonbytecode": None,
    "asm": None,              
    "csv": None,
    "tsv": None,
    "ini": None,               
    "diff": None,
    "rst": None,               # tree-sitter-rst exists but low adoption; verify
    "tex": None,               # tree-sitter-latex exists; verify naming if you need it
    "svg": None,               # just XML under the hood — could map to "xml" instead of None if you want structure
    "powershell": None,        # tree-sitter-powershell exists but less mature; verify
    "groovy": None,            # tree-sitter-groovy exists but less standardized; verify
    "fsharp": None,
    "matlab": None,
    "r": None,                 # tree-sitter-r exists; verify maturity before enabling
    "cmake": None,             # tree-sitter-cmake exists but niche
    "protobuf": None,          # tree-sitter-proto exists; verify
    "graphql": None,     
    "vbnet": "vb",
    "batch": "bat",
    "jsx": "tsx",
}

PYTHON_IMPORT_TYPES: frozenset[str] = frozenset({
    "import_statement",
    "import_from_statement",
    "future_import_statement",
})

# this needs revision
DEFAULT_NODE_TYPES: frozenset[str] = frozenset({
    "function_definition",
    "function_declaration",
    "class_definition",
    "class_declaration",
    "method_definition",
    "method_declaration",
})

# THIS NEEDS REVISION!!!!!!!!
LANGUAGE_NODE_TYPES: dict[str, frozenset[str]] = {
    "python": frozenset({
        "function_definition", "class_definition", "decorated_definition",
        "import_statement", "import_from_statement",
        "assignment", "decorator"
    }),
    "javascript": frozenset({
        "function_declaration", "class_declaration", "method_definition",
        "generator_function_declaration",
        "import_statement", "export_statement",
        "variable_declaration", "lexical_declaration"
    }),
    "typescript": frozenset({
        "function_declaration", "class_declaration", "method_definition",
        "interface_declaration", "type_alias_declaration", "enum_declaration",
        "generator_function_declaration", "module",
        "import_statement", "export_statement",
        "variable_declaration", "lexical_declaration", "decorator"
    }),
    "tsx": frozenset({
        "function_declaration", "class_declaration", "method_definition",
        "interface_declaration", "type_alias_declaration", "enum_declaration",
        "generator_function_declaration", "module",
        "import_statement", "export_statement",
        "variable_declaration", "lexical_declaration", "decorator"
    }),
    "java": frozenset({
        "class_declaration", "interface_declaration", "method_declaration",
        "constructor_declaration", "enum_declaration", "record_declaration",
        "annotation_type_declaration",
        "import_declaration", "package_declaration",
        "field_declaration", "annotation"
    }),
    "csharp": frozenset({
        "class_declaration", "interface_declaration", "method_declaration",
        "constructor_declaration", "struct_declaration", "enum_declaration",
        "record_declaration", "delegate_declaration",
        "using_directive", "namespace_declaration",
        "property_declaration", "field_declaration", "attribute"
    }),
    "go": frozenset({
        "function_declaration", "method_declaration", "type_declaration",
        "const_declaration",
        "import_declaration", "package_clause",
        "var_declaration"
    }),
    "rust": frozenset({
        "function_item", "struct_item", "impl_item", "trait_item",
        "enum_item", "mod_item", "union_item", "type_item",
        "macro_definition",
        "use_declaration", "extern_crate_declaration",
        "const_item", "static_item", "attribute_item"
    }),
    "c": frozenset({
        "function_definition", "struct_specifier", "enum_specifier",
        "union_specifier", "type_definition",
        "preproc_include", "preproc_def"
    }),
    "cpp": frozenset({
        "function_definition", "class_specifier", "struct_specifier",
        "enum_specifier", "union_specifier", "namespace_definition",
        "template_declaration", "type_definition",
        "preproc_include", "using_declaration", "preproc_def"
    }),
    "ruby": frozenset({
        "method", "class", "module", "singleton_method",
        "call"
    }),
    "php": frozenset({
        "function_definition", "class_declaration", "method_declaration",
        "interface_declaration", "trait_declaration", "enum_declaration",
        "namespace_definition",
        "namespace_use_declaration", "include_expression", "require_expression",
        "property_declaration"
    }),
    "kotlin": frozenset({
        "function_declaration", "class_declaration", "object_declaration",
        "property_declaration",
        "import_header", "package_header",
        "annotation"
    }),
    "swift": frozenset({
        "function_declaration", "class_declaration", "protocol_declaration",
        "struct_declaration", "enum_declaration", "extension_declaration",
        "typealias_declaration", "init_declaration",
        "import_declaration",
        "property_declaration", "attribute"
    }),
    "scala": frozenset({
        "function_definition", "class_definition", "object_definition",
        "trait_definition",
        "import_declaration", "package_clause",
        "val_definition", "var_definition", "annotation"
    }),

    # --- Markup / config / infra languages ---
    "html": frozenset({
        "element", "script_element", "style_element", "doctype"
    }),
    "css": frozenset({
        "rule_set", "media_statement", "keyframes_statement",
        "import_statement", "at_rule"
    }),
    "json": frozenset({
        "pair", "object", "array"
    }),
    "yaml": frozenset({
        "block_mapping_pair", "block_sequence_item", "document"
    }),
    "toml": frozenset({
        "table", "table_array_element", "pair"
    }),
    "dockerfile": frozenset({
        "from_instruction", "run_instruction", "cmd_instruction",
        "entrypoint_instruction", "copy_instruction", "add_instruction",
        "env_instruction", "expose_instruction", "volume_instruction",
        "workdir_instruction", "arg_instruction", "user_instruction",
        "label_instruction"
    }),
    "bash": frozenset({
        "function_definition", "command", "variable_assignment",
        "declaration_command"
    }),
    "sql": frozenset({
        "create_table", "create_view", "create_function_statement",
        "create_index_statement", "alter_table", "select_statement",
        "insert_statement", "update_statement", "delete_statement"
    }),
    "markdown": frozenset({
        "atx_heading", "setext_heading", "fenced_code_block",
        "link_reference_definition"
    }),
}


# SUMMARIZABLE_NODE_TYPES: Only semantic constructs that define behavior, structure, API boundaries, or program architecture. 
# low-level syntax (imports, variables,literals, statements, expressions, punctuation) are excluded.
# only these node types will be sent to the LLM for summary generation.
# cuz earlier, we had to generate summ for every node, now its only
# for func and class nodes (wrt py)
SUMMARIZABLE_NODE_TYPES: dict[str, frozenset[str]] = {
    "python": frozenset({
        "function_definition", "class_definition", "decorated_definition",
    }),
    "javascript": frozenset({
        "function_declaration", "class_declaration", "method_definition",
        "generator_function_declaration",
    }),
    "typescript": frozenset({
        "function_declaration", "class_declaration", "method_definition",
        "interface_declaration", "type_alias_declaration", "enum_declaration",
        "generator_function_declaration", "module", "decorator",
    }),
    "tsx": frozenset({
        "function_declaration", "class_declaration", "method_definition",
        "interface_declaration", "type_alias_declaration", "enum_declaration",
        "generator_function_declaration", "module", "decorator",
    }),
    "java": frozenset({
        "class_declaration", "interface_declaration", "method_declaration",
        "constructor_declaration", "enum_declaration", "record_declaration",
        "annotation_type_declaration", "annotation",
    }),
    "csharp": frozenset({
        "class_declaration", "interface_declaration", "method_declaration",
        "constructor_declaration", "struct_declaration", "enum_declaration",
        "record_declaration", "delegate_declaration",
        "namespace_declaration", "property_declaration", "attribute",
    }),
    "go": frozenset({
        "function_declaration", "method_declaration", "type_declaration",
    }),
    "rust": frozenset({
        "function_item", "struct_item", "impl_item", "trait_item",
        "enum_item", "mod_item", "union_item", "type_item",
        "macro_definition", "attribute_item",
    }),
    "c": frozenset({
        "function_definition", "struct_specifier", "enum_specifier",
        "union_specifier", "type_definition",
    }),
    "cpp": frozenset({
        "function_definition", "class_specifier", "struct_specifier",
        "enum_specifier", "union_specifier", "namespace_definition",
        "template_declaration", "type_definition",
    }),
    "ruby": frozenset({
        "method", "class", "module", "singleton_method",
    }),
    "php": frozenset({
        "function_definition", "class_declaration", "method_declaration",
        "interface_declaration", "trait_declaration", "enum_declaration",
        "namespace_definition", "property_declaration",
    }),
    "kotlin": frozenset({
        "function_declaration", "class_declaration", "object_declaration",
        "property_declaration", "annotation",
    }),
    "swift": frozenset({
        "function_declaration", "class_declaration", "protocol_declaration",
        "struct_declaration", "enum_declaration", "extension_declaration",
        "typealias_declaration", "init_declaration",
        "property_declaration", "attribute",
    }),
    "scala": frozenset({
        "function_definition", "class_definition", "object_definition",
        "trait_definition", "annotation",
    }),

    # --- Markup / config / infra languages ---
    # For markup/config languages, structural elements are the semantic constructs
    "html": frozenset({
        "element", "script_element", "style_element", "doctype",
    }),
    "css": frozenset({
        "rule_set", "media_statement", "keyframes_statement",
        "at_rule",
    }),
    "json": frozenset({
        "object", "array",
    }),
    "yaml": frozenset({
        "document", "block_mapping_pair",
    }),
    "toml": frozenset({
        "table", "table_array_element",
    }),
    "dockerfile": frozenset({
        "from_instruction", "run_instruction", "cmd_instruction",
        "entrypoint_instruction", "copy_instruction", "add_instruction",
        "env_instruction", "expose_instruction", "volume_instruction",
        "workdir_instruction", "arg_instruction", "user_instruction",
        "label_instruction",
    }),
    "bash": frozenset({
        "function_definition",
    }),
    "sql": frozenset({
        "create_table", "create_view", "create_function_statement",
        "create_index_statement", "alter_table",
    }),
    "markdown": frozenset({
        "atx_heading", "setext_heading", "fenced_code_block",
    }),
}


# Default summarizable types for languages not explicitly configured
DEFAULT_SUMMARIZABLE_TYPES: frozenset[str] = frozenset({
    "function_definition", "function_declaration", "function_item",
    "class_definition", "class_declaration", "class_specifier", "class", "class_item",
    "interface_declaration", "protocol_declaration", "trait_declaration",
    "struct_declaration", "struct_specifier", "struct_item",
    "enum_declaration", "enum_specifier", "enum_item",
    "method_definition", "method_declaration", "method_item",
    "constructor_declaration", "init_declaration",
    "function_definition", "function_item",
    "module", "mod_item", "namespace_definition", "namespace_declaration",
    "type_declaration", "type_definition", "type_item", "type_alias_declaration",
    "interface_declaration", "trait_item", "impl_item",
    "enum_declaration", "enum_item", "record_declaration",
    "macro_definition", "attribute", "attribute_item", "decorator",
})


def should_summarize_node(node: dict) -> bool:
    language = node.get("language", "")
    node_type = node.get("node_type", "")
    
    if not language or not node_type:
        return False
    
    summarizable_types = SUMMARIZABLE_NODE_TYPES.get(language, DEFAULT_SUMMARIZABLE_TYPES)
    return node_type in summarizable_types


_SUPPORTED_TS_LANGUAGES: frozenset[str] = frozenset(SupportedLanguage.__args__)

_used_ids: set[str] = set()

def _reset_ids() -> None:
    _used_ids.clear()

def _new_id() -> str:
    while True:
        candidate = secrets.token_hex(3)
        if candidate not in _used_ids:
            _used_ids.add(candidate)
            return candidate

_magika = Magika()

def _detect_language(path: Path) -> str | None:
    try:
        result = _magika.identify_path(path)
    except Exception:
        return None

    if result.output.group != "code":
        return None

    label = result.output.label
    ts_lang = MAGIKA_TO_TS.get(label, label)
    if not ts_lang or ts_lang not in _SUPPORTED_TS_LANGUAGES:
        return None
    return ts_lang

def _node_name(ts_node) -> str | None:
    name_node = ts_node.child_by_field_name("name")
    if name_node is not None:
        return name_node.text.decode("utf-8", errors="replace")
    # even decorators can have internal functions and stuff
    if ts_node.type == "decorated_definition":
        for child in ts_node.children:
            if child.type in ("function_definition", "class_definition"):
                inner_title = _node_name(child)
                if inner_title:
                    return inner_title

    text = ts_node.text.decode("utf-8", errors="replace").strip()
    first_line = text.splitlines()[0] if text else ""
    if len(first_line) > 60:
        first_line = first_line[:57] + "..."
    return first_line or ts_node.type


def _extract_raw_nodes(path: Path, language: str) -> list[dict]:
    try:
        parser = get_parser(language)
        ts_tree = parser.parse(path.read_bytes())
    except Exception:
        return []

    abs_path = str(path.resolve())
    raw_nodes: list[dict] = []

    if language == "python":
        def traverse(node):
            if node.type == "module":
                for child in node.children:
                    traverse(child)
                return

            if node.type in PYTHON_IMPORT_TYPES:
                return

            if node.type == "block":
                for child in node.children:
                    traverse(child)
                return

            raw_nodes.append({
                "id":         _new_id(),
                "path":       abs_path,
                "language":   language,
                "node_type":  node.type,
                "title":      _node_name(node),
                "start_line": node.start_point[0] + 1,
                "end_line":   node.end_point[0] + 1,
                "summary":    "",
            })

            for child in node.children:
                if child.type in (
                    "block", "function_definition", "class_definition",
                    "decorated_definition", "if_statement", "for_statement",
                    "while_statement", "try_statement", "with_statement", "match_statement"
                ):
                    traverse(child)

        traverse(ts_tree.root_node)
        return raw_nodes

    node_types = LANGUAGE_NODE_TYPES.get(language, DEFAULT_NODE_TYPES)
    stack = [ts_tree.root_node]

    while stack:
        ts_node = stack.pop()
        if ts_node.type in node_types:
            raw_nodes.append({
                "id":         _new_id(),
                "path":       abs_path,
                "language":   language,
                "node_type":  ts_node.type,
                "title":      _node_name(ts_node),
                "start_line": ts_node.start_point[0] + 1,
                "end_line":   ts_node.end_point[0] + 1,
                "summary":    "",
            })
        stack.extend(reversed(ts_node.children))

    return raw_nodes


@dataclass
class _Entry:
    id: str
    name: str
    path: str
    entry_type: str           # "repository" or "folder" or "file"
    parent_id: str | None
    summary: str = ""
    # file entries only
    raw_nodes: list[dict] = field(default_factory=list)
    children: list["_Entry"] = field(default_factory=list)

    def to_dict(self) -> dict:
        d: dict = {
            "id":      self.id,
            "name":    self.name,
            "path":    self.path,
            "type":    self.entry_type,
            "parent":  self.parent_id,
            "summary": self.summary,
        }
        if self.entry_type == "file":
            d["node_ids"] = [n["id"] for n in self.raw_nodes]
            # I have embeded raw node metadata so nodes.py can read it without re-parsing.
        d["children"] = [c.to_dict() for c in self.children]
        return d


def _build_file_entry(path: Path, parent_id: str) -> _Entry:
    entry = _Entry(
        id=_new_id(),
        name=path.name,
        path=str(path.resolve()),
        entry_type="file",
        parent_id=parent_id,
    )
    lang = _detect_language(path)
    if lang:
        entry.raw_nodes = _extract_raw_nodes(path, lang)
    return entry


def _build_dir_entry(path: Path, parent_id: str | None, entry_type: str) -> _Entry:
    entry = _Entry(
        id=_new_id(),
        name=path.name or str(path),
        path=str(path.resolve()),
        entry_type=entry_type,
        parent_id=parent_id,
    )

    try:
        items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except OSError:
        return entry

    for item in items:
        if item.name in IGNORED_DIR_NAMES:
            continue
        if item.is_dir():
            entry.children.append(_build_dir_entry(item, entry.id, "folder"))
        elif item.is_file():
            entry.children.append(_build_file_entry(item, entry.id))

    return entry

def run_treesitter() -> Path:
    if state.repo_path is None:
        raise RuntimeError("No repository cloned. Call POST /repo first.")

    _reset_ids()

    logger.info("Running tree-sitter on %s", state.repo_path)
    root_entry = _build_dir_entry(state.repo_path, None, "repository")
    structure = root_entry.to_dict()

    out_path = (state.out_dir / "filestructure.json").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(structure, indent=2), encoding="utf-8")

    all_raw_nodes: list[dict] = []
    for file_entry in _iter_file_entries(root_entry):
        for node in file_entry.raw_nodes:
            node["parent_id"] = file_entry.id
            all_raw_nodes.append(node)

    state.raw_nodes = all_raw_nodes

    raw_nodes_path = (state.out_dir / ".raw_nodes.json").resolve()
    raw_nodes_path.write_text(json.dumps(all_raw_nodes, indent=2), encoding="utf-8")

    logger.info(
        "filestructure.json written: %d code nodes across the repository", len(all_raw_nodes)
    )
    return out_path


def _iter_file_entries(entry: _Entry):
    # to yield all file _Entry objects in the tree.
    if entry.entry_type == "file":
        yield entry
    for child in entry.children:
        yield from _iter_file_entries(child)
