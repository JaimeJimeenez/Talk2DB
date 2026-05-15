import { computed, inject, Injectable, signal } from "@angular/core";

import { ConversationPort } from "@domain/ports/conversation";
import { Conversation } from "@domain/models/conversation";
import { Message } from "@domain/models/message";

@Injectable({ providedIn: 'root' })
export class ConversationFacade {
    private readonly _conversation = inject(ConversationPort);

    private readonly _currentConversation = signal<Conversation | null>(null);
    private readonly _isLoading = signal<boolean>(false);

    readonly currentConversation = this._currentConversation.asReadonly()
    readonly isLoading = this._isLoading.asReadonly();
    readonly messages = computed(() => this._currentConversation()?.messages ?? []);

    createConversation(): void {
        this._conversation.createConversation().subscribe(
            conversation => this._currentConversation.set(conversation)
        );
    }

    sendMessage(content: string): void {
        const conversation: Conversation | null = this._currentConversation();
        if (!conversation) return;

        const userMessage = this._creatUserMessage(content);
        this._updateConversation(userMessage);
        this._isLoading.set(true);
        
        this._conversation.sendMessage(conversation.id, content).subscribe({
            next: (assistantMessage) => {
                this._updateConversation(assistantMessage);
                this._isLoading.set(false);
            },
            error: () => {
                this._isLoading.set(false);
            },
        });
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
            messages: [...conversation.messages, message],
        } : conversation);
    }
}