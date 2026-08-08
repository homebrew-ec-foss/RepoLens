import json
import re
from rank_bm25 import BM25Okapi
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

from app.storage.state import state

load_dotenv()
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client()
    return _client
def refine_nodes(query, nodes):
    prompt = f"""
You are given a user query and a set of candidate code nodes.
Your task is to select the single most relevant node for the query.

Instructions:
- Read the user's query carefully.
- Compare the candidate nodes in the provided set.
- Choose the one node that is most relevant to the query.
- If none seem relevant, return null.
- Return valid JSON only.
- The output must be either:
  - a single full node object matching the candidate node schema, or
  - null

User query:
{query}

Candidate nodes:
{json.dumps(nodes, ensure_ascii=False, indent=2)}
"""
    res = _get_client().models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type='application/json')
    )
    text = getattr(res, 'text', '') or ''
    try:
        parsed = json.loads(text)
        parsed = {"res": parsed}
        if isinstance(parsed, dict):
            return parsed
        return None
    except json.JSONDecodeError:
        return None

TYPE_FILTERS = {
    'function': {
        'function_definition', 'function_declaration',
        'method_definition', 'method_declaration',
        'arrow_function', 'decorated_definition',
    },
    'class': {
        'class_definition', 'class_declaration',
    },
}

def parse_type_filter(query):
    if not query or not isinstance(query, str):
        return None, query
    q = query.strip()
    if q.startswith('f:'):
        return 'function', q[2:].strip()
    if q.startswith('c:'):
        return 'class', q[2:].strip()
    return None, q

class BM25KeywordSearch:
    def __init__(self, json_file, field):
        self.json_file = json_file
        self.field = field
        self.obj = None
        self.data = []
        self.by_id = {}
        self.file_tree = None
        self.tokenizer = lambda data: re.findall(r'\w+', data or '')

    def load_json(self):
        with open(self.json_file, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        self.data = raw.get('nodes', [])
        self.data = [item for item in self.data if item.get('title') is not None]
        self.by_id = {item['id']: item for item in self.data}

    def load_file_tree(self):
        if self.file_tree is not None:
            return self.file_tree
        tree_path = state.repo_dir / 'filestructure.json'
        if tree_path.is_file():
            with open(tree_path, 'r', encoding='utf-8') as f:
                self.file_tree = json.load(f)
        else:
            self.file_tree = {}
        return self.file_tree

    def get_tree_entry_by_id(self, entry_id, node=None):
        if not entry_id:
            return None
        if node is None:
            node = self.load_file_tree()
        if not isinstance(node, dict):
            return None
        if node.get('id') == entry_id:
            return node
        for child in node.get('children', []):
            found = self.get_tree_entry_by_id(entry_id, child)
            if found:
                return found
        return None

    def build_bm25_index(self):
        corpus = [self.tokenizer(item.get(self.field, '')) for item in self.data if item.get(self.field) is not None]
        self.obj = BM25Okapi(corpus)

    def answer_query(self, query, top_k=None):
        query = self.tokenizer(query)
        if not query or self.obj is None:
            return []
        scores = self.obj.get_scores(query)
        ranked = sorted(zip(self.data, scores), key=lambda x: x[1], reverse=True)
        results = []
        for item, score in ranked:
            if score <= 0.0:
                continue
            item_copy = dict(item)
            item_copy['_bm25_score'] = float(score)
            results.append(item_copy)
        return results[:top_k] if top_k is not None else results

    def get_context(self, item):
        parent = None
        parent_id = item.get('parent_id')
        if parent_id:
            parent = self.by_id.get(parent_id)
            if parent is None:
                tree_parent = self.get_tree_entry_by_id(parent_id)
                if tree_parent is not None:
                    parent = {
                        'id': tree_parent.get('id'),
                        'path': tree_parent.get('path'),
                        'node_type': tree_parent.get('type'),
                        'title': tree_parent.get('name'),
                        'start_line': None,
                        'end_line': None,
                    }
        children = [self.by_id[cid] for cid in item.get('children_ids', []) if cid in self.by_id]
        return parent, children

_cached_engine = None
_cached_engine_path = None
_cached_engine_mtime = None


def _get_search_engine(nodes_path: Path) -> BM25KeywordSearch:
    global _cached_engine, _cached_engine_path, _cached_engine_mtime
    try:
        mtime = nodes_path.stat().st_mtime
    except OSError:
        mtime = None
    if (
        _cached_engine is None
        or _cached_engine_path != nodes_path
        or _cached_engine_mtime != mtime
    ):
        engine = BM25KeywordSearch(nodes_path, 'title')
        engine.load_json()
        engine.build_bm25_index()
        _cached_engine = engine
        _cached_engine_path = nodes_path
        _cached_engine_mtime = mtime
    return _cached_engine


def _nodes_json_path() -> Path:
    return state.repo_dir / 'nodes.json'


def answer_query(query):
    obj = _get_search_engine(_nodes_json_path())
    return refine_nodes(query, obj.answer_query(query))['res']

def filter_nodes_based_on_type(query, type_filter):
    obj = _get_search_engine(_nodes_json_path())
    hits = obj.answer_query(query, top_k=50)
    allowed = TYPE_FILTERS.get(type_filter, {type_filter})
    return [item for item in hits if item.get('node_type') in allowed]

def search_nodes(query):
    if not query or not str(query).strip():
        return []
    type_filter, query_text = parse_type_filter(query)
    obj = _get_search_engine(_nodes_json_path())

    if type_filter and not query_text:
        hits = [
            dict(item, _bm25_score=0.0)
            for item in obj.data
            if item.get('node_type') in TYPE_FILTERS[type_filter]
        ]
        hits.sort(key=lambda item: (item.get('title') or '').lower())
        hits = hits[:10]
    elif type_filter:
        hits = [
            item for item in obj.answer_query(query_text, top_k=50)
            if item.get('node_type') in TYPE_FILTERS[type_filter]
        ][:10]
    else:
        hits = obj.answer_query(query_text, top_k=10)

    results = []
    for item in hits:
        parent, children = obj.get_context(item)
        results.append({
            'id': item.get('id'),
            'title': item.get('title'),
            'path': item.get('path'),
            'language': item.get('language'),
            'node_type': item.get('node_type'),
            'start_line': item.get('start_line'),
            'end_line': item.get('end_line'),
            'parent_id': item.get('parent_id'),
            'children_ids': item.get('children_ids', []),
            'score': item.get('_bm25_score'),
            'parent': parent,
            'children': [
                {
                    'id': child.get('id'),
                    'title': child.get('title'),
                    'path': child.get('path'),
                    'language': child.get('language'),
                    'node_type': child.get('node_type'),
                    'start_line': child.get('start_line'),
                    'end_line': child.get('end_line'),
                    'parent_id': child.get('parent_id'),
                    'children_ids': child.get('children_ids', []),
                }
                for child in children
            ],
        })
    return results

def filter_based_on_type(query, type_filter):
    if not query or not str(query).strip():
        return []
    return filter_nodes_based_on_type(query, type_filter)
