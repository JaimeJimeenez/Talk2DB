from datetime import datetime

from pydantic import BaseModel


class QuerySchemaColumnResponse(BaseModel):
    name: str
    data_type: str
    nullable: bool
    default: str | None = None


class QuerySchemaConstraintResponse(BaseModel):
    column: str
    foreign_table_schema: str
    foreign_table_name: str
    foreign_column_name: str


class QuerySchemaTableResponse(BaseModel):
    name: str
    columns: list[QuerySchemaColumnResponse]
    constraints: list[QuerySchemaConstraintResponse]


class QuerySchemaResponse(BaseModel):
    id: str
    name: str
    description: str
    business_rules: str
    created_at: datetime
    refreshed_at: datetime
    table_count: int = 0
    column_count: int = 0


class QuerySchemaDetailResponse(QuerySchemaResponse):
    tables: list[QuerySchemaTableResponse]
