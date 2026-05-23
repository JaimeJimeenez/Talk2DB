import { ChangeDetectionStrategy, Component, inject } from '@angular/core';

import { AlertsService } from '@services/alerts';

import { ALERT_ICONS, CROSS_ICON } from '@constants/components/alerts';

import { AlertType } from '@interfaces/components/alerts';
import { IIcon } from '@interfaces/components/icon';

import { Icon } from '@components/icon/icon';

@Component({
  selector: 'talk2db-alerts',
  imports: [Icon],
  templateUrl: './alerts.html',
  styleUrl: './alerts.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Alerts {
  private readonly _alerts = inject(AlertsService);

  readonly alerts = this._alerts.alerts;
  readonly crossIcon = { ...CROSS_ICON };

  dismiss(id: string): void {
    this._alerts.dismiss(id);
  }

  icon(type: AlertType): IIcon {
    return ALERT_ICONS[type];
  }
}
