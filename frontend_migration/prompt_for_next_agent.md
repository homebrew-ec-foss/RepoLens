# Frontend Migration & Integration Handoff Instructions

You are tasked with integrating a premium, highly polished frontend UI into a newly updated backend repository for **RepoLens**. The user has pulled recent backend changes (including new BM25 search, smart summarization, and classic RAG features) into a new directory. 

Your ultimate goal is to connect the beautiful, smooth frontend UI to this *new* backend, ensuring perfect feature parity, addressing known bugs, and maintaining the premium aesthetic.

**CRITICAL RULE:** Do NOT blindly overwrite the backend or ignore its new features. You must integrate the polished frontend around the *real* capabilities of this new backend.

---

## Phase 1: Study & Analysis (Do this first!)
1. **Analyze the New Backend:** Read `main.py`, `app/api/routes.py`, and `app/models/schemas.py`. Map out exactly what endpoints exist, what methods they use (GET/POST), and what their request/response schemas look like. Pay special attention to new endpoints (like BM25 search) and updated response payloads (like citations and context).
2. **Analyze the Frontend:** Look at the frontend code provided by the user. Note the CSS variables, layout structures, and `app.js` routing logic. Understand that the frontend was previously mocked to expect certain endpoints that the old backend didn't actually have.
3. **Compare & Reconcile:** Identify the gap between the frontend's expected API calls (e.g. `api('/repos')`) and the backend's actual defined routes.

---

## Phase 2: Feature Integration & Aesthetics
1. **Preserve the Premium Theme:** The existing frontend has a very specific, premium dark mode aesthetic (glassmorphism, smooth loading bars, no blank states, high-quality SVGs). You MUST preserve this exact theme. 
2. **Incorporate New Features:** If the new backend introduces new features (e.g. a BM25 search bar, new context in chat, etc.), you must build UI components for them that perfectly match the existing design system. Do not use unstyled native browser inputs or generic tables.
3. **Handle Conflicts:** If there is a conflict in parameters (like chunk size or batch size), prioritize the existing backend logic. Do not add or remove backend features just to fit the frontend; adapt the frontend to the backend.

---

## Phase 3: Fix Known Bugs & Missing Implementations
The previous iteration had several specific issues that you MUST resolve during this integration:

1. **Repository Persistence (`/repos` API):** 
   - *Problem:* Repositories parsed in previous sessions exist in the `out/` directory, but the frontend doesn't show them upon reload. The frontend expects a `GET /repos` endpoint, but the backend lacks it.
   - *Fix:* Create a `GET /repos` endpoint in the FastAPI backend that scans the `out/` directory for valid parsed repositories (e.g., checking for `filestructure.json`, `nodes.json`, etc.) and returns them in the expected format so the user doesn't have to re-parse.

2. **Graph View (3-Pane Layout):**
   - *Problem:* The graph view previously just dumped a raw SVG onto the screen.
   - *Fix:* Implement a strict 3-pane layout for the graph view. 
     - **Left Pane:** The File Tree Explorer.
     - **Center Pane:** The D3.js Force-Directed Graph.
     - **Right Pane:** The Inspector (showing node details, summary, and edge relationships).
     - Clicking a node in the graph must highlight it in the tree and update the inspector.

3. **Icon Rendering Glitches:**
   - *Problem:* `<svg>` elements were accidentally being rendered as raw text in buttons because they were string-concatenated in JavaScript (e.g., `el('button', {}, Icons.chevronLeft + ' Back')`).
   - *Fix:* When using the `Icons` dictionary, ensure SVGs are injected via `innerHTML` or parsed correctly as DOM nodes. For the Onboarding "Back" button specifically, simply remove the icon and just use the text `"Back"`.

4. **Chat & Citations Parsing:**
   - *Problem:* The frontend chat previously broke because it assumed `res.content`.
   - *Fix:* Ensure the frontend explicitly consumes `res.answer`, `res.citations`, and whatever new BM25 context fields are returned by the updated `POST /ask` endpoint.

5. **Loading States:**
   - *Problem:* The user requested exactly 3 smooth loading bars when a repository is being parsed. 
   - *Fix:* Ensure the UI correctly displays these 3 loading bars sequentially or concurrently without any blank states or unresponsive freezes.

---

**Execution:** 
Begin by confirming you have read these instructions and outline your map of the backend endpoints before you start modifying any frontend Javascript.
