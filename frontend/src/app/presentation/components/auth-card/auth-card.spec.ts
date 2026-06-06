import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AuthCard } from './auth-card';

@Component({
  template: `
    <talk2db-auth-card title="Acceso" subtitle="Entra en tu cuenta">
      <form auth-card-form>Formulario</form>
      <p auth-card-footer>Footer</p>
    </talk2db-auth-card>
  `,
  imports: [AuthCard],
})
class TestHostComponent {}

describe('AuthCard', () => {
  let fixture: ComponentFixture<TestHostComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestHostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('renders title, subtitle and projected content', () => {
    const element = fixture.nativeElement as HTMLElement;

    expect(element.querySelector('h2')?.textContent).toBe('Acceso');
    expect(element.querySelector('.card-header p')?.textContent).toBe('Entra en tu cuenta');
    expect(element.querySelector('form')?.textContent).toContain('Formulario');
    expect(element.querySelector('.auth-footer')?.textContent).toContain('Footer');
  });
});
