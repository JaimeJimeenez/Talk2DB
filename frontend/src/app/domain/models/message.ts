export type MessageRole = 'user' | 'assistant';

export interface Message {
    readonly id: string;
    readonly role: MessageRole;
    readonly content: string;
    readonly timestamp: Date;
}