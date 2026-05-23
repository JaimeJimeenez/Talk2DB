from fastapi import APIRouter, HTTPException, Request, status
from dependency_injector import providers

from app.infrastructure.api.routers.dependencies import SessionDep
from app.infrastructure.api.schemas.query_schema import QuerySchemaResponse, RegisterQuerySchemaRequest
from app.domain.errors import QuerySchemaNotFoundError, QuerySchemaUnavailableError

router = APIRouter(prefix="/api/v1/query-schemas", tags=["query-schemas"])


@router.post("", response_model=QuerySchemaResponse, status_code=status.HTTP_201_CREATED)
async def register_schema(
    payload: RegisterQuerySchemaRequest,
    request: Request,
    session: SessionDep,
) -> QuerySchemaResponse:
    with request.app.container.session.override(providers.Object(session)):
        schemas = request.app.container.query_schemas_use_case()
    try:
        schema = await schemas.register(payload.name, payload.description, payload.business_rules)
    except QuerySchemaUnavailableError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return QuerySchemaResponse.model_validate(schema, from_attributes=True)


@router.get("", response_model=list[QuerySchemaResponse])
async def list_schemas(request: Request, session: SessionDep) -> list[QuerySchemaResponse]:
    with request.app.container.session.override(providers.Object(session)):
        schemas = request.app.container.query_schemas_use_case()
    return [
        QuerySchemaResponse.model_validate(schema, from_attributes=True)
        for schema in await schemas.list()
    ]


@router.post("/{schema_id}/refresh", response_model=QuerySchemaResponse)
async def refresh_schema(
    schema_id: str,
    request: Request,
    session: SessionDep,
) -> QuerySchemaResponse:
    with request.app.container.session.override(providers.Object(session)):
        schemas = request.app.container.query_schemas_use_case()
    try:
        schema = await schemas.refresh(schema_id)
    except QuerySchemaNotFoundError as error:
        raise HTTPException(status_code=404, detail="Schema not found") from error
    except QuerySchemaUnavailableError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return QuerySchemaResponse.model_validate(schema, from_attributes=True)
