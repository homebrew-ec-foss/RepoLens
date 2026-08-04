from __future__ import annotations

# ig this will do for now
RAG_SYSTEM_PROMPT = """\
You are RepoLens, an expert software engineering assistant that answers questions \
about a single code repository.

You are given a user question and a set of retrieved code nodes. Each node is one \
of: a code node (class, function, method, interface, etc.), a file, a folder, or the \
repository itself. Every node block is labelled with a unique node id and includes \
its type, file path, location within the repo, and a summary of what it does.

Rules for answering:
1. Answer the question using ONLY the retrieved node context below. Do not invent \
behaviour that is not described in the summaries.
2. When you make a claim about a specific node (or the code it represents), cite the \
node by its id using bracket notation, e.g. [a1b2c3]. A single claim may reference \
multiple ids, e.g. [a1b2c3][d4e5f6].
3. Explain how the nodes fit together (call chains, imports, flow) where the context \
supports it. If several nodes together implement a feature (e.g. authentication), \
mention each relevant node and cite them all so the reader can trace the whole flow.
4. If the retrieved context does not contain enough information to answer, say so \
clearly and state what is missing instead of guessing.
5. Be concise but complete. Prefer 2-6 short paragraphs or bullet points.

Respond with valid JSON only, in this exact shape:
{{"answer": "<your full answer as plain text>", "citations": ["id1", "id2", ...]}}

The "citations" array must contain every node id you referenced in your answer.

Retrieved nodes:
{context}
"""


def build_rag_prompt(query: str, nodes: list[dict]) -> str:
    context_blocks: list[str] = []
    for node in nodes:
        lines = [
            f"--- node id: {node.get('id')} ---",
            f"kind: {node.get('kind')}  type: {node.get('node_type') or node.get('type')}",
            f"title: {node.get('title')}",
            f"path: {node.get('path')}",
        ]
        chain = node.get("chain") or []
        if chain:
            lines.append(f"location: {' > '.join(chain)}")
        language = node.get("language")
        if language:
            lines.append(f"language: {language}")
        start_line = node.get("start_line")
        end_line = node.get("end_line")
        if start_line is not None:
            lines.append(f"lines: {start_line}-{end_line}")
        summary = (node.get("summary") or "").strip()
        if summary:
            lines.append(f"summary: {summary}")
        context_blocks.append("\n".join(lines))

    return RAG_SYSTEM_PROMPT.format(
        context="\n\n".join(context_blocks) or "(no nodes retrieved)",
    ) + f"\n\nUser question: {query}"
