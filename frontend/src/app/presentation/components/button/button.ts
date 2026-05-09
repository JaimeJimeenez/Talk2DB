import { Component, Input } from '@angular/core';

import { IButton } from '@interfaces/components/button';
import { Icon } from "@components/icon/icon";

@Component({
  selector: 'talk2db-button',
  imports: [Icon],
  templateUrl: './button.html',
  styleUrl: './button.scss',
})
export class Button {
  @Input() button: IButton | null = null;



}

