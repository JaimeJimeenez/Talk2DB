import { computed, inject, Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';

import { ConversationFacade } from '@domain/facades/conversation';
import { ConversationSummary } from '@domain/models/conversation';
import { IButton } from '@interfaces/components/button';
import { IDropdown } from '@interfaces/components/dropdown';
import { ISidebar } from '@interfaces/components/sidebar';
import { NEW_CHAT_BUTTON, SIDEBAR_ITEMS } from '@constants/components/sidebar';

@Injectable({ providedIn: 'root' })
export class SidebarService {
  private readonly _conversationFacade = inject(ConversationFacade);
  private readonly _router = inject(Router);

  private readonly _sidebarItems = signal<ISidebar[]>([...SIDEBAR_ITEMS]);

  readonly sidebarButtons = computed<IButton[]>(() =>
    this._sidebarItems().slice(1).map(item => this._toSidebarButton(item)),
  );
  
  readonly recentQueriesDropdown = computed<IDropdown>(() => {
    const recentQueriesItem = this._sidebarItems()[0];

    return {
      label: recentQueriesItem.label,
      icon: {
        name: recentQueriesItem.icon,
        title: recentQueriesItem.label,
        size: 18,
      },
      items: this._conversationFacade.conversations().map((conversation, index) => ({
        id: conversation.id,
        label: this._conversationTitle(conversation, index),
      })),
      emptyLabel: 'Sin conversaciones recientes',
    };
  });
  readonly newChatButton = signal<IButton>({
    ...NEW_CHAT_BUTTON,
    onClick: () => this.newChat(),
  });

  loadRecentConversations(): void {
    this._conversationFacade.getConversations();
  }

  navigateToConversation(conversationId: string): void {
    this._router.navigate(['/conversations', conversationId]);
  }

  private newChat(): void {
    this._conversationFacade.clearCurrentConversation();
    this._router.navigate(['/new-chat']);
  }

  private _conversationTitle(conversation: ConversationSummary, index: number): string {
    return conversation.title?.trim() || `Conversación ${index + 1}`;
  }

  private _toSidebarButton(item: ISidebar): IButton {
    return {
      label: item.label,
      startIcon: {
        name: item.icon,
        title: item.label,
        size: 18,
      },
      class: 'sidebar-item-button',
      disabled: false,
      onClick: () => this._router.navigate([item.path]),
      type: 'button',
    };
  }
}
