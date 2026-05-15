import { Component, computed, inject, OnInit } from '@angular/core';

import { ConversationFacade } from '@domain/facades/conversation';
import { Prompt } from "@components/prompt/prompt";
import { Conversation } from "@components/conversation/conversation";

@Component({
  selector: 'talk2db-chat',
  imports: [Prompt, Conversation],
  templateUrl: './chat.html',
  styleUrl: './chat.scss',
})
export class Chat implements OnInit {

  private readonly _facade = inject(ConversationFacade);

  readonly hasMessages = computed(() => this._facade.messages().length > 0);

  ngOnInit(): void {
    this._facade.createConversation();
  }
}
