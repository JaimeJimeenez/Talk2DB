import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { ApiService } from './api';
import { environment } from '@environment/environment';

describe('ApiService', () => {
  let service: ApiService;
  let http: HttpTestingController;
  const baseUrl = `${environment.apiUrl}${environment.apiVersion}`;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ApiService,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });

    service = TestBed.inject(ApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
  });

  it('sends get requests to the configured api url', () => {
    service.get('conversations').subscribe();

    const request = http.expectOne(`${baseUrl}/conversations`);

    expect(request.request.method).toBe('GET');
    expect(request.request.headers.has('Authorization')).toBe(false);
    request.flush([]);
  });

  it('sends post requests with the provided body', () => {
    service.post('auth/signup', { username: 'demo' }).subscribe();

    const request = http.expectOne(`${baseUrl}/auth/signup`);

    expect(request.request.method).toBe('POST');
    expect(request.request.headers.has('Authorization')).toBe(false);
    expect(request.request.body).toEqual({ username: 'demo' });
    request.flush({});
  });
});
