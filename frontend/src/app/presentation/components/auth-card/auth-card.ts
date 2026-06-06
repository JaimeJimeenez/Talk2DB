import { ChangeDetectionStrategy, Component, input } from '@angular/core';

@Component({
  selector: 'talk2db-auth-card',
  imports: [],
  templateUrl: './auth-card.html',
  styleUrl: './auth-card.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AuthCard {
  readonly title = input.required<string>();
  readonly subtitle = input<string>('');
}
