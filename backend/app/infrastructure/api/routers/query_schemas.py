from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from app.application.use_cases.schemas import SchemasUseCase

from app.core.container import Container

from app.infrastructure.api.schemas.query_schemas import QuerySchemaResponse
from app.infrastructure.api.security import get_current_user_id

router = APIRouter(prefix="/api/v1/query-schemas", tags=["query-schemas"])


@router.get("", response_model=list[QuerySchemaResponse], status_code=status.HTTP_200_OK)
@inject
async def list_schemas(
    user_id: str = Depends(get_current_user_id),
    schemas_use_case: SchemasUseCase = Depends(Provide[Container.schemas_use_case]),
) -> list[QuerySchemaResponse]:
    schemas = await schemas_use_case.get_schemas()
    return [
        QuerySchemaResponse.model_validate(schema, from_attributes=True)
        for schema in schemas
    ]
