import { computed, inject, Injectable, signal } from "@angular/core";
import { Observable, tap } from "rxjs";

import { ConversationPort } from "@domain/ports/conversation";
import { Conversation, ConversationSummary } from "@domain/models/conversation";
import { Message } from "@domain/models/message";
import { AlertsService } from "@services/alerts";

@Injectable({ providedIn: 'root' })
export class ConversationFacade {
    private readonly _conversation = inject(ConversationPort);
    private readonly _alert = inject(AlertsService);

    private readonly _currentConversation = signal<Conversation | null>(null);
    private readonly _conversations = signal<ConversationSummary[]>([]);
    private readonly _isLoading = signal<boolean>(false);

    readonly currentConversation = this._currentConversation.asReadonly()
    readonly conversations = this._conversations.asReadonly();
    readonly isLoading = this._isLoading.asReadonly();
    readonly messages = computed(() => this._currentConversation()?.messages ?? []);

    createConversation(schemaId: string): Observable<Conversation> {
        return this._conversation.createConversation(schemaId).pipe(
            tap(conversation => {
                this._currentConversation.set(conversation);
                this._upsertConversationSummary(conversation.id, conversation.title);
            }),
        );
    }

    getConversation(id: string): void {
        this._conversation.getConversation(id).subscribe({
            next: (conversation: Conversation) => {
                this._currentConversation.set(conversation);
            },
            error: () => {
                this._alert.error('Error', 'Failed to fetch conversation. Please try again later.');
            },
        });
    }

    sendMessage(content: string): void {
        const conversation: Conversation | null = this._currentConversation();
        if (!conversation) return;

        this.sendMessageToConversation(conversation, content);
    }

    sendMessageToConversation(conversation: Conversation, content: string): void {
        if (this._isLoading()) return;
        const userMessage = this._creatUserMessage(content);
        this._updateConversation(userMessage);
        this._isLoading.set(true);
        
        this._conversation.sendMessage(conversation.id, content, conversation.schema_id).subscribe({
            next: (assistantMessage) => {
                this._updateConversation(assistantMessage);
                this._isLoading.set(false);
            },
            error: () => {
                this._isLoading.set(false);
            },
        });
    }

    getConversations(): void {
        this._conversation.getConversations().subscribe({
            next: (conversations: ConversationSummary[]) => {
                this._conversations.set(conversations);
            },
            error: (error: any) => {
                console.error('Failed to fetch conversations:', error);
                this._alert.error('Error', 'Failed to fetch conversations. Please try again later.');
            }
        });
    }

    clearCurrentConversation(): void {
        this._currentConversation.set(null);
    }

    private _creatUserMessage(content: string): Message {
        return {
            id: crypto.randomUUID(),
            role: 'user',
            content,
            timestamp: new Date(),
        };
    }

    private _updateConversation(message: Message): void {
        this._currentConversation.update(conversation => conversation ? {
            ...conversation,
            title: message.conversationTitle?.trim() || conversation.title,
            messages: [...conversation.messages, message],
        } : conversation);
        if (message.conversationTitle?.trim()) {
            this._updateConversationSummary(message.conversationTitle);
        }
    }

    private _updateConversationSummary(title: string): void {
        const conversation = this._currentConversation();
        if (!conversation) return;
        this._upsertConversationSummary(conversation.id, title);
    }

    private _upsertConversationSummary(id: string, title: string): void {
        this._conversations.update(conversations => {
            const existing = conversations.find(item => item.id === id);
            if (!existing) return [{ id, title }, ...conversations];
            return conversations.map(item => item.id === id ? { ...item, title } : item);
        });
    }
}
