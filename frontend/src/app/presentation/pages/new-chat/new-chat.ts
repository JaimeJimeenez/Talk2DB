import { Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { take } from 'rxjs';

import { Prompt } from '@components/prompt/prompt';
import { ConversationFacade } from '@domain/facades/conversation';
import { PromptSubmission } from '@interfaces/components/prompt';

@Component({
  selector: 'talk2db-new-chat',
  imports: [Prompt],
  templateUrl: './new-chat.html',
  styleUrl: './new-chat.scss',
})
export class NewChat implements OnInit {
  private readonly _facade = inject(ConversationFacade);
  private readonly _router = inject(Router);

  ngOnInit(): void {
    this._facade.clearCurrentConversation();
  }

  submitPrompt(submission: PromptSubmission): void {
    this._facade.createConversation(submission.schemaId)
      .pipe(take(1))
      .subscribe(conversation => {
        this._facade.sendMessageToConversation(conversation, submission.content);
        this._router.navigate(['/conversations', conversation.id]);
      });
  }
}
