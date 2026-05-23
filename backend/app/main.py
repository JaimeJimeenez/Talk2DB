from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.container import Container
from app.core.settings import get_settings
from app.infrastructure.api.routers.conversations import router as conversations_router
from app.infrastructure.api.routers.health import router as health_router
from app.infrastructure.api.routers.query_schemas import router as query_schemas_router
from app.infrastructure.api.routers.user import router as user_router
from app.infrastructure.persistence.session import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if not getattr(app.state, "skip_database_initialization", False):
        await initialize_database()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Talk2DB API", version="0.1.0", lifespan=lifespan)
    app.container = Container()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(user_router)
    app.include_router(conversations_router)
    app.include_router(query_schemas_router)
    return app


app = create_app()
