import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
try:

    client = genai.Client()

except:
    client = None 

model = "gemini-3.1-flash-lite"


def build_prompt(query: str) -> str:
    return f"""You are classifying how a user should retrieve code nodes.

User question: {query}

Return only one integer:
- 0 if the question requires semantic search using node summaries to find the most relevant node(s) to answer the question.
- 1 if a simple keyword search over node names/titles is sufficient to find suitable node(s).

Examples:
- 'Explain the purpose of the login flow' -> 0
- 'Find the LoginController node' -> 1

Respond with exactly one digit: 0 or 1."""


def _heuristic_classify(query: str) -> int:
    if not query:
        return 1

    query = query.lower()
    semantic_markers = [
        "explain", "describe", "purpose", "role", "responsibility",
        "how does", "why", "what does", "what is", "summarize",
        "behavior", "flow", "logic", "relationship", "architecture",
        "understand", "meaning", "intent"
    ]
    keyword_markers = [
        "find", "search", "locate", "show", "get", "open", "node",
        "class", "function", "method", "file", "component", "controller",
        "service", "model"
    ]

    if any(marker in query for marker in semantic_markers):
        return 0

    if any(marker in query for marker in keyword_markers):
        return 1

    return 1


def classify(query: str) -> int:
    try:

        prompt = build_prompt(query)
    except:
        return _heuristic_classify(query)
    if client is None or types is None:
        return _heuristic_classify(query)

    response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    text = getattr(response, "text", "") or ""
    match = re.search(r"\b([01])\b", text)
    if match:
        return int(match.group(1))

    return _heuristic_classify(query)