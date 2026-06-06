import { ChangeDetectionStrategy, Component, EventEmitter, Input, OnInit, Output, computed, effect, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

import { SUBMIT_PROMPT_BUTTON } from '@constants/components/prompt';
import { IButton } from '@interfaces/components/button';
import { Button } from "@components/button/button";
import { ConversationFacade } from '@domain/facades/conversation';
import { QuerySchema } from '@domain/models/query-schema';
import { QuerySchemaPort } from '@domain/ports/query-schema';
import { Dropdown } from '@components/dropdown/dropdown';
import { IDropdown } from '@interfaces/components/dropdown';
import { PromptSubmission, PromptSubmitMode } from '@interfaces/components/prompt';
import { buildSchemaDropdown } from '@utils/prompt';

@Component({
  selector: 'talk2db-prompt',
  imports: [ReactiveFormsModule, Button, Dropdown],
  templateUrl: './prompt.html',
  styleUrl: './prompt.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Prompt implements OnInit {

  private readonly _facade = inject(ConversationFacade);
  private readonly _schemas = inject(QuerySchemaPort);
  private _submitMode: PromptSubmitMode = 'send';
  private _schemasLoaded = false;

  @Input()
  set submitMode(mode: PromptSubmitMode) {
    this._submitMode = mode;
    if (mode === 'emit') {
      this._loadSchemas();
    }
  }

  get submitMode(): PromptSubmitMode {
    return this._submitMode;
  }

  @Output() submitted = new EventEmitter<PromptSubmission>();

  readonly isLoading = this._facade.isLoading;
  readonly schemas = signal<QuerySchema[]>([]);
  readonly selectedSchemaId = signal<string | null>(null);
  readonly isLoadingSchemas = signal<boolean>(false);
  readonly schemaError = signal<boolean>(false);
  readonly promptForm = new FormGroup({
    prompt: new FormControl('', [Validators.required]),
    schemaId: new FormControl(''),
  });

  readonly currentConversation = this._facade.currentConversation;
  private readonly _syncConversationSchema = effect(() => {
    const conversation = this.currentConversation();
    if (conversation && this.submitMode === 'send') {
      this.promptForm.controls.schemaId.setValue(conversation.schema_id, { emitEvent: false });
      this.selectedSchemaId.set(conversation.schema_id);
    }
  });

  readonly canSelectSchema = computed(() => this.submitMode === 'emit' && !this.isLoadingSchemas());
  readonly selectedSchemaName = computed(() => {
    const selectedId = this.selectedSchemaId();
    return this.schemas().find(schema => schema.id === selectedId)?.name
      ?? this.currentConversation()?.schema_name
      ?? 'Schema';
  });
  readonly schemaDropdown = computed<IDropdown>(() =>
    buildSchemaDropdown(this.schemas(), this.selectedSchemaName(), this.isLoadingSchemas()),
  );

  readonly submitButton = computed<IButton>(() => ({
    ...SUBMIT_PROMPT_BUTTON,
    disabled: this.isLoading() || (this.submitMode === 'emit' && !this.promptForm.controls.schemaId.value),
  }));

  ngOnInit(): void {
    if (this.submitMode !== 'emit') {
      return;
    }
    this._loadSchemas();
  }

  onSubmit(): void {
    if (this.promptForm.controls.prompt.invalid || this.isLoading()) return;

    const content = this.promptForm.get('prompt')?.value?.trim();
    const schemaId = this.promptForm.get('schemaId')?.value;
    if (!content) return;

    if (this.submitMode === 'emit') {
      if (!schemaId) return;
      this.submitted.emit({ content, schemaId });
    } else {
      this._facade.sendMessage(content);
    }
    this.promptForm.controls.prompt.reset();
  }

  selectSchema(schemaId: string): void {
    if (!this.canSelectSchema()) return;
    this.promptForm.controls.schemaId.setValue(schemaId);
    this.selectedSchemaId.set(schemaId);
  }

  private _loadSchemas(): void {
    if (this._schemasLoaded) {
      return;
    }
    this._schemasLoaded = true;
    const conversation = this.currentConversation();
    if (conversation) {
      this.promptForm.controls.schemaId.setValue(conversation.schema_id);
      this.selectedSchemaId.set(conversation.schema_id);
    }

    this.isLoadingSchemas.set(true);
    this._schemas.getSchemas().subscribe({
      next: schemas => {
        this.schemas.set(schemas);
        this.schemaError.set(false);
        const currentSchemaId = this.currentConversation()?.schema_id;
        const selectedSchemaId = this.promptForm.controls.schemaId.value;
        const fallbackSchemaId = schemas[0]?.id ?? '';
        const nextSchemaId = currentSchemaId || selectedSchemaId || fallbackSchemaId;
        this.promptForm.controls.schemaId.setValue(nextSchemaId);
        this.selectedSchemaId.set(nextSchemaId || null);
        this.isLoadingSchemas.set(false);
      },
      error: () => {
        this.schemaError.set(true);
        this.isLoadingSchemas.set(false);
      },
    });
  }
}
