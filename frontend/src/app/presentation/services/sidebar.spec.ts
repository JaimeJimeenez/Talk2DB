import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';

import { SidebarService } from './sidebar';
import { NEW_CHAT_BUTTON } from '@constants/components/sidebar';
import { ConversationPort } from '@domain/ports/conversation';
import { MockConversationAdapter } from '@infrastructure/adapters/mock-conversation.adapter';

describe('SidebarService', () => {
  let service: SidebarService;
  let router: Router;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        SidebarService,
        { provide: ConversationPort, useClass: MockConversationAdapter },
        provideRouter([]),
      ],
    });

    service = TestBed.inject(SidebarService);
    router = TestBed.inject(Router);
  });

  it('builds the new chat button from the sidebar constants', () => {
    expect(service.newChatButton().label).toBe(NEW_CHAT_BUTTON.label);
    expect(service.newChatButton().class).toBe(NEW_CHAT_BUTTON.class);
    expect(service.newChatButton().onClick).toBeTruthy();
  });

  it('builds static sidebar buttons', () => {
    const buttons = service.sidebarButtons();

    expect(buttons.map(button => button.label)).toEqual([
      'Esquemas de bases de datos',
      'Métrica de uso',
    ]);
    expect(buttons.every(button => button.class === 'sidebar-item-button')).toBe(true);
  });

  it('loads recent conversations into the dropdown', () => {
    service.loadRecentConversations();

    expect(service.recentQueriesDropdown().items).toEqual([
      { id: 'conversation-1', label: 'Mock conversation' },
    ]);
  });

  it('navigates to a selected conversation', () => {
    const navigate = vi.spyOn(router, 'navigate').mockResolvedValue(true);

    service.navigateToConversation('conversation-1');

    expect(navigate).toHaveBeenCalledWith(['/conversations', 'conversation-1']);
  });
});
