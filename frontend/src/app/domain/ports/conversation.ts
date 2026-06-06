import { Observable } from 'rxjs';

import { Message } from '@domain/models/message';
import { Conversation, ConversationSummary } from '@domain/models/conversation';

export abstract class ConversationPort {
  abstract sendMessage(conversationId: string, content: string, schemaId?: string): Observable<Message>;
  abstract getConversation(id: string): Observable<Conversation>;
  abstract createConversation(schemaId: string): Observable<Conversation>;
  abstract getConversations(): Observable<ConversationSummary[]>;
}
