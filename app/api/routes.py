from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import RepoRequest, StatusResponse
from app.services import github as github_svc
from app.services import nodes as nodes_svc
from app.services import summaries as summaries_svc
from app.services import treesitter as ts_svc
from app.storage.state import state

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
