import { Observable } from 'rxjs';

import { RagMetricsFilters, RagMetricsSummary, RagRun, RagRunStatus } from '@domain/models/rag-metrics';

export abstract class RagMetricsPort {
  abstract getSummary(filters?: RagMetricsFilters): Observable<RagMetricsSummary>;
  abstract getRuns(filters?: RagMetricsFilters & { readonly limit?: number; readonly status?: RagRunStatus }): Observable<RagRun[]>;
}
