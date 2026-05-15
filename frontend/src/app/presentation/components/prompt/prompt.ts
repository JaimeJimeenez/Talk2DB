import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

import { SUBMIT_PROMPT_BUTTON } from '@constants/components/prompt';
import { IButton } from '@interfaces/components/button';
import { Button } from "@components/button/button";
import { ConversationFacade } from '@domain/facades/conversation';

@Component({
  selector: 'talk2db-prompt',
  imports: [ReactiveFormsModule, Button],
  templateUrl: './prompt.html',
  styleUrl: './prompt.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Prompt {

  private readonly _facade = inject(ConversationFacade);

  readonly isLoading = this._facade.isLoading;
  readonly promptForm = new FormGroup({
    prompt: new FormControl('', [Validators.required]),
  });

  readonly submitButton = computed<IButton>(() => ({
    ...SUBMIT_PROMPT_BUTTON,
    disabled: this.isLoading(),
  }));

  onSubmit(): void {
    if (this.promptForm.invalid || this.isLoading()) return;

    const content = this.promptForm.get('prompt')?.value?.trim();
    if (!content) return;

    this._facade.sendMessage(content);
    this.promptForm.reset();
  }
}
