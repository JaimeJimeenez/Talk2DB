import { Injectable, signal } from '@angular/core';

import { IAlert, AlertType } from '@interfaces/components/alerts';

@Injectable({ providedIn: 'root' })
export class AlertsService {
  private readonly _alerts = signal<IAlert[]>([]);

  readonly alerts = this._alerts.asReadonly();

  success(title: string, message?: string): void {
    this._show('success', title, message);
  }

  info(title: string, message?: string): void {
    this._show('info', title, message);
  }

  warning(title: string, message?: string): void {
    this._show('warning', title, message);
  }

  error(title: string, message?: string): void {
    this._show('error', title, message);
  }

  dismiss(id: string): void {
    this._alerts.update(alerts => alerts.filter(alert => alert.id !== id));
  }

  private _show(type: AlertType, title: string, message?: string): void {
    const alert: IAlert = {
      id: crypto.randomUUID(),
      type,
      title,
      message,
    };

    this._alerts.update(alerts => [alert, ...alerts].slice(0, 4));
    window.setTimeout(() => this.dismiss(alert.id), 5000);
  }

}