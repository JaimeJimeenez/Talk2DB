import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ConversationAdapter } from './conversation';
import { ApiService } from '@infrastructure/api/api';
import { environment } from '@environment/environment';

describe('ConversationAdapter', () => {
  let adapter: ConversationAdapter;
  let api: {
    get: ReturnType<typeof vi.fn>;
    post: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    const conversation = {
      id: 'conversation-1',
      title: 'Demo',
      created_at: '2026-05-23T00:00:00.000Z',
      schema_id: environment.defaultSchemaId,
      schema_name: 'sales',
      messages: [],
    };
    const message = {
      id: 'message-1',
      role: 'assistant',
      content: 'Done',
      timestamp: '2026-05-23T00:00:01.000Z',
      conversation_id: 'conversation-1',
      sql: null,
      error: null,
      artifact: null,
      conversation_title: 'show users',
    };

    api = {
      get: vi.fn().mockReturnValue(of(conversation)),
      post: vi.fn((url: string) => of(url === 'rag/completion' ? message : conversation)),
    };

    TestBed.configureTestingModule({
      providers: [
        ConversationAdapter,
        { provide: ApiService, useValue: api },
      ],
    });

    adapter = TestBed.inject(ConversationAdapter);
  });

  it('creates conversations with the selected schema id', () => {
    adapter.createConversation('schema-1').subscribe(conversation => {
      expect(conversation.createdAt).toBeInstanceOf(Date);
    });

    expect(api.post).toHaveBeenCalledWith('conversations', {
      schema_id: 'schema-1',
    });
  });

  it('gets conversations by id', () => {
    adapter.getConversation('conversation-1').subscribe();

    expect(api.get).toHaveBeenCalledWith('conversations/conversation-1');
  });

  it('sends messages to a conversation', () => {
    adapter.sendMessage('conversation-1', 'show users', 'schema-1').subscribe(message => {
      expect(message.timestamp).toBeInstanceOf(Date);
      expect(message.conversationTitle).toBe('show users');
    });

    expect(api.post).toHaveBeenCalledWith('rag/completion', {
      conversation_id: 'conversation-1',
      prompt: 'show users',
      schema_id: 'schema-1',
    });
  });

  it('requires a schema id to send a message', () => {
    expect(() => adapter.sendMessage('conversation-1', 'show users')).toThrow('schemaId is required');
  });

  it('maps completion answers when content is missing', () => {
    api.post.mockReturnValueOnce(of({
      id: 'message-3',
      role: 'assistant',
      answer: 'Done from RAG',
      title: 'RAG title',
      timestamp: '2026-05-23T00:00:03.000Z',
      sql: null,
      error: null,
      artifact: null,
    }));

    adapter.sendMessage('conversation-1', 'show users', 'schema-1').subscribe(message => {
      expect(message.content).toBe('Done from RAG');
      expect(message.conversationTitle).toBe('RAG title');
    });
  });

  it('creates a fallback artifact for assistant messages with sql', () => {
    api.post.mockReturnValueOnce(of({
      id: 'message-2',
      role: 'assistant',
      content: 'SQL ready',
      timestamp: '2026-05-23T00:00:02.000Z',
      sql: 'SELECT 1',
      error: null,
      artifact: null,
    }));

    adapter.sendMessage('conversation-1', 'show users', 'schema-1').subscribe(message => {
      expect(message.artifact?.title).toBe('SQL ready');
      expect(message.artifact?.sql).toBe('SELECT 1');
    });
  });

  it('lists conversations', () => {
    adapter.getConversations().subscribe();

    expect(api.get).toHaveBeenCalledWith('conversations');
  });
});
