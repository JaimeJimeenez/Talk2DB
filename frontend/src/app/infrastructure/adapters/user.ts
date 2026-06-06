import { inject, Injectable } from "@angular/core";

import { Observable } from "rxjs/internal/Observable";
import { map } from "rxjs";

import { User } from "@domain/models/user";
import { ApiService } from "@infrastructure/api/api";

type AuthTokenResponse = {
    readonly access_token: string;
    readonly token_type: string;
};

@Injectable()
export class UserAdapter {

    private readonly _http = inject(ApiService);
    
    signup(username: string, email: string, password: string): Observable<User> {
        return this._http.post<AuthTokenResponse>('auth/signup', { username, email, password }).pipe(
            map(response => this._toUser(response, username, email)),
        );
    }

    login(email: string, password: string): Observable<User> {
        return this._http.post<AuthTokenResponse>('auth/login', { email, password }).pipe(
            map(response => this._toUser(response, '', email)),
        );
    }

    private _toUser(response: AuthTokenResponse, username: string, email: string): User {
        return {
            id: '',
            username,
            email,
            token: response.access_token,
        };
    }
}
