import asyncio
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.application.rag.bootstrap import seed_schema_context
from app.core.container import Container
from app.core.settings import get_settings
from app.infrastructure.api.routers.auth import router as auth_router
from app.infrastructure.api.routers.conversations import router as conversations_router
from app.infrastructure.api.routers.query_schemas import router as query_schemas_router
from app.infrastructure.api.routers.rag import router as rag_router
from app.infrastructure.api.routers.rag_metrics import router as rag_metrics_router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    container = Container()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        bootstrap_task = None
        if settings.seed_schema_context_on_startup:
            bootstrap_task = asyncio.create_task(seed_schema_context(container))
            bootstrap_task.add_done_callback(_log_bootstrap_error)
        yield
        if bootstrap_task is not None and not bootstrap_task.done():
            bootstrap_task.cancel()

    app = FastAPI(title="Talk2DB API", version="0.1.0", lifespan=lifespan)
    app.container = container
    container.wire(
        modules=[
            "app.infrastructure.api.routers.auth",
            "app.infrastructure.api.routers.conversations",
            "app.infrastructure.api.routers.query_schemas",
            "app.infrastructure.api.routers.rag",
            "app.infrastructure.api.routers.rag_metrics",
        ]
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(auth_router)
    app.include_router(conversations_router)
    app.include_router(query_schemas_router)
    app.include_router(rag_router)
    app.include_router(rag_metrics_router)
    return app


def _log_bootstrap_error(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    error = task.exception()
    if error is not None:
        logger.warning("RAG context bootstrap task failed: %s", error)


app = create_app()
