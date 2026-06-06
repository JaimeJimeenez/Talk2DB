import { ChangeDetectionStrategy, Component, computed, effect, input, output, signal } from '@angular/core';

import { QueryArtifact } from '@domain/models/message';
import { Icon } from '@components/icon/icon';
import { ArtifactTable } from '@components/artifact-table/artifact-table';
import { ArtifactChart } from '@components/artifact-chart/artifact-chart';
import { ArtifactSql } from '@components/artifact-sql/artifact-sql';
import { ARTIFACT_COPY_RESET_MS, ARTIFACT_ICONS } from '@constants/components/artifact';
import { ArtifactTab } from '@interfaces/components/artifact';
import { getDefaultArtifactTab, getNumericColumns, hasChartableDataset } from '@utils/artifact';

@Component({
  selector: 'talk2db-artifact',
  imports: [Icon, ArtifactTable, ArtifactChart, ArtifactSql],
  templateUrl: './artifact.html',
  styleUrl: './artifact.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Artifact {
  readonly artifact = input.required<QueryArtifact>();
  readonly closed = output<void>();

  readonly activeTab = signal<ArtifactTab>('table');
  readonly copied = signal(false);

  readonly hasRows = computed(() => this.artifact().rows.length > 0);
  readonly numericColumns = computed(() => getNumericColumns(this.artifact()));
  readonly hasChart = computed(() => hasChartableDataset(this.artifact()));

  readonly tableIcon = ARTIFACT_ICONS.table;
  readonly rowsIcon = ARTIFACT_ICONS.rows;
  readonly chartIcon = ARTIFACT_ICONS.chart;
  readonly codeIcon = ARTIFACT_ICONS.code;
  readonly copyIcon = ARTIFACT_ICONS.copy;
  readonly checkIcon = ARTIFACT_ICONS.check;
  readonly closeIcon = ARTIFACT_ICONS.close;

  constructor() {
    effect(() => {
      this.activeTab.set(getDefaultArtifactTab(this.artifact()));
    });
  }

  copySql(): void {
    const sql = this.artifact().sql;
    if (!sql) return;

    void navigator.clipboard?.writeText(sql);
    this.copied.set(true);
    setTimeout(() => this.copied.set(false), ARTIFACT_COPY_RESET_MS);
  }
}
