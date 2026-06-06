import { IIcon } from '@interfaces/components/icon';

export const ARTIFACT_COPY_RESET_MS = 1600;

export const ARTIFACT_ICONS: Record<
  'table' | 'rows' | 'chart' | 'code' | 'copy' | 'check' | 'close',
  IIcon
> = {
  table: { name: 'table', size: 20, title: 'Tabla' },
  rows: { name: 'rows-3', size: 16, title: 'Tabla' },
  chart: { name: 'bar-chart-3', size: 16, title: 'Gráfico' },
  code: { name: 'code-2', size: 16, title: 'SQL' },
  copy: { name: 'copy', size: 16, title: 'Copiar SQL' },
  check: { name: 'check', size: 16, title: 'Copiado' },
  close: { name: 'x', size: 18, title: 'Cerrar' },
};

export const ARTIFACT_CHART_COLOR = '#3525cd';
