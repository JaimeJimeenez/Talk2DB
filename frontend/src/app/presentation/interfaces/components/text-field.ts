import { FormControl } from '@angular/forms';

export type TextFieldType = 'email' | 'password' | 'search' | 'tel' | 'text' | 'url';

export interface ITextField {
  readonly id: string;
  readonly label: string;
  readonly control: FormControl<string>;
  readonly type?: TextFieldType;
  readonly placeholder?: string;
  readonly autocomplete?: string;
  readonly errors?: Partial<Record<string, string>>;
}
