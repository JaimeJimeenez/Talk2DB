import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import { UserFacade } from './user';
import { UserPort } from '@domain/ports/user';
import { AlertsService } from '@services/alerts';
import { User } from '@domain/models/user';

describe('UserFacade', () => {
  let facade: UserFacade;
  let userPort: {
    signup: ReturnType<typeof vi.fn>;
    login: ReturnType<typeof vi.fn>;
  };
  let alerts: {
    success: ReturnType<typeof vi.fn>;
    error: ReturnType<typeof vi.fn>;
  };
  let router: { navigate: ReturnType<typeof vi.fn> };
  let token: string | null;

  const user: User = {
    id: 'user-1',
    username: 'demo_user',
    email: 'demo@example.com',
    token: 'jwt-token',
  };

  beforeEach(() => {
    token = null;
    vi.stubGlobal('localStorage', {
      setItem: vi.fn((_key: string, value: string) => {
        token = value;
      }),
      getItem: vi.fn(() => token),
    });

    userPort = {
      signup: vi.fn().mockReturnValue(of(user)),
      login: vi.fn().mockReturnValue(of(user)),
    };
    alerts = {
      success: vi.fn(),
      error: vi.fn(),
    };
    router = {
      navigate: vi.fn(),
    };

    TestBed.configureTestingModule({
      providers: [
        UserFacade,
        { provide: UserPort, useValue: userPort },
        { provide: AlertsService, useValue: alerts },
        { provide: Router, useValue: router },
      ],
    });

    facade = TestBed.inject(UserFacade);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('signs up users and shows a success alert', () => {
    facade.signup('demo_user', 'demo@example.com', 'password123');

    expect(userPort.signup).toHaveBeenCalledWith('demo_user', 'demo@example.com', 'password123');
    expect(facade.currentUser()).toEqual(user);
    expect(alerts.success).toHaveBeenCalledWith('Cuenta creada', 'Tu usuario se ha creado correctamente.');
  });

  it('logs in users, stores token and navigates to chat', () => {
    facade.login('demo@example.com', 'password123');

    expect(userPort.login).toHaveBeenCalledWith('demo@example.com', 'password123');
    expect(token).toBe('jwt-token');
    expect(facade.currentUser()).toEqual(user);
    expect(alerts.success).toHaveBeenCalledWith('Sesión iniciada', 'Bienvenido de nuevo.');
    expect(router.navigate).toHaveBeenCalledWith(['/chat']);
  });

  it('shows an error alert when login fails', () => {
    userPort.login.mockReturnValueOnce(throwError(() => new Error('invalid')));

    facade.login('demo@example.com', 'wrong');

    expect(alerts.error).toHaveBeenCalledWith('No se pudo iniciar sesión', 'Revisa tu correo y contraseña.');
    expect(router.navigate).not.toHaveBeenCalled();
    expect(token).toBeNull();
  });
});
