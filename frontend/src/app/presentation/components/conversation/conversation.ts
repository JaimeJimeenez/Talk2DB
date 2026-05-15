import { ChangeDetectionStrategy, Component, computed, ElementRef, effect, inject, viewChild } from '@angular/core';

import { ConversationFacade } from '@domain/facades/conversation';
import { Question } from '@components/question/question';
import { Answer } from '@components/answer/answer';

@Component({
  selector: 'talk2db-conversation',
  imports: [Question, Answer],
  templateUrl: './conversation.html',
  styleUrl: './conversation.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Conversation {

  private readonly _facade = inject(ConversationFacade);
  private readonly _scrollContainer = viewChild<ElementRef<HTMLElement>>('scrollContainer');

  readonly messages = this._facade.messages;
  readonly isLoading = this._facade.isLoading;
  readonly hasMessages = computed(() => this.messages().length > 0);

  constructor() {
    effect(() => {
      this.messages();
      this._scrollToBottom();
    });
  }

  private _scrollToBottom(): void {
    setTimeout(() => {
      const container = this._scrollContainer()?.nativeElement;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    });
  }
}
