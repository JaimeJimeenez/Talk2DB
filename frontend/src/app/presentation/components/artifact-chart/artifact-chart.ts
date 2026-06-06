import {
  AfterViewInit,
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  effect,
  inject,
  input,
  viewChild,
} from '@angular/core';
import * as echarts from 'echarts';

import { QueryArtifact } from '@domain/models/message';
import { ARTIFACT_CHART_COLOR } from '@constants/components/artifact';
import { buildArtifactChartDataset } from '@utils/artifact';

@Component({
  selector: 'talk2db-artifact-chart',
  imports: [],
  templateUrl: './artifact-chart.html',
  styleUrl: './artifact-chart.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ArtifactChart implements AfterViewInit {
  readonly artifact = input.required<QueryArtifact>();

  private readonly _destroyRef = inject(DestroyRef);
  private readonly _chartElement = viewChild<ElementRef<HTMLDivElement>>('chart');
  private _chart: echarts.ECharts | null = null;

  constructor() {
    effect(() => {
      this.artifact();
      this._render();
    });
  }

  ngAfterViewInit(): void {
    this._chart = echarts.init(this._chartElement()!.nativeElement, undefined, { renderer: 'svg' });
    this._render();

    const resize = () => this._chart?.resize();
    window.addEventListener('resize', resize);
    this._destroyRef.onDestroy(() => {
      window.removeEventListener('resize', resize);
      this._chart?.dispose();
    });
  }

  private _render(): void {
    if (!this._chart) return;

    const dataset = buildArtifactChartDataset(this.artifact());
    if (!dataset) return;

    this._chart.setOption({
      color: [ARTIFACT_CHART_COLOR],
      tooltip: { trigger: 'axis' },
      grid: { left: 42, right: 18, top: 28, bottom: 48 },
      xAxis: {
        type: 'category',
        data: dataset.labels,
        axisLabel: { color: '#777587', interval: 0, rotate: dataset.labels.length > 6 ? 30 : 0 },
        axisLine: { lineStyle: { color: '#c7c4d8' } },
      },
      yAxis: {
        type: 'value',
        axisLabel: { color: '#777587' },
        splitLine: { lineStyle: { color: '#efeeec' } },
      },
      series: [
        {
          name: dataset.valueColumn.name,
          type: 'bar',
          data: dataset.values,
          barMaxWidth: 42,
          itemStyle: { borderRadius: [6, 6, 0, 0] },
        },
      ],
    });
  }
}
