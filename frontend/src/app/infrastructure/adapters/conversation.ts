import { inject, Injectable } from "@angular/core";

import { Observable } from "rxjs/internal/Observable";
import { map } from "rxjs";

import { ApiService } from "@infrastructure/api/api";

import { Conversation, ConversationSummary } from "@domain/models/conversation";
import { Message, QueryArtifact } from "@domain/models/message";

type ApiConversation = Omit<Conversation, 'createdAt' | 'messages'> & {
    readonly created_at?: string;
    readonly createdAt?: string;
    readonly messages: ApiMessage[];
};

type ApiMessage = Omit<Message, 'timestamp'> & {
    readonly timestamp: string;
    readonly conversation_id?: string;
    readonly answer?: string;
    readonly title?: string;
    readonly conversation_title?: string | null;
};

@Injectable()
export class ConversationAdapter {

    private readonly _http = inject(ApiService);

    createConversation(schemaId: string): Observable<Conversation> {
        return this._http.post<ApiConversation>('conversations', { schema_id: schemaId }).pipe(
            map(conversation => this._mapConversation(conversation)),
        );
    }

    getConversation(id: string): Observable<Conversation> {
        return this._http.get<ApiConversation>(`conversations/${id}`).pipe(
            map(conversation => this._mapConversation(conversation)),
        );
    }
    
    sendMessage(conversationId: string, content: string, schemaId?: string): Observable<Message> {
        if (!schemaId) {
            throw new Error('schemaId is required to send a RAG completion message.');
        }

        return this._http.post<ApiMessage>('rag/completion', {
            conversation_id: conversationId,
            prompt: content,
            schema_id: schemaId,
        }).pipe(
            map(message => this._mapMessage(message)),
        );
    }

    getConversations(): Observable<ConversationSummary[]> {
        return this._http.get<ConversationSummary[]>('conversations');
    }

    private _mapConversation(conversation: ApiConversation): Conversation {
        return {
            ...conversation,
            createdAt: new Date(conversation.createdAt ?? conversation.created_at ?? Date.now()),
            messages: conversation.messages.map(message => this._mapMessage(message)),
        };
    }

    private _mapMessage(message: ApiMessage): Message {
        const timestamp = new Date(message.timestamp);
        return {
            ...message,
            content: message.content ?? message.answer ?? '',
            timestamp,
            conversationTitle: message.conversationTitle ?? message.conversation_title ?? message.title ?? null,
            artifact: message.artifact ?? this._fallbackArtifact(message),
        };
    }

    private _fallbackArtifact(message: ApiMessage): QueryArtifact | null {
        if (message.role !== 'assistant' || !message.sql || message.error) {
            return null;
        }

        return {
            id: `${message.id}-artifact`,
            title: this._artifactTitle(message.content),
            summary: message.content,
            type: 'query_result',
            generatedFrom: 'Consulta SQL',
            sql: message.sql,
            columns: [],
            rows: [],
            rowCount: 0,
            truncated: false,
            error: null,
        };
    }

    private _artifactTitle(content: string): string {
        const title = content.trim().replace(/\s+/g, ' ');
        if (!title) return 'Resultado de consulta';
        return title.length > 72 ? `${title.slice(0, 72)}...` : title;
    }
}
