import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { UserAdapter } from './user';
import { ApiService } from '@infrastructure/api/api';

describe('UserAdapter', () => {
  let adapter: UserAdapter;
  let api: { post: ReturnType<typeof vi.fn> };

  beforeEach(() => {
    api = {
      post: vi.fn().mockReturnValue(of({
        access_token: 'jwt-token',
        token_type: 'bearer',
      })),
    };

    TestBed.configureTestingModule({
      providers: [
        UserAdapter,
        { provide: ApiService, useValue: api },
      ],
    });

    adapter = TestBed.inject(UserAdapter);
  });

  it('sends signup payload to the auth endpoint', () => {
    adapter.signup('demo_user', 'demo@example.com', 'password123').subscribe(user => {
      expect(user.token).toBe('jwt-token');
      expect(user.username).toBe('demo_user');
      expect(user.email).toBe('demo@example.com');
    });

    expect(api.post).toHaveBeenCalledWith('auth/signup', {
      username: 'demo_user',
      email: 'demo@example.com',
      password: 'password123',
    });
  });

  it('sends login payload to the auth endpoint', () => {
    adapter.login('demo@example.com', 'password123').subscribe(user => {
      expect(user.token).toBe('jwt-token');
      expect(user.email).toBe('demo@example.com');
    });

    expect(api.post).toHaveBeenCalledWith('auth/login', {
      email: 'demo@example.com',
      password: 'password123',
    });
  });
});
