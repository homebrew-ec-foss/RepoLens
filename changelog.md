# RepoLens Changelog

## [Recent Updates]

### UI & UX Improvements
- **Graph Node Selection & Highlighting**: Fixed the issue where clicking a node caused the graph camera to "randomly fly off". Clicking a node now correctly centers the camera, highlights the node, and immediately displays its AI-generated summary in the right-side information panel.
- **Global Search Integration**: Upgraded the global search and left-pane search functionalities so that clicking on a search result correctly navigates to the graph, focusing and highlighting the matched node.
- **Left Panel Directory Explorer**: Completely stripped out code symbols (like functions, classes, and comments) from the left-side file explorer. It now strictly displays a clean directory tree (folders and files), functioning exactly like VSCode or standard IDE file explorers.
- **Misc Nodes Toggle UI**: Added a toggle box (placed compactly in the top-most empty bar space) that allows users to seamlessly show or hide miscellaneous nodes (like comments or generic functions) without separating or destroying the primary graph layout. The repository architecture is now strictly treated as a file system hierarchy.
- **API Key Onboarding Screen**: Built a robust API Key input modal that saves the user's Gemini API key permanently to the backend state upon entry. Users only have to enter their API Key once during onboarding or when changing it via settings.

### Backend & Infrastructure Fixes
- **Embedded Vector Database**: Modified `vectorstore.py` to use an embedded local database for Qdrant (`out/qdrant_db`) if the `QDRANT_URL` is not explicitly set in the environment. This completely removes the strict requirement for developers to spin up a Qdrant Docker container just to parse a repository.
- **API Key Persistence & State Saving**: Fixed the `/config` route to correctly execute `state.save()` so the Gemini API key persists reliably across server restarts.
- **Lazy AI Client Initialization**: Fixed backend startup crashes that occurred when the server launched without an API key present. Services (`classifier`, `keyword_search`, `summaries`, `rag`) now lazily initialize the `google.genai` client only when an API call is actively made.
- **Uvicorn Reload Loop Crash Resolved**: Identified a critical crash loop during the parsing pipeline (`POST /summary` -> `POST /index`). When the backend cloned the repository to the `out/` folder, the Uvicorn `--reload` watcher detected the file changes and prematurely restarted the server, breaking the connection. Excluded the `out/` directory from the watcher.
- **Pipeline Log Route**: Implemented the foundation for real-time parsing logs by adding a `GET /logs` endpoint to `routes.py`, allowing the frontend to poll and see exactly which node and batch is being processed.
