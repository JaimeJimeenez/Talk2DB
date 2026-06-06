import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { provideLucideIcons, LucideChartLine, LucideChevronDown, LucideDatabase, LucideHistory, LucidePlus } from '@lucide/angular';

import { Sidebar } from './sidebar';
import { NEW_CHAT_BUTTON } from '@constants/components/sidebar';
import { ConversationPort } from '@domain/ports/conversation';
import { MockConversationAdapter } from '@infrastructure/adapters/mock-conversation.adapter';

describe('Sidebar', () => {
  let component: Sidebar;
  let fixture: ComponentFixture<Sidebar>;
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Sidebar],
      providers: [
        { provide: ConversationPort, useClass: MockConversationAdapter },
        provideRouter([]),
        provideLucideIcons(LucidePlus, LucideHistory, LucideChevronDown, LucideDatabase, LucideChartLine),
      ],
    }).compileComponents();

    router = TestBed.inject(Router);
    fixture = TestBed.createComponent(Sidebar);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('newChatButton', () => {
    it('should have a newChatButton property defined', () => {
      expect(component.newChatButton()).toBeTruthy();
    });

    it('should have the correct label from NEW_CHAT_BUTTON constant', () => {
      expect(component.newChatButton().label).toBe(NEW_CHAT_BUTTON.label);
    });

    it('should have the correct disabled state from NEW_CHAT_BUTTON constant', () => {
      expect(component.newChatButton().disabled).toBe(NEW_CHAT_BUTTON.disabled);
    });

    it('should have the correct class from NEW_CHAT_BUTTON constant', () => {
      expect(component.newChatButton().class).toBe(NEW_CHAT_BUTTON.class);
    });

    it('should have the correct startIcon from NEW_CHAT_BUTTON constant', () => {
      expect(component.newChatButton().startIcon).toEqual(NEW_CHAT_BUTTON.startIcon);
    });

    it('should be a separate copy from the constant (not same reference)', () => {
      expect(component.newChatButton()).not.toBe(NEW_CHAT_BUTTON);
      expect(component.newChatButton().label).toBe(NEW_CHAT_BUTTON.label);
    });
  });

  describe('DOM structure', () => {
    it('should render an aside element', () => {
      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.querySelector('aside')).toBeTruthy();
    });

    it('should render the sidebar-header container', () => {
      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.querySelector('.sidebar-header')).toBeTruthy();
    });

    it('should display "Talk2DB" title in an h4 element', () => {
      const compiled = fixture.nativeElement as HTMLElement;
      const h4 = compiled.querySelector('h4');
      expect(h4).toBeTruthy();
      expect(h4?.textContent).toBe('Talk2DB');
    });

    it('should render the talk2db-button component', () => {
      const compiled = fixture.nativeElement as HTMLElement;
      expect(compiled.querySelector('talk2db-button')).toBeTruthy();
    });

    it('should render the talk2db-button with the new_chat class', () => {
      const compiled = fixture.nativeElement as HTMLElement;
      const buttonWrapper = compiled.querySelector('talk2db-button.new_chat');
      expect(buttonWrapper).toBeTruthy();
    });

    it('should render sidebar navigation sections', () => {
      const compiled = fixture.nativeElement as HTMLElement;

      expect(compiled.textContent).toContain('Consultas recientes');
      expect(compiled.textContent).toContain('Esquemas de bases de datos');
      expect(compiled.textContent).toContain('Métrica de uso');
    });

    it('should render recent conversations', () => {
      const compiled = fixture.nativeElement as HTMLElement;

      expect(compiled.querySelector('.dropdown-item')?.textContent).toContain('Mock conversation');
    });

    it('should navigate to a recent conversation', () => {
      const navigate = vi.spyOn(router, 'navigate').mockResolvedValue(true);
      const compiled = fixture.nativeElement as HTMLElement;
      const recentConversation = compiled.querySelector<HTMLButtonElement>('.dropdown-item');

      recentConversation?.click();

      expect(navigate).toHaveBeenCalledWith(['/conversations', 'conversation-1']);
    });
  });
});
