import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'talk2db-question',
  imports: [],
  templateUrl: './question.html',
  styleUrl: './question.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Question {
  readonly content = input.required<string>();
}
