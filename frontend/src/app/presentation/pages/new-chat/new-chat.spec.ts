import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { provideLucideIcons, LucideArrowUp, LucideChevronDown, LucideDatabase } from '@lucide/angular';
import { of } from 'rxjs';

import { NewChat } from './new-chat';
import { ConversationFacade } from '@domain/facades/conversation';
import { ConversationPort } from '@domain/ports/conversation';
import { MockConversationAdapter } from '@infrastructure/adapters/mock-conversation.adapter';
import { QuerySchemaPort } from '@domain/ports/query-schema';

class MockQuerySchemaAdapter extends QuerySchemaPort {
  getSchemas() {
    return of([
      {
        id: 'schema-1',
        name: 'ventas',
        description: 'Ventas',
        business_rules: '',
        created_at: '2026-05-23T00:00:00Z',
        refreshed_at: '2026-05-23T00:00:00Z',
      },
    ]);
  }
}

describe('NewChat', () => {
  let component: NewChat;
  let fixture: ComponentFixture<NewChat>;
  let router: { navigate: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    router = {
      navigate: vi.fn().mockResolvedValue(true),
    };

    await TestBed.configureTestingModule({
      imports: [NewChat],
      providers: [
        { provide: ConversationPort, useClass: MockConversationAdapter },
        { provide: QuerySchemaPort, useClass: MockQuerySchemaAdapter },
        { provide: Router, useValue: router },
        provideLucideIcons(LucideArrowUp, LucideChevronDown, LucideDatabase),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(NewChat);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('creates a conversation, navigates to it and sends the first prompt', async () => {
    const facade = TestBed.inject(ConversationFacade);
    const createConversation = vi.spyOn(facade, 'createConversation');
    const sendMessageToConversation = vi.spyOn(facade, 'sendMessageToConversation');

    component.submitPrompt({ content: 'show active customers', schemaId: 'schema-1' });
    await fixture.whenStable();

    expect(createConversation).toHaveBeenCalledWith('schema-1');
    expect(sendMessageToConversation).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'conversation-1', schema_id: 'schema-1' }),
      'show active customers',
    );
    expect(router.navigate).toHaveBeenCalledWith(['/conversations', 'conversation-1']);
  });
});
