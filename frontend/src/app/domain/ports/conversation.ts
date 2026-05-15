import { Observable } from 'rxjs';

import { Message } from '@domain/models/message';
import { Conversation } from '@domain/models/conversation';

export abstract class ConversationPort {
  abstract sendMessage(conversationId: string, content: string): Observable<Message>;
  abstract getConversation(id: string): Observable<Conversation>;
  abstract createConversation(): Observable<Conversation>;
}
