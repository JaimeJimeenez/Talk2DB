export type PromptSubmitMode = 'send' | 'emit';

export interface PromptSubmission {
  content: string;
  schemaId: string;
}
