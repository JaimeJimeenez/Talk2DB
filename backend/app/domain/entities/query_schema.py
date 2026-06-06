from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class QuerySchemaColumn:
    name: str
    data_type: str
    nullable: bool
    default: str | None = None


@dataclass(slots=True)
class QuerySchemaConstraint:
    column: str
    foreign_table_schema: str
    foreign_table_name: str
    foreign_column_name: str


@dataclass(slots=True)
class QuerySchemaTable:
    name: str
    columns: list[QuerySchemaColumn]
    constraints: list[QuerySchemaConstraint]


@dataclass(slots=True)
class QuerySchema:
    id: str
    name: str
    description: str
    business_rules: str
    context: str
    created_at: datetime
    refreshed_at: datetime
    table_count: int = 0
    column_count: int = 0
    tables: list[QuerySchemaTable] | None = None
