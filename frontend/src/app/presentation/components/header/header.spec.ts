import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Header } from './header';
import { ConversationFacade } from '@domain/facades/conversation';
import { ConversationPort } from '@domain/ports/conversation';
import { MockConversationAdapter } from '@infrastructure/adapters/mock-conversation.adapter';

describe('Header', () => {
  let component: Header;
  let fixture: ComponentFixture<Header>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Header],
      providers: [
        { provide: ConversationPort, useClass: MockConversationAdapter },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Header);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have title set to "SQL Assistant"', () => {
    expect(component.title).toBe('SQL Assistant');
  });

  it('should render the header element', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('header')).toBeTruthy();
  });

  it('should display the title in an h3 element', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const h3 = compiled.querySelector('h3');
    expect(h3).toBeTruthy();
    expect(h3?.textContent?.trim()).toBe('SQL Assistant');
  });

  it('should display the selected conversation title', () => {
    const facade = TestBed.inject(ConversationFacade);

    facade.createConversation('schema-1').subscribe();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h3')?.textContent).toContain('SQL Assistant');
    expect(compiled.querySelector('h3')?.textContent).toContain('>');
    expect(compiled.querySelector('h3')?.textContent).toContain('Mock conversation');
  });

  it('should display the selected conversation schema chip', () => {
    const facade = TestBed.inject(ConversationFacade);

    facade.createConversation('schema-1').subscribe();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const chip = compiled.querySelector('talk2db-chip .chip');
    expect(chip?.textContent).toBe('ventas');
  });

  it('should render the header-title container', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const titleDiv = compiled.querySelector('.header-title');
    expect(titleDiv).toBeTruthy();
  });

  it('should render the header-options container', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const optionsDiv = compiled.querySelector('.header-options');
    expect(optionsDiv).toBeTruthy();
  });

  it('should have header-options container empty', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const optionsDiv = compiled.querySelector('.header-options');
    expect(optionsDiv?.children.length).toBe(0);
  });
});
