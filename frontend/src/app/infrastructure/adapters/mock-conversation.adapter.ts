import { Injectable } from '@angular/core';

import { Observable, of, delay, map } from 'rxjs';

import { Message } from '../../domain/models/message';
import { Conversation } from '../../domain/models/conversation';
import { ConversationPort } from '../../domain/ports/conversation';

const MOCK_RESPONSES: string[] = [
  'Based on the database schema, you can use the following SQL query:\n\n```sql\nSELECT * FROM users WHERE created_at > NOW() - INTERVAL \'7 days\';\n```\n\nThis will return all users created in the last 7 days.',
  'Here\'s the optimized query for your request:\n\n```sql\nSELECT u.name, COUNT(o.id) AS total_orders\nFROM users u\nJOIN orders o ON u.id = o.user_id\nGROUP BY u.name\nORDER BY total_orders DESC\nLIMIT 10;\n```',
  'The table structure shows a one-to-many relationship. You can query it like this:\n\n```sql\nSELECT p.name, c.name AS category\nFROM products p\nINNER JOIN categories c ON p.category_id = c.id\nWHERE p.price > 100;\n```',
  'To get the monthly revenue breakdown:\n\n```sql\nSELECT\n  DATE_TRUNC(\'month\', order_date) AS month,\n  SUM(total_amount) AS revenue\nFROM orders\nWHERE order_date >= \'2025-01-01\'\nGROUP BY month\nORDER BY month;\n```',
];

@Injectable()
export class MockConversationAdapter extends ConversationPort {

  private _responseIndex = 0;

  createConversation(): Observable<Conversation> {
    const conversation: Conversation = {
      id: crypto.randomUUID(),
      title: 'New Conversation',
      messages: [],
      createdAt: new Date(),
    };
    return of(conversation);
  }

  getConversation(id: string): Observable<Conversation> {
    return of({
      id,
      title: 'Existing Conversation',
      messages: [],
      createdAt: new Date(),
    });
  }

  sendMessage(_conversationId: string, _content: string): Observable<Message> {
    const responseContent = MOCK_RESPONSES[this._responseIndex % MOCK_RESPONSES.length];
    this._responseIndex++;

    return of(null).pipe(
      delay(800 + Math.random() * 1200),
      map(() => ({
        id: crypto.randomUUID(),
        role: 'assistant' as const,
        content: responseContent,
        timestamp: new Date(),
      })),
    );
  }
}
