from __future__ import annotations

from collections import defaultdict
from contextlib import AbstractContextManager
from datetime import UTC, datetime
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.rag_metrics import (
    RagMetricBucket,
    RagMetricPoint,
    RagMetricsFilters,
    RagMetricsSummary,
    RagRun,
    RagSchemaMetric,
)
from app.domain.ports.rag_metrics import RagMetricsPort
from app.infrastructure.adapters.database.models.rag_runs import RagRunRecord


class RagMetricsAdapter(RagMetricsPort):
    _table_checked = False

    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
    ) -> None:
        self._session_factory = session_factory

    async def save_run(self, run: RagRun) -> RagRun:
        with self._session_factory() as session:
            self._ensure_table(session)
            record = RagRunRecord(
                id=run.id,
                conversation_id=run.conversation_id,
                message_id=run.message_id,
                user_id=run.user_id,
                schema_id=run.schema_id,
                schema_name=run.schema_name,
                prompt=run.prompt,
                status=run.status,
                created_at=run.created_at,
                started_at=run.started_at,
                completed_at=run.completed_at,
                duration_ms=run.duration_ms,
                attempt_count=run.attempt_count,
                repair_count=run.repair_count,
                sql_validated=run.sql_validated,
                sql_executed=run.sql_executed,
                generated_sql=run.generated_sql,
                error=run.error,
                row_count=run.row_count,
                truncated=run.truncated,
                used_context=run.used_context,
                context_message_count=run.context_message_count,
                model=run.model,
                retrieved_table_count=run.retrieved_table_count,
                retrieved_tables=run.retrieved_tables,
            )
            session.add(record)
            session.flush()
            return self._to_entity(record)

    async def get_summary(self, filters: RagMetricsFilters) -> RagMetricsSummary:
        with self._session_factory() as session:
            self._ensure_table(session)
            records = session.execute(self._filtered_select(filters)).scalars().all()
            total_runs = len(records)
            successful_runs = sum(1 for record in records if record.status == "success")
            failed_runs = total_runs - successful_runs
            return RagMetricsSummary(
                total_runs=total_runs,
                successful_runs=successful_runs,
                failed_runs=failed_runs,
                success_rate=round(successful_runs / total_runs, 4) if total_runs else 0,
                average_duration_ms=round(_average(record.duration_ms for record in records), 2),
                average_repair_count=round(_average(record.repair_count for record in records), 2),
                average_row_count=round(_average(record.row_count for record in records), 2),
                runs_by_day=_runs_by_day(records),
                latency_by_day=_latency_by_day(records),
                runs_by_schema=_runs_by_schema(records),
                errors_by_type=_errors_by_type(records),
                row_count_buckets=_row_count_buckets(records),
            )

    async def list_runs(self, filters: RagMetricsFilters) -> list[RagRun]:
        statement = self._filtered_select(filters)
        statement = statement.order_by(RagRunRecord.created_at.desc()).limit(filters.limit)
        with self._session_factory() as session:
            self._ensure_table(session)
            records = session.execute(statement).scalars().all()
            return [self._to_entity(record) for record in records]

    def _ensure_table(self, session: Session) -> None:
        if RagMetricsAdapter._table_checked:
            return
        bind = session.get_bind()
        RagRunRecord.__table__.create(bind=bind, checkfirst=True)
        RagMetricsAdapter._table_checked = True

    def _filtered_select(self, filters: RagMetricsFilters):
        statement = select(RagRunRecord)
        if filters.from_date is not None:
            statement = statement.where(RagRunRecord.created_at >= filters.from_date)
        if filters.to_date is not None:
            statement = statement.where(RagRunRecord.created_at <= filters.to_date)
        if filters.schema_id:
            statement = statement.where(RagRunRecord.schema_id == filters.schema_id)
        if filters.status:
            statement = statement.where(RagRunRecord.status == filters.status)
        return statement

    @staticmethod
    def _to_entity(record: RagRunRecord) -> RagRun:
        return RagRun(
            id=record.id,
            conversation_id=record.conversation_id,
            message_id=record.message_id,
            user_id=record.user_id,
            schema_id=record.schema_id,
            schema_name=record.schema_name,
            prompt=record.prompt,
            status=record.status,
            created_at=record.created_at,
            started_at=record.started_at,
            completed_at=record.completed_at,
            duration_ms=record.duration_ms,
            attempt_count=record.attempt_count,
            repair_count=record.repair_count,
            sql_validated=record.sql_validated,
            sql_executed=record.sql_executed,
            generated_sql=record.generated_sql,
            error=record.error,
            row_count=record.row_count,
            truncated=record.truncated,
            used_context=record.used_context,
            context_message_count=record.context_message_count,
            model=record.model,
            retrieved_table_count=record.retrieved_table_count,
            retrieved_tables=list(record.retrieved_tables or []),
        )


def _average(values) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0


def _day_label(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.date().isoformat()


def _runs_by_day(records: list[RagRunRecord]) -> list[RagMetricPoint]:
    grouped: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "success": 0, "error": 0})
    for record in records:
        label = _day_label(record.created_at)
        grouped[label]["total"] += 1
        grouped[label][record.status] += 1
    return [
        RagMetricPoint(
            label=label,
            total=counts["total"],
            successful=counts["success"],
            failed=counts["error"],
        )
        for label, counts in sorted(grouped.items())
    ]


def _latency_by_day(records: list[RagRunRecord]) -> list[RagMetricPoint]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for record in records:
        grouped[_day_label(record.created_at)].append(record.duration_ms)
    return [
        RagMetricPoint(
            label=label,
            total=len(values),
            average_duration_ms=round(_average(values), 2),
        )
        for label, values in sorted(grouped.items())
    ]


def _runs_by_schema(records: list[RagRunRecord]) -> list[RagSchemaMetric]:
    grouped: dict[tuple[str, str], int] = defaultdict(int)
    for record in records:
        grouped[(record.schema_id, record.schema_name)] += 1
    return [
        RagSchemaMetric(schema_id=schema_id, schema_name=schema_name, count=count)
        for (schema_id, schema_name), count in sorted(grouped.items(), key=lambda item: item[1], reverse=True)
    ]


def _errors_by_type(records: list[RagRunRecord]) -> list[RagMetricBucket]:
    grouped: dict[str, int] = defaultdict(int)
    for record in records:
        if record.status != "error":
            continue
        grouped[_error_label(record.error)] += 1
    return [
        RagMetricBucket(label=label, count=count)
        for label, count in sorted(grouped.items(), key=lambda item: item[1], reverse=True)
    ]


def _error_label(error: str | None) -> str:
    if not error:
        return "Error desconocido"
    first_line = error.strip().splitlines()[0]
    if ":" in first_line:
        return first_line.split(":", 1)[0][:80]
    return first_line[:80]


def _row_count_buckets(records: list[RagRunRecord]) -> list[RagMetricBucket]:
    buckets = {
        "0": 0,
        "1-10": 0,
        "11-100": 0,
        "101-1000": 0,
        ">1000": 0,
    }
    for record in records:
        if record.row_count == 0:
            buckets["0"] += 1
        elif record.row_count <= 10:
            buckets["1-10"] += 1
        elif record.row_count <= 100:
            buckets["11-100"] += 1
        elif record.row_count <= 1000:
            buckets["101-1000"] += 1
        else:
            buckets[">1000"] += 1
    return [RagMetricBucket(label=label, count=count) for label, count in buckets.items()]
