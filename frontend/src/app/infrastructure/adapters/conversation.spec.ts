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
    api = {
      get: vi.fn().mockReturnValue(of(null)),
      post: vi.fn().mockReturnValue(of(null)),
    };

    TestBed.configureTestingModule({
      providers: [
        ConversationAdapter,
        { provide: ApiService, useValue: api },
      ],
    });

    adapter = TestBed.inject(ConversationAdapter);
  });

  it('creates conversations with the default schema id', () => {
    adapter.createConversation().subscribe();

    expect(api.post).toHaveBeenCalledWith('conversations', {
      schema_id: environment.defaultSchemaId,
    });
  });

  it('gets conversations by id', () => {
    adapter.getConversation('conversation-1').subscribe();

    expect(api.get).toHaveBeenCalledWith('conversations/conversation-1');
  });

  it('sends messages to a conversation', () => {
    adapter.sendMessage('conversation-1', 'show users').subscribe();

    expect(api.post).toHaveBeenCalledWith('conversations/conversation-1/messages', {
      content: 'show users',
    });
  });

  it('lists conversations', () => {
    adapter.getConversations().subscribe();

    expect(api.get).toHaveBeenCalledWith('conversations');
  });
});
