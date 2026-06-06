import { IIcon } from './icon';

export interface IDropdownItem {
  id: string;
  label: string;
}

export interface IDropdown {
  label: string;
  icon?: IIcon | null;
  items: IDropdownItem[];
  emptyLabel?: string;
}
