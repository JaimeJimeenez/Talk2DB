import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';

import { ITextField } from '@interfaces/components/text-field';

@Component({
  selector: 'talk2db-text-field',
  imports: [ReactiveFormsModule],
  templateUrl: './text-field.html',
  styleUrl: './text-field.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TextField {
  readonly field = input.required<ITextField>();

  error(): string | null {
    const control = this.field().control;
    if (!control.invalid || (!control.dirty && !control.touched)) return null;

    const errors = control.errors ?? {};
    const messages = this.field().errors ?? {};
    const firstKey = Object.keys(errors)[0];

    return firstKey ? messages[firstKey] ?? 'El campo no es válido.' : null;
  }
}
