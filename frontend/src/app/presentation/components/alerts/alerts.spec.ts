import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideLucideIcons, LucideBadgeCheck, LucideCircleX, LucideInfo, LucideTriangleAlert, LucideX } from '@lucide/angular';

import { Alerts } from './alerts';
import { AlertsService } from '@services/alerts';

describe('Alerts', () => {
  let fixture: ComponentFixture<Alerts>;
  let component: Alerts;
  let service: AlertsService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Alerts],
      providers: [
        provideLucideIcons(
          LucideBadgeCheck,
          LucideCircleX,
          LucideInfo,
          LucideTriangleAlert,
          LucideX,
        ),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Alerts);
    component = fixture.componentInstance;
    service = TestBed.inject(AlertsService);
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('renders alerts from the service', () => {
    service.success('Guardado', 'Los cambios se guardaron.');
    fixture.detectChanges();

    const alert = fixture.nativeElement.querySelector('.alert-success') as HTMLElement;

    expect(alert).toBeTruthy();
    expect(alert.textContent).toContain('Guardado');
    expect(alert.textContent).toContain('Los cambios se guardaron.');
  });

  it('dismisses alerts from the close button', () => {
    service.error('Algo falló');
    fixture.detectChanges();

    const close = fixture.nativeElement.querySelector('.alert-close') as HTMLButtonElement;
    close.click();
    fixture.detectChanges();

    expect(service.alerts()).toEqual([]);
    expect(fixture.nativeElement.querySelector('.alert')).toBeNull();
  });
});
