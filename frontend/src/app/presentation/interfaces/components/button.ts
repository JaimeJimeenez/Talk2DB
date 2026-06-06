import { IIcon } from "@interfaces/components/icon";

export type ButtonType = 'button' | 'submit';

export interface IButton {
  label?: string;
  startIcon?: IIcon;
  endIcon?: IIcon;
  onClick?: () => void;
  class?: string;
  disabled?: boolean;
  type?: ButtonType;
}
