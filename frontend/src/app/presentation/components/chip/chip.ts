import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'talk2db-chip',
  imports: [],
  templateUrl: './chip.html',
  styleUrl: './chip.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Chip {
  readonly label = input.required<string>();
}
