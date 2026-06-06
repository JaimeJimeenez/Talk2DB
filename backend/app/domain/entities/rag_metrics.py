from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RagRun:
    id: str
    conversation_id: str
    message_id: str
    user_id: str
    schema_id: str
    schema_name: str
    prompt: str
    status: str
    created_at: datetime
    started_at: datetime
    completed_at: datetime
    duration_ms: int
    attempt_count: int
    repair_count: int
    sql_validated: bool
    sql_executed: bool
    generated_sql: str | None
    error: str | None
    row_count: int
    truncated: bool
    used_context: bool
    context_message_count: int
    model: str
    retrieved_table_count: int
    retrieved_tables: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RagMetricsFilters:
    from_date: datetime | None = None
    to_date: datetime | None = None
    schema_id: str | None = None
    status: str | None = None
    limit: int = 25


@dataclass(frozen=True)
class RagMetricPoint:
    label: str
    total: int
    successful: int = 0
    failed: int = 0
    average_duration_ms: float = 0


@dataclass(frozen=True)
class RagMetricBucket:
    label: str
    count: int


@dataclass(frozen=True)
class RagSchemaMetric:
    schema_id: str
    schema_name: str
    count: int


@dataclass(frozen=True)
class RagMetricsSummary:
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    average_duration_ms: float
    average_repair_count: float
    average_row_count: float
    runs_by_day: list[RagMetricPoint]
    latency_by_day: list[RagMetricPoint]
    runs_by_schema: list[RagSchemaMetric]
    errors_by_type: list[RagMetricBucket]
    row_count_buckets: list[RagMetricBucket]
