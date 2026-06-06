import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import {
  LucideArrowRight,
  LucideArrowUp,
  LucideBarChart3,
  LucideBot,
  LucideCheck,
  LucideChevronDown,
  LucideCode2,
  LucideCopy,
  LucideDatabase,
  LucideRows3,
  LucideTable,
  LucideX,
  provideLucideIcons,
} from '@lucide/angular';
import { of } from 'rxjs';

import { Chat } from './chat';
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
        table_count: 1,
        column_count: 2,
      },
    ]);
  }

  getSchemaDetail() {
    return of({
      id: 'schema-1',
      name: 'ventas',
      description: 'Ventas',
      business_rules: '',
      created_at: '2026-05-23T00:00:00Z',
      refreshed_at: '2026-05-23T00:00:00Z',
      table_count: 1,
      column_count: 2,
      tables: [],
    });
  }

  importSchema() {
    return this.getSchemaDetail();
  }
}

describe('Chat', () => {
  let component: Chat;
  let fixture: ComponentFixture<Chat>;

  async function setup(
    conversationId?: string,
    prepareFacade?: (facade: ConversationFacade) => void,
  ): Promise<void> {
    TestBed.resetTestingModule();

    await TestBed.configureTestingModule({
      imports: [Chat],
      providers: [
        { provide: ConversationPort, useClass: MockConversationAdapter },
        { provide: QuerySchemaPort, useClass: MockQuerySchemaAdapter },
        {
          provide: ActivatedRoute,
          useValue: {
            paramMap: of(convertToParamMap(conversationId ? { conversationId } : {})),
          },
        },
        provideLucideIcons(
          LucideArrowUp,
          LucideBot,
          LucideTable,
          LucideArrowRight,
          LucideRows3,
          LucideBarChart3,
          LucideCode2,
          LucideCopy,
          LucideCheck,
          LucideX,
          LucideDatabase,
          LucideChevronDown,
        ),
      ],
    }).compileComponents();

    prepareFacade?.(TestBed.inject(ConversationFacade));
    fixture = TestBed.createComponent(Chat);
    component = fixture.componentInstance;
    await fixture.whenStable();
  }

  it('should create', async () => {
    await setup();

    expect(component).toBeTruthy();
  });

  it('does not create a conversation when there is no conversation id in the url', async () => {
    let createConversation: ReturnType<typeof vi.spyOn>;
    await setup(undefined, facade => {
      createConversation = vi.spyOn(facade, 'createConversation');
    });

    fixture.detectChanges();

    expect(createConversation!).not.toHaveBeenCalled();
  });

  it('loads the conversation from the url conversation id', async () => {
    let getConversation: ReturnType<typeof vi.spyOn>;
    let createConversation: ReturnType<typeof vi.spyOn>;
    await setup('conversation-1', facade => {
      getConversation = vi.spyOn(facade, 'getConversation');
      createConversation = vi.spyOn(facade, 'createConversation');
    });

    fixture.detectChanges();

    expect(getConversation!).toHaveBeenCalledWith('conversation-1');
    expect(createConversation!).not.toHaveBeenCalled();
  });

  it('does not refetch the conversation that is already current', async () => {
    let getConversation: ReturnType<typeof vi.spyOn>;
    await setup('conversation-1', facade => {
      facade.createConversation('schema-1').subscribe();
      getConversation = vi.spyOn(facade, 'getConversation');
    });

    fixture.detectChanges();

    expect(getConversation!).not.toHaveBeenCalled();
  });
});
