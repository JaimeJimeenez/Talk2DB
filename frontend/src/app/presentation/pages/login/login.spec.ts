import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { Login } from './login';
import { UserFacade } from '@domain/facades/user';

describe('Login', () => {
  let component: Login;
  let fixture: ComponentFixture<Login>;
  let userFacade: {
    login: ReturnType<typeof vi.fn>;
  };

  beforeEach(async () => {
    userFacade = {
      login: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [Login],
      providers: [
        provideRouter([]),
        { provide: UserFacade, useValue: userFacade },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Login);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('renders reusable text fields', () => {
    fixture.detectChanges();

    const fields = fixture.nativeElement.querySelectorAll('talk2db-text-field');

    expect(fields.length).toBe(2);
  });

  it('keeps submit disabled while the form is invalid', () => {
    expect(component.loginButton().disabled).toBe(true);
  });

  it('calls facade when submitting a valid form', () => {
    component.email.setValue('demo@example.com');
    component.password.setValue('password123');

    component.onSubmit();

    expect(userFacade.login).toHaveBeenCalledWith('demo@example.com', 'password123');
  });
});
