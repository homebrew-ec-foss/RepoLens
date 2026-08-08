from __future__ import annotations

import logging
import os
from pathlib import Path
import json

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.models.schemas import RepoRequest, LocalRepoRequest, StatusResponse, QueryRequest, RAGAnswer, ConfigRequest, HealthResponse, ConfigResponse
from app.services import github as github_svc
from app.services import nodes as nodes_svc
from app.services import summaries as summaries_svc
from app.services import treesitter as ts_svc
from app.services import keyword_search as keyword_search_svc
from app.storage.state import state
from app.services.classifier import classify
from app.services import edges as edges_svc
from app.services import rag as rag_svc
from app.services import vectorstore as vectorstore_svc
from app.services import content as content_svc
logger = logging.getLogger(__name__)

router = APIRouter()

from google import genai
from google.genai.errors import ClientError

@router.post("/config", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def post_config(body: ConfigRequest) -> StatusResponse:
    logger.info("POST /config")
    if body.gemini_api_key:
        try:
            client = genai.Client(api_key=body.gemini_api_key)
            # Validate the key by making a minimal API call
            client.models.get(model="gemini-1.5-flash")
        except ClientError as e:
            logger.error(f"API key validation failed: {e}")
            raise HTTPException(status_code=400, detail="API key is invalid or unable to connect.")
        except Exception as e:
            logger.error(f"Unexpected error during API key validation: {e}")
            raise HTTPException(status_code=400, detail="Failed to validate API key.")
            
        os.environ["GEMINI_API_KEY"] = body.gemini_api_key
        state.gemini_api_key = body.gemini_api_key
        # Reset all cached genai clients so they pick up the new key
        summaries_svc._client = None
        rag_svc._client = None
        vectorstore_svc._client = None if hasattr(vectorstore_svc, '_client') else None
        keyword_search_svc._client = None
        try:
            from app.services import embeddings as emb_svc
            emb_svc._client = None
        except Exception:
            pass
        try:
            from app.services import classifier as cls_svc
            cls_svc._client = None
        except Exception:
            pass

        state.save()
        
    return StatusResponse(status="ok", detail="Configuration updated")

@router.get("/config", response_model=ConfigResponse, status_code=status.HTTP_200_OK)
async def get_config() -> ConfigResponse:
    logger.info("GET /config")
    key = os.environ.get("GEMINI_API_KEY") or state.gemini_api_key
    
    is_set = bool(key)
    preview = f"{key[:4]}...{key[-4:]}" if is_set and len(key) > 8 else None
    
    return ConfigResponse(
        api_key_set=is_set,
        api_key_preview=preview
    )

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def get_health() -> HealthResponse:
    logger.info("GET /health")
    return HealthResponse(
        status="ok",
        gemini_key_set=bool(os.environ.get("GEMINI_API_KEY")),
        ollama_running=False
    )

@router.post("/repo", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def post_repo(body: RepoRequest) -> StatusResponse:
    logger.info("POST /repo  url=%s", body.github_url)
    try:
        repo_path: Path = await github_svc.clone_repo(body.github_url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except RuntimeError as exc:
        import traceback
        logger.exception("RuntimeError in /repo")
        tb = traceback.format_exc()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"{str(exc)}\n{tb}")

    return StatusResponse(
        status="ok",
        detail=f"Repository cloned to {repo_path}",
    )


def _validate_local_folder(folder_path: str) -> Path:
    raw = (folder_path or "").strip()
    raw = raw.strip('"').strip("'")
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Folder path is required.",
        )
    try:
        folder = Path(raw).expanduser().resolve()
    except (OSError, RuntimeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid folder path: {exc}",
        )
    if not folder.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Folder does not exist: {folder}",
        )
    if not folder.is_dir():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Path is not a directory: {folder}",
        )
    try:
        if not os.access(folder, os.R_OK):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Folder is not readable: {folder}",
            )
        os.listdir(folder)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Folder could not be accessed: {folder} ({exc})",
        )
    out_resolved = state.out_dir.resolve()
    if folder == out_resolved or out_resolved in folder.parents:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot use RepoLens' output directory as a repository.",
        )
    return folder


@router.post("/repo/local", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def post_repo_local(body: LocalRepoRequest) -> StatusResponse:
    logger.info("POST /repo/local folder_path=%s", body.folder_path)
    folder = _validate_local_folder(body.folder_path)
    state.repo_path = folder
    logger.info("Local repo registered: %s", folder)
    return StatusResponse(
        status="ok",
        detail=f"Local folder registered: {folder}",
    )

@router.post("/tree", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def post_tree() -> StatusResponse:
    logger.info("POST /tree  repo=%s", state.repo_path)
    try:
        out_path: Path = ts_svc.run_treesitter()
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /tree")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return StatusResponse(
        status="ok",
        detail=f"filestructure.json written to {out_path}",
    )


@router.post("/nodes", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def post_nodes() -> StatusResponse:
    logger.info("POST /nodes")
    try:
        out_path: Path = nodes_svc.generate_nodes()
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /nodes")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return StatusResponse(
        status="ok",
        detail=f"nodes.json written to {out_path}",
    )


@router.post("/edges", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def post_edges() -> StatusResponse:
    logger.info("POST /edges")
    try:
        out_path: Path = edges_svc.generate_edges()
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /edges")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return StatusResponse(
        status="ok",
        detail=f"edges.json written to {out_path}",
    )


@router.post("/summary", status_code=status.HTTP_200_OK)
async def post_summary():
    logger.info("POST /summary")
    try:
        result = summaries_svc.run_summary_pipeline()
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /summary")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    # for the frontend loading bar
    return {
        "status": "ok",
        "detail": (
            f"Summary complete: {result['summarized_nodes']}/{result['total_nodes']} nodes summarized. "
            f"Root summary length: {result['root_summary_length']} chars."
        ),
        "summaries_completed": result["summarized_nodes"],
        "total_nodes": result["total_nodes"],
    }

@router.post("/query",response_model=StatusResponse,status_code=status.HTTP_200_OK)
async def user_query(body: QueryRequest) -> StatusResponse:
        logger.info("POST /query")
        try:
            res = classify(body.query)
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
        except Exception as exc:
            logger.exception("Unexpected error in /summary")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    
        return StatusResponse(
            status="ok",
            detail=(
                f"result = {res}"
            ),
        )
@router.post("/index", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def post_index() -> StatusResponse:
    logger.info("POST /index")
    try:
        result = vectorstore_svc.index_nodes()
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /index")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return StatusResponse(
        status="ok",
        detail=(
            f"Indexed {result['indexed']} nodes into Qdrant collection "
            f"'{result['collection']}' (dim {result['vector_dim']})"
        ),
    )


@router.post("/ask", response_model=RAGAnswer, status_code=status.HTTP_200_OK)
async def ask(body: QueryRequest) -> RAGAnswer:
    logger.info("POST /ask")
    try:
        if body.repo_owner and body.repo_name:
            target = (state.out_dir / "repo" / body.repo_owner / body.repo_name).resolve()
            if target.exists():
                state.repo_path = target
                
        if not state.repo_path:
            raise RuntimeError("No repository parsed. Call POST /repo first.")
        return rag_svc.answer_query(body.query, deep=body.deep)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /ask")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/search", status_code=status.HTTP_200_OK)
async def search(query: str):
    logger.info("GET /search query=%s", query)
    try:
        return {"results": keyword_search_svc.search_nodes(query)}
    except Exception as exc:
        logger.exception("Unexpected error in /search")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/pipeline/progress", status_code=status.HTTP_200_OK)
async def get_pipeline_progress():
    return state.pipeline_progress or {}


@router.get("/content/{node_id}", status_code=status.HTTP_200_OK)
async def get_content(node_id: str):
    logger.info("GET /content/%s", node_id)
    result = content_svc.get_node_content(node_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown node id: {node_id}")
    return result


@router.get("/get_code", status_code=status.HTTP_200_OK)
async def get_code(node_id: str):
    logger.info("GET /get_code node_id=%s", node_id)
    try:
        return content_svc.get_node_code(node_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.get("/data/{file_name}", status_code=status.HTTP_200_OK)
async def get_data_file(file_name: str):
    safe_name = Path(file_name).name
    if safe_name != file_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file name")
    path = (state.out_dir / safe_name).resolve()
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{file_name} not found in out directory")
    return FileResponse(path, media_type="application/json")

@router.get("/repos", status_code=status.HTTP_200_OK)
async def get_repos_list():
    logger.info("GET /repos")
    fs_path = state.out_dir / "filestructure.json"
    if fs_path.is_file():
        try:
            with open(fs_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            name = data.get("name", "Unknown Repository")
            file_count = _count_files(data)
            summarized = _count_summarized(data)
            return {"repos": [{
                "owner": "local",
                "name": name,
                "path": str(state.out_dir),
                "file_count": file_count,
                "node_count": _count_nodes_from_files(data),
                "has_summaries": summarized > 0,
                "summary_count": summarized,
            }]}
        except Exception:
            pass
    return {"repos": []}


def _count_files(node: dict) -> int:
    count = 0
    stack = [node]
    while stack:
        current = stack.pop()
        if current.get("type") == "file":
            count += 1
        stack.extend(current.get("children") or [])
    return count


def _count_nodes_from_files(node: dict) -> int:
    count = 0
    stack = [node]
    while stack:
        current = stack.pop()
        if current.get("type") == "file":
            count += len(current.get("node_ids") or [])
        stack.extend(current.get("children") or [])
    return count


def _count_summarized(node: dict) -> int:
    count = 0
    stack = [node]
    while stack:
        current = stack.pop()
        if current.get("summary"):
            count += 1
        stack.extend(current.get("children") or [])
    return count

@router.get("/structure", status_code=status.HTTP_200_OK)
async def get_structure_endpoint():
    return await get_data_file("filestructure.json")

@router.get("/nodes", status_code=status.HTTP_200_OK)
async def get_nodes_endpoint():
    return await get_data_file("nodes.json")

@router.get("/edges", status_code=status.HTTP_200_OK)
async def get_edges_endpoint():
    return await get_data_file("edges.json")

@router.get("/chats/{owner}/{repo}", status_code=status.HTTP_200_OK)
async def get_chats_endpoint(owner: str, repo: str):
    return {"conversations": []}

@router.get("/chat/{owner}/{repo}/{id}", status_code=status.HTTP_200_OK)
async def get_chat_endpoint(owner: str, repo: str, id: str):
    return {"messages": []}


@router.get('/test_qdrant')
async def test_qdrant():
    c = vectorstore_svc._collection_name()
    return str(vectorstore_svc.get_client().get_collection(c))
