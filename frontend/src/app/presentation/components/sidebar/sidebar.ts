import { ChangeDetectionStrategy, Component, inject, OnInit } from '@angular/core';

import { Button } from "@components/button/button";
import { Dropdown } from '@components/dropdown/dropdown';
import { SidebarService } from '@services/sidebar';

@Component({
  selector: 'talk2db-sidebar',
  imports: [Button, Dropdown],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Sidebar implements OnInit {
  private readonly _sidebar = inject(SidebarService);

  readonly newChatButton = this._sidebar.newChatButton;
  readonly recentQueriesDropdown = this._sidebar.recentQueriesDropdown;
  readonly sidebarButtons = this._sidebar.sidebarButtons;

  ngOnInit(): void {
    this._sidebar.loadRecentConversations();
  }

  navigateToConversation(conversationId: string): void {
    this._sidebar.navigateToConversation(conversationId);
  }
}
