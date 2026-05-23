import { inject, Injectable } from "@angular/core";

import { Observable } from "rxjs/internal/Observable";

import { User } from "@domain/models/user";
import { ApiService } from "@infrastructure/api/api";

@Injectable()
export class UserAdapter {

    private readonly _http = inject(ApiService);
    
    signup(username: string, email: string, password: string): Observable<User> {
        return this._http.post<User>('auth/signup', { username, email, password });
    }

    login(email: string, password: string): Observable<User> {
        return this._http.post<User>('auth/login', { email, password });
    }
}
