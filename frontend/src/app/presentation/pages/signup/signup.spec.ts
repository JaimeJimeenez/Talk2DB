import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';

import { Signup } from './signup';
import { UserPort } from '@domain/ports/user';

describe('Signup', () => {
  let component: Signup;
  let fixture: ComponentFixture<Signup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Signup],
      providers: [
        {
          provide: UserPort,
          useValue: {
            signup: vi.fn().mockReturnValue(of({
              id: 'user-1',
              username: 'demo_user',
              email: 'demo@example.com',
              token: 'token',
            })),
            login: vi.fn(),
          },
        },
        provideRouter([]),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Signup);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
