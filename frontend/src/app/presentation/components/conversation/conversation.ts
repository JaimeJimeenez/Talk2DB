import { ChangeDetectionStrategy, Component, computed, ElementRef, effect, inject, output, viewChild } from '@angular/core';

import { ConversationFacade } from '@domain/facades/conversation';
import { Question } from '@components/question/question';
import { Answer } from '@components/answer/answer';
import { QueryArtifact } from '@domain/models/message';

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

  readonly artifactSelected = output<QueryArtifact>();
  readonly messages = this._facade.messages;
  readonly isLoading = this._facade.isLoading;
  readonly hasMessages = computed(() => this.messages().length > 0);
  private _lastEmittedArtifactId: string | null = null;

  constructor() {
    effect(() => {
      const messages = this.messages();
      this._scrollToBottom();
      const artifact = messages
        .filter(message => message.role === 'assistant' && message.artifact)
        .at(-1)?.artifact;
      if (artifact && artifact.id !== this._lastEmittedArtifactId) {
        this._lastEmittedArtifactId = artifact.id;
        this.artifactSelected.emit(artifact);
      }
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
