import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';

import { QueryArtifact } from '@domain/models/message';
import { Icon } from '@components/icon/icon';
import { hasChartableDataset } from '@utils/artifact';

@Component({
  selector: 'talk2db-artifact-link',
  imports: [Icon],
  templateUrl: './artifact-link.html',
  styleUrl: './artifact-link.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ArtifactLink {
  readonly artifact = input.required<QueryArtifact>();
  readonly selected = output<QueryArtifact>();

  readonly tableIcon = { name: 'table', size: 19, title: 'Resultado' };
  readonly chartIcon = { name: 'bar-chart-3', size: 19, title: 'Gráfico' };
  readonly arrowIcon = { name: 'arrow-right', size: 18, title: 'Abrir' };

  hasChart(): boolean {
    return hasChartableDataset(this.artifact());
  }
}
