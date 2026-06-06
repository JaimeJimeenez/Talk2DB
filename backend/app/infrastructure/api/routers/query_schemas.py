from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.application.use_cases.schemas import SchemasUseCase

from app.core.container import Container
from app.domain.errors import QuerySchemaImportError
from app.infrastructure.adapters.database.models.users import UserRecord

from app.infrastructure.api.schemas.query_schemas import QuerySchemaDetailResponse, QuerySchemaResponse
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


@router.get("/{schema_id}", response_model=QuerySchemaDetailResponse, status_code=status.HTTP_200_OK)
@inject
async def get_schema_detail(
    schema_id: str,
    user_id: str = Depends(get_current_user_id),
    schemas_use_case: SchemasUseCase = Depends(Provide[Container.schemas_use_case]),
) -> QuerySchemaDetailResponse:
    schema = await schemas_use_case.get_schema_detail(schema_id)
    if schema is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Schema '{schema_id}' was not found.")
    return QuerySchemaDetailResponse.model_validate(schema, from_attributes=True)


@router.post("/import", response_model=QuerySchemaDetailResponse, status_code=status.HTTP_201_CREATED)
@inject
async def import_schema(
    name: str = Form(...),
    description: str = Form(""),
    business_rules: str = Form(""),
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    schemas_use_case: SchemasUseCase = Depends(Provide[Container.schemas_use_case]),
    database=Depends(Provide[Container.database]),
) -> QuerySchemaDetailResponse:
    _require_admin_user(database, user_id)
    content = await file.read()
    try:
        schema = await schemas_use_case.import_schema(
            name=name,
            description=description,
            business_rules=business_rules,
            filename=file.filename or "",
            content=content,
        )
    except QuerySchemaImportError as error:
        status_code = status.HTTP_409_CONFLICT if "already exists" in str(error) else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(error)) from error
    return QuerySchemaDetailResponse.model_validate(schema, from_attributes=True)


def _require_admin_user(database, user_id: str) -> None:
    with database.session() as session:
        user = session.get(UserRecord, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        if user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin users can import schemas.")
