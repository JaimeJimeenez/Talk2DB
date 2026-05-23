import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { UserFacade } from '@domain/facades/user';
import { Button } from "@components/button/button";
import { SIGNUP_BUTTON } from '@constants/pages/signup';
import { TextField } from '@components/text-field/text-field';
import { ITextField } from '@interfaces/components/text-field';
import { AuthCard } from '@components/auth-card/auth-card';

@Component({
  selector: 'talk2db-signup',
  imports: [ReactiveFormsModule, Button, TextField, AuthCard, RouterLink],
  templateUrl: './signup.html',
  styleUrl: './signup.scss',
})
export class Signup {

  private readonly _user = inject(UserFacade);

  readonly username = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required, Validators.minLength(8), Validators.maxLength(16)],
  });
  readonly email = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required, Validators.email],
  });
  readonly password = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required, Validators.minLength(8), Validators.maxLength(20)],
  });

  readonly signupForm = new FormGroup({
    username: this.username,
    email: this.email,
    password: this.password,
  });

  readonly fields: ITextField[] = [
    {
      id: 'username',
      label: 'Nombre completo',
      control: this.username,
      placeholder: 'Ej. Juan Pérez',
      autocomplete: 'name',
      errors: {
        required: 'Introduce tu nombre.',
        minlength: 'Debe tener al menos 8 caracteres.',
        maxlength: 'No puede superar 16 caracteres.',
      },
    },
    {
      id: 'email',
      label: 'Correo electrónico',
      control: this.email,
      type: 'email',
      placeholder: 'nombre@ejemplo.com',
      autocomplete: 'email',
      errors: {
        required: 'Introduce tu correo electrónico.',
        email: 'Introduce un correo válido.',
      },
    },
    {
      id: 'password',
      label: 'Contraseña',
      control: this.password,
      type: 'password',
      placeholder: '••••••••',
      autocomplete: 'new-password',
      errors: {
        required: 'Introduce una contraseña.',
        minlength: 'Debe tener al menos 8 caracteres.',
        maxlength: 'No puede superar 20 caracteres.',
      },
    },
  ];

  signupButton() {
    return {
      ...SIGNUP_BUTTON,
      disabled: this.signupForm.invalid || this._user.isLoading(),
    };
  }

  public onSubmit(): void {
    if (this.signupForm.invalid) {
      this.signupForm.markAllAsTouched();
      return;
    }

    this._user.signup(this.username.value, this.email.value, this.password.value);
  }
}
