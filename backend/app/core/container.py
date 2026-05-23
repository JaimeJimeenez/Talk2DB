from dependency_injector import containers, providers

from app.application.use_cases.conversations import Conversations
from app.application.use_cases.messages import Messages
from app.application.use_cases.query_schemas import QuerySchemas
from app.application.use_cases.users import Users
from app.core.settings import get_settings
from app.infrastructure.api.security import TokenAuthenticator
from app.infrastructure.persistence.repositories.conversations import SqlAlchemyConversationsRepository
from app.infrastructure.persistence.repositories.query_schemas import SqlAlchemyQuerySchemasRepository
from app.infrastructure.persistence.repositories.users import SqlAlchemyUsersRepository
from app.infrastructure.persistence.session import engine, rag_engine
from app.infrastructure.rag.assistant import RagAssistantGateway
from app.infrastructure.rag.openai_client import OpenAITextClient
from app.infrastructure.rag.schema_context import SchemaContextBuilder


class Container(containers.DeclarativeContainer):
    session = providers.Dependency()

    settings = providers.Singleton(get_settings)

    conversations_repository = providers.Factory(
        SqlAlchemyConversationsRepository,
        session=session,
    )
    query_schemas_repository = providers.Factory(
        SqlAlchemyQuerySchemasRepository,
        session=session,
    )
    users_repository = providers.Factory(
        SqlAlchemyUsersRepository,
        session=session,
    )

    database_engine = providers.Object(engine)
    rag_database_engine = providers.Object(rag_engine)

    schema_context_builder = providers.Factory(
        SchemaContextBuilder,
        engine=database_engine,
    )
    openai_client = providers.Factory(
        OpenAITextClient,
        api_key=settings.provided.openai_api_key,
        model=settings.provided.openai_model,
    )
    assistant_gateway = providers.Factory(
        RagAssistantGateway,
        schemas=query_schemas_repository,
        engine=rag_database_engine,
        llm=openai_client,
    )

    conversations_use_case = providers.Factory(
        Conversations,
        repository=conversations_repository,
        schemas=query_schemas_repository,
    )
    messages_use_case = providers.Factory(
        Messages,
        repository=conversations_repository,
        assistant=assistant_gateway,
    )
    query_schemas_use_case = providers.Factory(
        QuerySchemas,
        repository=query_schemas_repository,
        context_builder=schema_context_builder,
    )

    users_use_case = providers.Factory(
        Users,
        repository=users_repository,
    )

    token_authenticator = providers.Factory(
        TokenAuthenticator,
        users=users_repository,
        settings=settings,
    )
