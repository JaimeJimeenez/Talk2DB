import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

const TOKEN_STORAGE_KEY = 'talk2db_jwt';

export const authGuard: CanActivateFn = (_route, state) => {
  const token = globalThis.sessionStorage?.getItem(TOKEN_STORAGE_KEY)?.trim();

  if (token) {
    return true;
  }

  return inject(Router).createUrlTree(['/login'], {
    queryParams: {
      returnUrl: state.url,
    },
  });
};
