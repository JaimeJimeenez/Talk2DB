import { TestBed } from '@angular/core/testing';
import { Router, RouterStateSnapshot, provideRouter } from '@angular/router';

import { authGuard } from './auth';

describe('authGuard', () => {
  let token: string | null;

  beforeEach(() => {
    token = null;
    vi.stubGlobal('sessionStorage', {
      getItem: vi.fn(() => token),
    });

    TestBed.configureTestingModule({
      providers: [provideRouter([])],
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('allows access when a token exists', () => {
    token = 'jwt-token';

    const result = TestBed.runInInjectionContext(() =>
      authGuard({} as never, { url: '/new-chat' } as RouterStateSnapshot),
    );

    expect(result).toBe(true);
  });

  it('redirects to login with returnUrl when the token is missing', () => {
    const router = TestBed.inject(Router);

    const result = TestBed.runInInjectionContext(() =>
      authGuard({} as never, { url: '/conversations/123' } as RouterStateSnapshot),
    );

    expect(router.serializeUrl(result as ReturnType<Router['createUrlTree']>)).toBe(
      '/login?returnUrl=%2Fconversations%2F123',
    );
  });

  it('redirects to login when the token is blank', () => {
    const router = TestBed.inject(Router);
    token = '   ';

    const result = TestBed.runInInjectionContext(() =>
      authGuard({} as never, { url: '/metrics' } as RouterStateSnapshot),
    );

    expect(router.serializeUrl(result as ReturnType<Router['createUrlTree']>)).toBe(
      '/login?returnUrl=%2Fmetrics',
    );
  });
});
