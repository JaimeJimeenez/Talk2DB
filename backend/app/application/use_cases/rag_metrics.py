from __future__ import annotations

from app.domain.entities.rag_metrics import RagMetricsFilters, RagMetricsSummary, RagRun
from app.domain.ports.rag_metrics import RagMetricsPort


class RagMetricsUseCase:
    def __init__(self, rag_metrics_port: RagMetricsPort) -> None:
        self._rag_metrics_port = rag_metrics_port

    async def save_run(self, run: RagRun) -> RagRun:
        return await self._rag_metrics_port.save_run(run)

    async def get_summary(
        self,
        *,
        from_date=None,
        to_date=None,
        schema_id: str | None = None,
    ) -> RagMetricsSummary:
        return await self._rag_metrics_port.get_summary(
            RagMetricsFilters(
                from_date=from_date,
                to_date=to_date,
                schema_id=schema_id,
            )
        )

    async def list_runs(
        self,
        *,
        limit: int = 25,
        status: str | None = None,
        schema_id: str | None = None,
        from_date=None,
        to_date=None,
    ) -> list[RagRun]:
        return await self._rag_metrics_port.list_runs(
            RagMetricsFilters(
                from_date=from_date,
                to_date=to_date,
                schema_id=schema_id,
                status=status,
                limit=min(max(limit, 1), 100),
            )
        )
