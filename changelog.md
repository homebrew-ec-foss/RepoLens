# RepoLens Changelog

## [Unreleased]
### Added
- **Embedded Qdrant Support**: Added an embedded file-based fallback for the Qdrant Vector database in `app/services/vectorstore.py`. If the `QDRANT_URL` environment variable is not set, it defaults to a local path (`out/qdrant_db`), eliminating the strict requirement for users to run a Docker container for Qdrant.
- **Backend Log Streaming Route**: Added a `GET /logs` endpoint in `app/api/routes.py` to allow the frontend to fetch real-time backend pipeline logs during repository parsing.

### Fixed
- **API Key Persistence**: Fixed a bug where the Gemini API key was not being written to the persistent state file (`state.save()`) in the `/config` route. Users now only have to enter their API key once.
- **Backend Startup Crashes**: Updated `classifier.py`, `keyword_search.py`, `summaries.py`, and other AI services to lazily initialize the `google.genai` client. This prevents the server from crashing on startup when a user has not yet configured their API key.
- **Uvicorn Reload Loop Crash**: Identified and advised against watching the `out/` directory with Uvicorn's `--reload` flag. The constant writing of cloned repos and JSON states during the pipeline caused immediate server reloads and pipeline interruptions.

### Changed
- **File Explorer Tree view**: The UI's left-pane repository explorer was updated to only show files and directories, acting like a standard IDE explorer, rather than mixing functions and classes into the hierarchical folder tree.
