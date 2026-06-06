import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl, Validators } from '@angular/forms';

import { ITextField } from '@interfaces/components/text-field';
import { TextField } from './text-field';

@Component({
  template: `<talk2db-text-field [field]="field" />`,
  imports: [TextField],
})
class TestHostComponent {
  control = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required, Validators.email],
  });

  field: ITextField = {
    id: 'email',
    label: 'Correo',
    control: this.control,
    type: 'email',
    placeholder: 'nombre@ejemplo.com',
    autocomplete: 'email',
    errors: {
      required: 'El correo es obligatorio.',
      email: 'El correo no es válido.',
    },
  };
}

describe('TextField', () => {
  let fixture: ComponentFixture<TestHostComponent>;
  let host: TestHostComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    host = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('renders label and input metadata', () => {
    const label = fixture.nativeElement.querySelector('label') as HTMLLabelElement;
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;

    expect(label.textContent).toBe('Correo');
    expect(label.htmlFor).toContain('email');
    expect(input.type).toBe('email');
    expect(input.placeholder).toBe('nombre@ejemplo.com');
    expect(input.autocomplete).toBe('email');
  });

  it('does not show an error before the control is touched', () => {
    expect(fixture.nativeElement.querySelector('.field-error')).toBeNull();
  });

  it('shows configured validation error once touched', () => {
    host.control.markAsTouched();
    fixture.detectChanges();

    const error = fixture.nativeElement.querySelector('.field-error') as HTMLElement;
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;

    expect(error.textContent).toBe('El correo es obligatorio.');
    expect(input.getAttribute('aria-invalid')).toBe('true');
    expect(input.getAttribute('aria-describedby')).toBe('email-error');
  });
});
