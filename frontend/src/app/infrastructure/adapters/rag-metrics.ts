import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';

import { RagMetricsFilters, RagMetricsSummary, RagRun, RagRunStatus } from '@domain/models/rag-metrics';
import { RagMetricsPort } from '@domain/ports/rag-metrics';
import { ApiService } from '@infrastructure/api/api';

type ApiMetricPoint = {
  readonly label: string;
  readonly total: number;
  readonly successful: number;
  readonly failed: number;
  readonly average_duration_ms: number;
};

type ApiMetricBucket = {
  readonly label: string;
  readonly count: number;
};

type ApiSchemaMetric = {
  readonly schema_id: string;
  readonly schema_name: string;
  readonly count: number;
};

type ApiMetricsSummary = {
  readonly total_runs: number;
  readonly successful_runs: number;
  readonly failed_runs: number;
  readonly success_rate: number;
  readonly average_duration_ms: number;
  readonly average_repair_count: number;
  readonly average_row_count: number;
  readonly runs_by_day: ApiMetricPoint[];
  readonly latency_by_day: ApiMetricPoint[];
  readonly runs_by_schema: ApiSchemaMetric[];
  readonly errors_by_type: ApiMetricBucket[];
  readonly row_count_buckets: ApiMetricBucket[];
};

type ApiRagRun = {
  readonly id: string;
  readonly created_at: string;
  readonly status: RagRunStatus;
  readonly schema_id: string;
  readonly schema_name: string;
  readonly conversation_id: string;
  readonly message_id: string;
  readonly prompt: string;
  readonly generated_sql: string | null;
  readonly error: string | null;
  readonly duration_ms: number;
  readonly attempt_count: number;
  readonly repair_count: number;
  readonly row_count: number;
  readonly used_context: boolean;
};

@Injectable()
export class RagMetricsAdapter extends RagMetricsPort {
  private readonly _http = inject(ApiService);

  getSummary(filters: RagMetricsFilters = {}): Observable<RagMetricsSummary> {
    return this._http.get<ApiMetricsSummary>('rag/metrics/summary', this._params(filters)).pipe(
      map(summary => this._mapSummary(summary)),
    );
  }

  getRuns(filters: RagMetricsFilters & { readonly limit?: number; readonly status?: RagRunStatus } = {}): Observable<RagRun[]> {
    return this._http.get<ApiRagRun[]>('rag/metrics/runs', this._params(filters)).pipe(
      map(runs => runs.map(run => this._mapRun(run))),
    );
  }

  private _params(filters: RagMetricsFilters & { readonly limit?: number; readonly status?: RagRunStatus }): Record<string, string | number> {
    const params: Record<string, string | number> = {};
    if (filters.from) params['from'] = filters.from;
    if (filters.to) params['to'] = filters.to;
    if (filters.schemaId) params['schema_id'] = filters.schemaId;
    if (filters.limit) params['limit'] = filters.limit;
    if (filters.status) params['status'] = filters.status;
    return params;
  }

  private _mapSummary(summary: ApiMetricsSummary): RagMetricsSummary {
    return {
      totalRuns: summary.total_runs,
      successfulRuns: summary.successful_runs,
      failedRuns: summary.failed_runs,
      successRate: summary.success_rate,
      averageDurationMs: summary.average_duration_ms,
      averageRepairCount: summary.average_repair_count,
      averageRowCount: summary.average_row_count,
      runsByDay: summary.runs_by_day.map(point => ({
        label: point.label,
        total: point.total,
        successful: point.successful,
        failed: point.failed,
        averageDurationMs: point.average_duration_ms,
      })),
      latencyByDay: summary.latency_by_day.map(point => ({
        label: point.label,
        total: point.total,
        successful: point.successful,
        failed: point.failed,
        averageDurationMs: point.average_duration_ms,
      })),
      runsBySchema: summary.runs_by_schema.map(schema => ({
        schemaId: schema.schema_id,
        schemaName: schema.schema_name,
        count: schema.count,
      })),
      errorsByType: summary.errors_by_type,
      rowCountBuckets: summary.row_count_buckets,
    };
  }

  private _mapRun(run: ApiRagRun): RagRun {
    return {
      id: run.id,
      createdAt: new Date(run.created_at),
      status: run.status,
      schemaId: run.schema_id,
      schemaName: run.schema_name,
      conversationId: run.conversation_id,
      messageId: run.message_id,
      prompt: run.prompt,
      generatedSql: run.generated_sql,
      error: run.error,
      durationMs: run.duration_ms,
      attemptCount: run.attempt_count,
      repairCount: run.repair_count,
      rowCount: run.row_count,
      usedContext: run.used_context,
    };
  }
}
