import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideLucideIcons, LucidePlus } from '@lucide/angular';

import { Sidebar } from './sidebar';
import { NEW_CHAT_BUTTON } from '@constants/components/sidebar';

describe('Sidebar', () => {
  let component: Sidebar;
  let fixture: ComponentFixture<Sidebar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Sidebar],
      providers: [provideLucideIcons(LucidePlus)],
    }).compileComponents();

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
      expect(component.newChatButton()).toEqual(NEW_CHAT_BUTTON);
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
  });
});
