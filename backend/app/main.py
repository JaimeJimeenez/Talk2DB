from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.container import Container
from app.core.settings import get_settings
from app.infrastructure.api.routers.auth import router as auth_router
from app.infrastructure.api.routers.conversations import router as conversations_router
from app.infrastructure.api.routers.query_schemas import router as query_schemas_router
from app.infrastructure.api.routers.rag import router as rag_router
from app.infrastructure.api.routers.rag_metrics import router as rag_metrics_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Talk2DB API", version="0.1.0")
    app.container = Container()
    app.container.wire(
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


app = create_app()
