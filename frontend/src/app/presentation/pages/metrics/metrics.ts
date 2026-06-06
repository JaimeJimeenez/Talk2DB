import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { RagMetricsFacade } from '@domain/facades/rag-metrics';
import { RagMetricBucket, RagMetricPoint, RagSchemaMetric } from '@domain/models/rag-metrics';

@Component({
  selector: 'talk2db-metrics',
  imports: [FormsModule],
  templateUrl: './metrics.html',
  styleUrl: './metrics.scss',
})
export class Metrics implements OnInit {
  private readonly _facade = inject(RagMetricsFacade);

  readonly from = signal('');
  readonly to = signal('');
  readonly schemaId = signal('');
  readonly summary = this._facade.summary;
  readonly failedRuns = this._facade.failedRuns;
  readonly isLoading = this._facade.isLoading;
  readonly hasData = this._facade.hasData;

  readonly schemaOptions = computed<RagSchemaMetric[]>(() => this.summary()?.runsBySchema ?? []);

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this._facade.load({
      from: this.from() || undefined,
      to: this.to() || undefined,
      schemaId: this.schemaId() || undefined,
    });
  }

  formatPercent(value: number): string {
    return `${Math.round(value * 100)}%`;
  }

  formatMs(value: number): string {
    if (value >= 1000) return `${(value / 1000).toFixed(1)}s`;
    return `${Math.round(value)}ms`;
  }

  maxRunCount(points: RagMetricPoint[]): number {
    return Math.max(1, ...points.map(point => point.total));
  }

  maxLatency(points: RagMetricPoint[]): number {
    return Math.max(1, ...points.map(point => point.averageDurationMs));
  }

  maxBucketCount(points: RagMetricBucket[]): number {
    return Math.max(1, ...points.map(point => point.count));
  }

  maxSchemaCount(points: RagSchemaMetric[]): number {
    return Math.max(1, ...points.map(point => point.count));
  }

  barHeight(value: number, max: number): string {
    return `${Math.max(4, Math.round((value / max) * 100))}%`;
  }

  barWidth(value: number, max: number): string {
    return `${Math.max(2, Math.round((value / max) * 100))}%`;
  }

  trackByLabel(_: number, item: { readonly label: string }): string {
    return item.label;
  }

  trackBySchema(_: number, item: RagSchemaMetric): string {
    return item.schemaId;
  }
}
