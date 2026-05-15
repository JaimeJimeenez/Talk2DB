import { ChangeDetectionStrategy, Component, input } from '@angular/core';

import { IButton } from '@interfaces/components/button';
import { Icon } from "@components/icon/icon";

@Component({
  selector: 'talk2db-button',
  imports: [Icon],
  templateUrl: './button.html',
  styleUrl: './button.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Button {
  readonly button = input<IButton | null>(null);
}
