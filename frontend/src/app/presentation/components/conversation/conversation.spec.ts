import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LucideArrowRight, LucideArrowUp, LucideBot, LucideTable, provideLucideIcons } from '@lucide/angular';

import { Conversation } from './conversation';
import { ConversationPort } from '@domain/ports/conversation';
import { MockConversationAdapter } from '@infrastructure/adapters/mock-conversation.adapter';

describe('Conversation', () => {
  let component: Conversation;
  let fixture: ComponentFixture<Conversation>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Conversation],
      providers: [
        { provide: ConversationPort, useClass: MockConversationAdapter },
        provideLucideIcons(LucideArrowUp, LucideBot, LucideTable, LucideArrowRight),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Conversation);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render conversation container', () => {
    fixture.detectChanges();
    const container = fixture.nativeElement.querySelector('.conversation-container');
    expect(container).toBeTruthy();
  });
});
