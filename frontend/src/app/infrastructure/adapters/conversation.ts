import { inject, Injectable } from "@angular/core";

import { Observable } from "rxjs/internal/Observable";

import { environment } from "@environment/environment";
import { ApiService } from "@infrastructure/api/api";

import { Conversation } from "@domain/models/conversation";
import { Message } from "@domain/models/message";

@Injectable()
export class ConversationAdapter {

    private readonly _http = inject(ApiService);

    createConversation(): Observable<Conversation> {
        return this._http.post<Conversation>('conversations', { schema_id: environment.defaultSchemaId });
    }

    getConversation(id: string): Observable<Conversation> {
        return this._http.get<Conversation>(`conversations/${id}`);
    }
    
    sendMessage(conversationId: string, content: string): Observable<Message> {
        return this._http.post<Message>(`conversations/${conversationId}/messages`, { content });
    }

    getConversations(): Observable<Conversation[]> {
        return this._http.get<Conversation[]>('conversations');
    }
}
