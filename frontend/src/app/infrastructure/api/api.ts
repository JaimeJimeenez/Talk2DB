import { inject, Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";

import { Observable } from "rxjs/internal/Observable";

import { environment } from "@environment/environment";

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    private readonly _apiUrl = `${environment.apiUrl}${environment.apiVersion}`;

    private _httpClient = inject(HttpClient);

    get<T>(url: string, params?: any): Observable<T> {
        return this._httpClient.get<T>(`${this._apiUrl}/${url}`, { params });
    }

    post<T>(url: string, body: any): Observable<T> {
        return this._httpClient.post<T>(`${this._apiUrl}/${url}`, body);
    }

    patch<T>(url: string, body: any): Observable<T> {
        return this._httpClient.patch<T>(`${this._apiUrl}/${url}`, body);
    }

    put<T>(url: string, body: any): Observable<T> {
        return this._httpClient.put<T>(`${this._apiUrl}/${url}`, body);
    }

    delete<T>(url: string): Observable<T> {
        return this._httpClient.delete<T>(`${this._apiUrl}/${url}`);
    }
}
