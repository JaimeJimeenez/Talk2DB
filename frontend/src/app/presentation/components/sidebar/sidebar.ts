import { Component } from '@angular/core';

import { Button } from "@components/button/button";

import { NEW_CHAT_BUTTON } from '@constants/components/sidebar';

import { IButton } from '@interfaces/components/button';

@Component({
  selector: 'talk2db-sidebar',
  imports: [Button],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
})
export class Sidebar {
  public readonly newChatButton: IButton = { ...NEW_CHAT_BUTTON };

}
