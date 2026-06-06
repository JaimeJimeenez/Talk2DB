import { Component, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';

import { ConversationFacade } from '@domain/facades/conversation';
import { Prompt } from "@components/prompt/prompt";
import { Conversation } from "@components/conversation/conversation";
import { Artifact } from "@components/artifact/artifact";
import { QueryArtifact } from '@domain/models/message';

@Component({
  selector: 'talk2db-chat',
  imports: [Prompt, Conversation, Artifact],
  templateUrl: './chat.html',
  styleUrl: './chat.scss',
})
export class Chat implements OnInit {

  private readonly _facade = inject(ConversationFacade);
  private readonly _route = inject(ActivatedRoute);
  private readonly _destroyRef = inject(DestroyRef);

  readonly activeArtifact = signal<QueryArtifact | null>(null);

  ngOnInit(): void {
    this._route.paramMap
      .pipe(takeUntilDestroyed(this._destroyRef))
      .subscribe(params => {
        const conversationId = params.get('conversationId');

        if (conversationId) {
          if (this._facade.currentConversation()?.id === conversationId) {
            return;
          }
          this._facade.getConversation(conversationId);
          return;
        }
      });
  }

  openArtifact(artifact: QueryArtifact): void {
    this.activeArtifact.set(artifact);
  }

  closeArtifact(): void {
    this.activeArtifact.set(null);
  }
}
