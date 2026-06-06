import { TestBed } from '@angular/core/testing';

import { AlertsService } from './alerts';

describe('AlertsService', () => {
  let service: AlertsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AlertsService);
  });

  it('adds success alerts', () => {
    service.success('Cuenta creada', 'Todo listo.');

    expect(service.alerts()).toEqual([
      expect.objectContaining({
        type: 'success',
        title: 'Cuenta creada',
        message: 'Todo listo.',
      }),
    ]);
  });

  it('dismisses alerts by id', () => {
    service.error('Error');
    const [alert] = service.alerts();

    service.dismiss(alert.id);

    expect(service.alerts()).toEqual([]);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('auto dismisses alerts after five seconds', () => {
    vi.useFakeTimers();

    service.info('Procesando');

    vi.advanceTimersByTime(5000);

    expect(service.alerts()).toEqual([]);
  });

  it('keeps only the four latest alerts', () => {
    service.info('1');
    service.info('2');
    service.info('3');
    service.info('4');
    service.info('5');

    expect(service.alerts().map(alert => alert.title)).toEqual(['5', '4', '3', '2']);
  });
});
