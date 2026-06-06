import { QueryArtifact, QueryArtifactColumn } from '@domain/models/message';
import { ArtifactChartDataset, ArtifactTab } from '@interfaces/components/artifact';

export function getNumericColumns(artifact: QueryArtifact): QueryArtifactColumn[] {
  return artifact.columns.filter(column => isNumericColumn(artifact, column.name));
}

export function hasChartableDataset(artifact: QueryArtifact): boolean {
  return buildArtifactChartDataset(artifact) !== null;
}

export function getDefaultArtifactTab(artifact: QueryArtifact): ArtifactTab {
  if (artifact.rows.length > 0) return 'table';
  if (hasChartableDataset(artifact)) return 'chart';
  if (artifact.sql) return 'sql';
  return 'table';
}

export function buildArtifactChartDataset(artifact: QueryArtifact): ArtifactChartDataset | null {
  const valueColumn = getNumericColumns(artifact)[0];
  if (!valueColumn) return null;

  const labelColumn = artifact.columns.find(column =>
    column.name !== valueColumn.name &&
    artifact.rows.some(row => isChartLabel(row[column.name])),
  ) ?? null;

  return {
    labels: artifact.rows.map((row, index) => String(labelColumn ? row[labelColumn.name] : index + 1)),
    values: artifact.rows.map(row => Number(row[valueColumn.name] ?? 0)),
    valueColumn,
    labelColumn,
  };
}

function isNumericColumn(artifact: QueryArtifact, columnName: string): boolean {
  return artifact.rows.some(row => typeof row[columnName] === 'number');
}

function isChartLabel(value: unknown): boolean {
  return ['string', 'number'].includes(typeof value);
}
