from __future__ import annotations

from datetime import datetime

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from app.application.use_cases.rag_metrics import RagMetricsUseCase
from app.core.container import Container
from app.infrastructure.api.schemas.rag_metrics import RagMetricsSummaryResponse, RagRunResponse
from app.infrastructure.api.security import get_current_user_id

router = APIRouter(prefix="/api/v1/rag/metrics", tags=["rag-metrics"])


@router.get("/summary", response_model=RagMetricsSummaryResponse, status_code=status.HTTP_200_OK)
@inject
async def get_rag_metrics_summary(
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    schema_id: str | None = None,
    user_id: str = Depends(get_current_user_id),
    rag_metrics_use_case: RagMetricsUseCase = Depends(Provide[Container.rag_metrics_use_case]),
) -> RagMetricsSummaryResponse:
    _ = user_id
    summary = await rag_metrics_use_case.get_summary(
        from_date=from_date,
        to_date=to_date,
        schema_id=schema_id,
    )
    return RagMetricsSummaryResponse.model_validate(summary, from_attributes=True)


@router.get("/runs", response_model=list[RagRunResponse], status_code=status.HTTP_200_OK)
@inject
async def list_rag_metric_runs(
    limit: int = Query(default=25, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status"),
    schema_id: str | None = None,
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    user_id: str = Depends(get_current_user_id),
    rag_metrics_use_case: RagMetricsUseCase = Depends(Provide[Container.rag_metrics_use_case]),
) -> list[RagRunResponse]:
    _ = user_id
    runs = await rag_metrics_use_case.list_runs(
        limit=limit,
        status=status_filter,
        schema_id=schema_id,
        from_date=from_date,
        to_date=to_date,
    )
    return [RagRunResponse.model_validate(run, from_attributes=True) for run in runs]
