import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { LucideDynamicIcon } from '@lucide/angular';

import { IIcon } from '@interfaces/components/icon';

@Component({
  selector: 'talk2db-icon',
  imports: [LucideDynamicIcon],
  templateUrl: './icon.html',
  styleUrl: './icon.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Icon {
  readonly icon = input<IIcon | null>(null);
} 