import { ChangeDetectionStrategy, Component, input } from '@angular/core';

import { QueryArtifact } from '@domain/models/message';

@Component({
  selector: 'talk2db-artifact-table',
  imports: [],
  templateUrl: './artifact-table.html',
  styleUrl: './artifact-table.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ArtifactTable {
  readonly artifact = input.required<QueryArtifact>();

  formatValue(value: unknown): string {
    if (value === null || value === undefined) return 'NULL';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  }
}
