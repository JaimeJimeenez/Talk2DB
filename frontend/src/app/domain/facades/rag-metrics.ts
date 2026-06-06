import { computed, inject, Injectable, signal } from '@angular/core';
import { finalize } from 'rxjs';

import { RagMetricsFilters, RagMetricsSummary, RagRun } from '@domain/models/rag-metrics';
import { RagMetricsPort } from '@domain/ports/rag-metrics';
import { AlertsService } from '@services/alerts';

@Injectable({ providedIn: 'root' })
export class RagMetricsFacade {
  private readonly _metrics = inject(RagMetricsPort);
  private readonly _alerts = inject(AlertsService);

  private readonly _summary = signal<RagMetricsSummary | null>(null);
  private readonly _failedRuns = signal<RagRun[]>([]);
  private readonly _isLoading = signal(false);

  readonly summary = this._summary.asReadonly();
  readonly failedRuns = this._failedRuns.asReadonly();
  readonly isLoading = this._isLoading.asReadonly();
  readonly hasData = computed(() => (this._summary()?.totalRuns ?? 0) > 0);

  load(filters: RagMetricsFilters = {}): void {
    this._isLoading.set(true);
    this._metrics.getSummary(filters)
      .pipe(finalize(() => this._isLoading.set(false)))
      .subscribe({
        next: summary => this._summary.set(summary),
        error: () => this._alerts.error('Error', 'No se han podido cargar las métricas del RAG.'),
      });

    this._metrics.getRuns({ ...filters, status: 'error', limit: 25 }).subscribe({
      next: runs => this._failedRuns.set(runs),
      error: () => this._alerts.error('Error', 'No se han podido cargar las ejecuciones fallidas.'),
    });
  }
}
