import { QueryArtifactColumn } from '@domain/models/message';

export type ArtifactTab = 'table' | 'chart' | 'sql';

export interface ArtifactChartDataset {
  readonly labels: string[];
  readonly values: number[];
  readonly valueColumn: QueryArtifactColumn;
  readonly labelColumn: QueryArtifactColumn | null;
}
