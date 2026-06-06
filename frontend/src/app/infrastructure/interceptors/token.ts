import { HttpInterceptorFn } from '@angular/common/http';

const TOKEN_STORAGE_KEY = 'talk2db_jwt';
const AUTH_EXCLUDED_PATHS = ['/auth/login', '/auth/signup'];

export const tokenInterceptor: HttpInterceptorFn = (request, next) => {
  const token = globalThis.sessionStorage?.getItem(TOKEN_STORAGE_KEY);
  const isAuthRequest = AUTH_EXCLUDED_PATHS.some(path => request.url.includes(path));

  if (!token || isAuthRequest) {
    return next(request);
  }

  return next(request.clone({
    setHeaders: {
      Authorization: `Bearer ${token}`,
    },
  }));
};
