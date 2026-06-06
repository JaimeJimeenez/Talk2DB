import { IIcon } from '@interfaces/components/icon';
import { AlertType } from '@interfaces/components/alerts';

export const CROSS_ICON: IIcon = {
    name: 'x',
    size: 16,
    strokeWidth: 2,
    title: 'Close'
}

export const ERROR_ICON: IIcon = {
    name: 'circle-x',
    size: 16,
    strokeWidth: 2,
    title: 'Error'
}

export const WARNING_ICON: IIcon = {
    name: 'alert-triangle',
    size: 16,
    strokeWidth: 2,
    title: 'Warning'
}

export const INFO_ICON: IIcon = {
    name: 'info',
    size: 16,
    strokeWidth: 2,
    title: 'Information'
}

export const SUCCESS_ICON: IIcon = {
    name: 'badge-check',
    size: 16,
    strokeWidth: 2,
    title: 'Success'
}

export const ALERT_ICONS: Record<AlertType, IIcon> = {
    success: SUCCESS_ICON,
    info: INFO_ICON,
    warning: WARNING_ICON,
    error: ERROR_ICON,
};
