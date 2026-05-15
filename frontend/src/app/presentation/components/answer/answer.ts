import { ChangeDetectionStrategy, Component, input } from '@angular/core';

import { Icon } from '@components/icon/icon';

@Component({
  selector: 'talk2db-answer',
  imports: [Icon],
  templateUrl: './answer.html',
  styleUrl: './answer.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Answer {
  readonly content = input.required<string>();
  readonly timestamp = input<Date>();

  readonly botIcon = { name: 'bot', size: 20, title: 'AI Assistant' };
}
