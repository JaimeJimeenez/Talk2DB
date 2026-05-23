import { inject, Injectable, signal } from "@angular/core";
import { Router } from "@angular/router";
import { User } from "@domain/models/user";

import { UserPort } from "@domain/ports/user";
import { AlertsService } from "@services/alerts";

@Injectable({ providedIn: 'root' })
export class UserFacade {
    private readonly _user = inject(UserPort);
    private readonly _alerts = inject(AlertsService);
    private readonly _router = inject(Router);

    private readonly _isLoading = signal<boolean>(false);
    private readonly _currentUser = signal<User | null>(null);

    readonly isLoading = this._isLoading.asReadonly();
    readonly currentUser = this._currentUser.asReadonly();

    signup(username: string, email: string, password: string) {
        this._isLoading.set(true);
        this._user.signup(username, email, password).subscribe({
            next: (user) => {
                this._isLoading.set(false);
                this._currentUser.set(user);
                this._alerts.success('Cuenta creada', 'Tu usuario se ha creado correctamente.');
            },
            error: () => {
                this._isLoading.set(false);
                this._alerts.error('No se pudo crear la cuenta', 'Revisa los datos e inténtalo de nuevo.');
            },
        });
    }

    login(email: string, password: string): void {
        this._isLoading.set(true);
        this._user.login(email, password).subscribe({
            next: (user) => {
                globalThis.localStorage?.setItem('talk2db_jwt', user.token);
                this._currentUser.set(user);
                this._isLoading.set(false);
                this._alerts.success('Sesión iniciada', 'Bienvenido de nuevo.');
                this._router.navigate(['/chat']);
            },
            error: () => {
                this._isLoading.set(false);
                this._alerts.error('No se pudo iniciar sesión', 'Revisa tu correo y contraseña.');
            },
        });
    }
}
