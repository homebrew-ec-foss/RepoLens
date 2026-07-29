import json
import re
from rank_bm25 import BM25Okapi
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
client = genai.Client()
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
    res = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type='application/json')
    )
    text = getattr(res, 'text', '') or ''
    try:
        
        parsed = json.loads(text)
        parsed = {"res":parsed}
        if isinstance(parsed, dict):
            return parsed
        return None
    except json.JSONDecodeError:
        return None
class BM25KeywordSearch:
    def __init__(self,json_file,field):
        self.json_file = json_file
        self.field = field
        self.obj = None
        self.tokenizer = lambda data: re.findall(r'\w+',data) 
    def load_json(self):
        with open(self.json_file,'r') as f:
            self.data = json.load(f)
        self.data = self.data['nodes']
        self.data = [item for item in self.data if item['title'] is not None]
    def build_bm25_index(self):
        corpus = [self.tokenizer(item.get(self.field,"")) for item in self.data if item[self.field] is not None]
        self.obj = BM25Okapi(corpus)

    def answer_query(self,query):
        query = self.tokenizer(query)
        scores = self.obj.get_scores(query)
        ranked = sorted(zip(self.data,scores),key=lambda x: x[1],reverse=True)
        res = []
        for item,score in ranked:
            if score > 0.0:
                res.append(item)
        return res
def answer_query(query):
    path = Path(__file__).parent.parent.parent / 'out' / 'nodes.json'
    obj = BM25KeywordSearch(path,'title')
    obj.load_json()
    obj.build_bm25_index()
    return refine_nodes(query,obj.answer_query(query))['res']

if __name__ == "__main__":
    print(answer_query("I want to know about the get_orders function"))