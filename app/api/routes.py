from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.models.schemas import RepoRequest, StatusResponse, QueryRequest, RAGAnswer
from app.services import github as github_svc
from app.services import nodes as nodes_svc
from app.services import summaries as summaries_svc
from app.services import treesitter as ts_svc
from app.storage.state import state
from app.services.classifier import classify
from app.services import edges as edges_svc
from app.services import rag as rag_svc
from app.services import vectorstore as vectorstore_svc
from app.services import content as content_svc
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/repo", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def post_repo(body: RepoRequest) -> StatusResponse:
    logger.info("POST /repo  url=%s", body.github_url)
    try:
        repo_path: Path = await github_svc.clone_repo(body.github_url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    return StatusResponse(
        status="ok",
        detail=f"Repository cloned to {repo_path}",
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


@router.post("/summary", response_model=StatusResponse, status_code=status.HTTP_200_OK)
async def post_summary() -> StatusResponse:
    logger.info("POST /summary")
    try:
        result = summaries_svc.run_summary_pipeline()
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /summary")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return StatusResponse(
        status="ok",
        detail=(
            f"Summary complete: {result['summarized_nodes']}/{result['total_nodes']} nodes summarized. "
            f"Root summary length: {result['root_summary_length']} chars."
        ),
    )

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
    logger.info("POST /ask query=%s", body.query)
    try:
        return RAGAnswer(**rag_svc.answer_query(body.query))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error in /ask")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/content/{node_id}", status_code=status.HTTP_200_OK)
async def get_content(node_id: str):
    logger.info("GET /content/%s", node_id)
    result = content_svc.get_node_content(node_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown node id: {node_id}")
    return result


@router.get("/data/{file_name}", status_code=status.HTTP_200_OK)
async def get_data_file(file_name: str):
    safe_name = Path(file_name).name
    if safe_name != file_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file name")
    path = (state.out_dir / safe_name).resolve()
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{file_name} not found in out directory")
    return FileResponse(path, media_type="application/json")
