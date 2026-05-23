import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { AuthCard } from '@components/auth-card/auth-card';
import { Button } from '@components/button/button';
import { TextField } from '@components/text-field/text-field';
import { UserFacade } from '@domain/facades/user';
import { ITextField } from '@interfaces/components/text-field';
import { LOGIN_BUTTON } from '@constants/pages/login';

@Component({
  selector: 'talk2db-login',
  imports: [AuthCard, Button, ReactiveFormsModule, RouterLink, TextField],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  private readonly _user = inject(UserFacade);

  readonly email = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required, Validators.email],
  });
  readonly password = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required],
  });

  readonly loginForm = new FormGroup({
    email: this.email,
    password: this.password,
  });

  readonly fields: ITextField[] = [
    {
      id: 'login-email',
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
      id: 'login-password',
      label: 'Contraseña',
      control: this.password,
      type: 'password',
      placeholder: '••••••••',
      autocomplete: 'current-password',
      errors: {
        required: 'Introduce tu contraseña.',
      },
    },
  ];

  loginButton() {
    return {
      ...LOGIN_BUTTON,
      disabled: this.loginForm.invalid || this._user.isLoading(),
    };
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this._user.login(this.email.value, this.password.value);
  }
}
