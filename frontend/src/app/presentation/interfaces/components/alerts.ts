export type AlertType = 'success' | 'error' | 'warning' | 'info';

export interface IAlert {
    readonly id: string;
    readonly type: AlertType;
    readonly title: string;
    readonly message?: string;
}