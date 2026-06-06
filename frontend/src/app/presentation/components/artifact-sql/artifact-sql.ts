import { ChangeDetectionStrategy, Component, input, signal } from '@angular/core';

import { Icon } from '@components/icon/icon';

@Component({
  selector: 'talk2db-artifact-sql',
  imports: [Icon],
  templateUrl: './artifact-sql.html',
  styleUrl: './artifact-sql.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ArtifactSql {
  readonly sql = input.required<string>();
  readonly copied = signal(false);

  readonly copyIcon = { name: 'copy', size: 15, title: 'Copiar SQL' };
  readonly checkIcon = { name: 'check', size: 15, title: 'Copiado' };

  copy(): void {
    void navigator.clipboard?.writeText(this.sql());
    this.copied.set(true);
    setTimeout(() => this.copied.set(false), 1600);
  }
}
