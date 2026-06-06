import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

import { Conversation, ConversationSummary } from '@domain/models/conversation';
import { Message } from '@domain/models/message';
import { ConversationPort } from '@domain/ports/conversation';
import { environment } from '@environment/environment';

@Injectable()
export class MockConversationAdapter extends ConversationPort {
  private readonly _conversation: Conversation = {
    id: 'conversation-1',
    title: 'Mock conversation',
    messages: [],
    createdAt: new Date('2026-05-23T00:00:00.000Z'),
    schema_id: environment.defaultSchemaId,
    schema_name: 'ventas',
  };

  sendMessage(_conversationId: string, content: string, _schemaId?: string): Observable<Message> {
    return of({
      id: 'message-1',
      role: 'assistant',
      content,
      timestamp: new Date('2026-05-23T00:00:01.000Z'),
    });
  }

  getConversation(_id: string): Observable<Conversation> {
    return of(this._conversation);
  }

  createConversation(schemaId: string): Observable<Conversation> {
    return of({ ...this._conversation, schema_id: schemaId });
  }

  getConversations(): Observable<ConversationSummary[]> {
    return of([this._conversation]);
  }
}
