from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RagMetricPointResponse(BaseModel):
    label: str
    total: int
    successful: int = 0
    failed: int = 0
    average_duration_ms: float = 0


class RagMetricBucketResponse(BaseModel):
    label: str
    count: int


class RagSchemaMetricResponse(BaseModel):
    schema_id: str
    schema_name: str
    count: int


class RagMetricsSummaryResponse(BaseModel):
    total_runs: int
    successful_runs: int
    failed_runs: int
    success_rate: float
    average_duration_ms: float
    average_repair_count: float
    average_row_count: float
    runs_by_day: list[RagMetricPointResponse]
    latency_by_day: list[RagMetricPointResponse]
    runs_by_schema: list[RagSchemaMetricResponse]
    errors_by_type: list[RagMetricBucketResponse]
    row_count_buckets: list[RagMetricBucketResponse]


class RagRunResponse(BaseModel):
    id: str
    created_at: datetime
    status: str
    schema_id: str
    schema_name: str
    conversation_id: str
    message_id: str
    prompt: str
    generated_sql: str | None
    error: str | None
    duration_ms: int
    attempt_count: int
    repair_count: int
    row_count: int
    used_context: bool
