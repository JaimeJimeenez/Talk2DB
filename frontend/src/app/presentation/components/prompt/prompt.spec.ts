import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideLucideIcons, LucideArrowUp } from '@lucide/angular';

import { Prompt } from './prompt';
import { ConversationPort } from '@domain/ports/conversation';
import { MockConversationAdapter } from '@infrastructure/adapters/mock-conversation.adapter';

describe('Prompt', () => {
  let component: Prompt;
  let fixture: ComponentFixture<Prompt>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Prompt],
      providers: [
        { provide: ConversationPort, useClass: MockConversationAdapter },
        provideLucideIcons(LucideArrowUp),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Prompt);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
