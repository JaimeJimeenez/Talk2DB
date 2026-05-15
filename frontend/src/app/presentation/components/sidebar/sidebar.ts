import { ChangeDetectionStrategy, Component, signal } from '@angular/core';

import { Button } from "@components/button/button";

import { NEW_CHAT_BUTTON } from '@constants/components/sidebar';

import { IButton } from '@interfaces/components/button';

@Component({
  selector: 'talk2db-sidebar',
  imports: [Button],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Sidebar {
  readonly newChatButton = signal<IButton>({ ...NEW_CHAT_BUTTON });
}
