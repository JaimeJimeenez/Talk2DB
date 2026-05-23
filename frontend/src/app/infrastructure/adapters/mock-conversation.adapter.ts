import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

import { Conversation } from '@domain/models/conversation';
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
  };

  sendMessage(_conversationId: string, content: string): Observable<Message> {
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

  createConversation(): Observable<Conversation> {
    return of(this._conversation);
  }
}
