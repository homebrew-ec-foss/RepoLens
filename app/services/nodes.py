from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from app.storage.state import state

logger = logging.getLogger(__name__)
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
try:
    _client = genai.Client()
except Exception:
    _client = None

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
    filestructure_path = (state.out_dir / "filestructure.json").resolve()
    if not filestructure_path.exists():
        raise RuntimeError(
            "filestructure.json not found. Call POST /tree first."
        )

    logger.info("Reading %s", filestructure_path)
    structure: dict = json.loads(filestructure_path.read_text(encoding="utf-8"))

    raw_nodes: list[dict] = []
    _collect_raw_nodes(structure, structure.get("id", ""), raw_nodes)

    for node in raw_nodes:
        node.setdefault("children_ids", [])
        node.setdefault("summary", "")

    _compute_children_ids(raw_nodes)

    nodes_path = (state.out_dir / "nodes.json").resolve()
    nodes_path.write_text(
        json.dumps({"nodes": raw_nodes}, indent=2), encoding="utf-8"
    )

    logger.info("nodes.json written: %d nodes", len(raw_nodes))
    return nodes_path

def find_files_in_tree(id,data):
    if data['id'] == id:
        return data
    if 'children' in data:
        for child in data['children']:
            result = find_files_in_tree(id,child)
            if result:
                return result
    return None
def get_nodes_based_on_id(id):
    out_folder = Path(__file__).parent.parent.parent / 'out'
    with open(out_folder / 'nodes.json', 'r') as f:
        data = json.load(f)
    data = data['nodes']
    for item in data:
        if item['id'] == id:
            return item
    data = json.loads((out_folder / 'filestructure.json').read_text(encoding="utf-8"))
    return find_files_in_tree(id,data)

def retrieve_parent_and_child_nodes(pid,cid=None):
    p_node = get_nodes_based_on_id(pid)
    if cid:

        c_node = get_nodes_based_on_id(cid)
    else:
        c_node = None

    if not hasattr(p_node,'node_type'):
        p_node['node_type'] = 'file'
        p_node['start_line'] = 'Encompassing entire file'
        p_node['end_line'] = 'Encompassing entire file'
    if p_node:
        p_node = {"Path":p_node['path'],"node_type":p_node['node_type'],"identifier":p_node['id'],"line_range":f"{p_node['start_line']} - {p_node['end_line']}","summary":p_node['summary']}
    if c_node:
        c_node = {"Path":c_node['path'],"node_type":c_node['node_type'],"identifier":c_node['id'],"line_range":f"{c_node['start_line']} - {c_node['end_line']}","summary":c_node['summary']}
    if p_node and c_node:
        return {"parent_node":p_node,"child_node":c_node}
    if p_node and not c_node:
        return {"parent_node":p_node,"child_node":None}

    if c_node and not p_node:
        return {"parent_node":None,"child_node":c_node}
    if not p_node and not c_node:
        return {"parent_node":None,"child_node":None}

def answer_query_with_context(nodes,query):
    
    prompt = f"""You are a code assistant. You are given a query and a context of code nodes. Your task is to answer the query based on the context provided.
    You will be given a query and a context of code nodes. Your task is to answer the query based on the context provided. You should only use the information provided in the context to answer the query. If the context does not contain enough information to answer the query, you should respond with "I don't know". You should not make up any information or provide an answer that is not supported by the context.
    Query: {query}
    The context consists of a node, a parent node, and child nodes. The node is the main node that is relevant to the query. The parent node is the parent of the main node, and the child nodes are the children of the main node. You should use the information from the main node, parent node, and child nodes to answer the query. If any of these nodes are not available, you should ignore them in your answer.
    Context:
    Node: {nodes}
    Your job is to provide a concise and accurate answer to the query based on the context provided. If the context does not contain enough information to answer the query, you should respond with "I don't know". You should not make up any information or provide an answer that is not supported by the context.
    Also another thing you must do is answer the user's query along with the path of the node and the line number's of the selected lines in which the answer is found. If the answer is not found in any of the nodes, you should respond with "I don't know". You should not make up any information or provide an answer that is not supported by the context.

    The final response should be in the following JSON format:
    {{
        "answer": "<your answer here>",
        "path": "<path of the node where the answer is found>",
        "line_range": "<line range of the node where the answer is found>"
    }}
    """
    response = _client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return response.text.strip() if response and hasattr(response, "text") else "I don't know"