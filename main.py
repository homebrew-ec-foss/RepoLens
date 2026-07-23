from __future__ import annotations

import logging
import logging.config
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.api.routes import router
from app.storage.state import state

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s:     %(name)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
})

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    state.out_dir = Path("out").resolve() # uses the storage class singleton method
    state.out_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Starting Repolens at : %s", state.out_dir)
    yield
    logger.info("RepoLens shutting down")


app = FastAPI(
    title="RepoLens",
    description=(),
    version="0.2.0",
    lifespan=lifespan,
)

# i felt like, this will file will grow much bigger 
# if i define all routes here, 
# hence i moved them
app.include_router(router)
