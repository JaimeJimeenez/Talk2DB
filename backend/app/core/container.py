from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine


from app.application.use_cases.conversations import ConversationsUseCase
from app.application.use_cases.rag import RagUseCase
from app.application.use_cases.rag_metrics import RagMetricsUseCase
from app.application.use_cases.schemas import SchemasUseCase
from app.application.use_cases.auth import AuthUseCase
from app.application.rag.database import DatabaseSchemaLoader, ReadonlySQLExecutor
from app.application.rag.llm import EmbeddingGateway, OllamaChatModel, SqlGenerator
from app.application.rag.schema_context import SchemaContextService
from app.application.rag.service import RagService

from app.infrastructure.adapters.conversations import ConversationsAdapter
from app.infrastructure.adapters.database.orm import Database
from app.infrastructure.adapters.rag_metrics import RagMetricsAdapter
from app.infrastructure.adapters.schemas import SchemasAdapter
from app.infrastructure.adapters.auth import AuthAdapter

from app.core.settings import get_settings



class Container(containers.DeclarativeContainer):
    session = providers.Dependency()
    settings = providers.Singleton(get_settings)
    database = providers.Singleton(Database, db_url=settings.provided.database_url)
    rag_engine = providers.Singleton(
        create_async_engine,
        settings.provided.rag_database_url,
        pool_pre_ping=True,
    )
    
    # Adapters

    schemas_adapter = providers.Factory(
        SchemasAdapter,
        session_factory=database.provided.session
    )

    conversations_adapter = providers.Factory(
        ConversationsAdapter,
        session_factory=database.provided.session
    )

    auth_adapter = providers.Factory(
        AuthAdapter,
        session_factory=database.provided.session
    )

    rag_metrics_adapter = providers.Factory(
        RagMetricsAdapter,
        session_factory=database.provided.session
    )

    # Use Case

    schemas_use_case = providers.Factory(
        SchemasUseCase,
        schemas_adapter=schemas_adapter
    )

    conversations_use_case = providers.Factory(
        ConversationsUseCase,
        conversations_port=conversations_adapter,
        schemas_port=schemas_adapter,
    )

    auth_use_case = providers.Factory(
        AuthUseCase,
        auth_adapter=auth_adapter
    )

    rag_metrics_use_case = providers.Factory(
        RagMetricsUseCase,
        rag_metrics_port=rag_metrics_adapter
    )

    # RAG

    embedding_gateway = providers.Factory(
        EmbeddingGateway,
        model=settings.provided.embedding_model,
        base_url=settings.provided.embedding_base_url,
    )

    chat_model = providers.Factory(
        OllamaChatModel,
        model=settings.provided.llm_model,
        base_url=settings.provided.llm_base_url,
    )

    sql_generator = providers.Factory(
        SqlGenerator,
        llm=chat_model,
    )

    schema_loader = providers.Factory(
        DatabaseSchemaLoader,
        engine=rag_engine,
    )

    sql_executor = providers.Factory(
        ReadonlySQLExecutor,
        engine=rag_engine,
    )

    schema_context = providers.Factory(
        SchemaContextService,
        embedding_gateway=embedding_gateway,
        qdrant_url=settings.provided.qdrant_url,
        collection_name=settings.provided.qdrant_collection,
        top_k=settings.provided.schema_retrieval_top_k,
    )

    rag_service = providers.Factory(
        RagService,
        schemas=schemas_adapter,
        schema_loader=schema_loader,
        schema_context=schema_context,
        sql_generator=sql_generator,
        sql_executor=sql_executor,
        model_name=settings.provided.llm_model,
    )

    rag_use_case = providers.Factory(
        RagUseCase,
        rag_service=rag_service,
        conversations_use_case=conversations_use_case,
        rag_metrics_use_case=rag_metrics_use_case
    )
