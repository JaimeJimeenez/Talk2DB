import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { environment } from '@environment/environment';

import { tokenInterceptor } from './token';

describe('tokenInterceptor', () => {
  let httpClient: HttpClient;
  let http: HttpTestingController;
  let token: string | null;
  const baseUrl = `${environment.apiUrl}${environment.apiVersion}`;

  beforeEach(() => {
    token = null;
    vi.stubGlobal('sessionStorage', {
      getItem: vi.fn(() => token),
    });

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([tokenInterceptor])),
        provideHttpClientTesting(),
      ],
    });

    httpClient = TestBed.inject(HttpClient);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify();
    vi.unstubAllGlobals();
  });

  it('adds bearer token to protected api requests', () => {
    token = 'token-123';

    httpClient.get(`${baseUrl}/conversations`).subscribe();

    const request = http.expectOne(`${baseUrl}/conversations`);

    expect(request.request.headers.get('Authorization')).toBe('Bearer token-123');
    request.flush([]);
  });

  it('adds bearer token to completion requests', () => {
    token = 'token-123';

    httpClient.post(`${baseUrl}/rag/completion`, {
      conversation_id: 'conversation-1',
      prompt: 'show users',
      schema_id: 'schema-1',
    }).subscribe();

    const request = http.expectOne(`${baseUrl}/rag/completion`);

    expect(request.request.headers.get('Authorization')).toBe('Bearer token-123');
    request.flush({});
  });

  it('does not add bearer token when jwt is missing', () => {
    httpClient.get(`${baseUrl}/conversations`).subscribe();

    const request = http.expectOne(`${baseUrl}/conversations`);

    expect(request.request.headers.has('Authorization')).toBe(false);
    request.flush([]);
  });

  it('does not add bearer token to login or signup requests', () => {
    token = 'token-123';

    httpClient.post(`${baseUrl}/auth/login`, {}).subscribe();
    httpClient.post(`${baseUrl}/auth/signup`, {}).subscribe();

    const loginRequest = http.expectOne(`${baseUrl}/auth/login`);
    const signupRequest = http.expectOne(`${baseUrl}/auth/signup`);

    expect(loginRequest.request.headers.has('Authorization')).toBe(false);
    expect(signupRequest.request.headers.has('Authorization')).toBe(false);
    loginRequest.flush({});
    signupRequest.flush({});
  });
});
