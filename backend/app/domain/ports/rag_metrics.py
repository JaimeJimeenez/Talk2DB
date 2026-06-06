from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.rag_metrics import RagMetricsFilters, RagMetricsSummary, RagRun


class RagMetricsPort(ABC):
    @abstractmethod
    async def save_run(self, run: RagRun) -> RagRun:
        raise NotImplementedError

    @abstractmethod
    async def get_summary(self, filters: RagMetricsFilters) -> RagMetricsSummary:
        raise NotImplementedError

    @abstractmethod
    async def list_runs(self, filters: RagMetricsFilters) -> list[RagRun]:
        raise NotImplementedError
