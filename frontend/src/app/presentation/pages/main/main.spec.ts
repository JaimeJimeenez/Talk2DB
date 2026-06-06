import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideLucideIcons, LucideChartLine, LucideChevronDown, LucideDatabase, LucideHistory, LucidePlus } from '@lucide/angular';

import { Main } from './main';
import { ConversationPort } from '@domain/ports/conversation';
import { MockConversationAdapter } from '@infrastructure/adapters/mock-conversation.adapter';

describe('Main', () => {
  let component: Main;
  let fixture: ComponentFixture<Main>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Main],
      providers: [
        { provide: ConversationPort, useClass: MockConversationAdapter },
        provideRouter([]),
        provideLucideIcons(LucidePlus, LucideHistory, LucideChevronDown, LucideDatabase, LucideChartLine),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Main);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render the sidebar component', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('talk2db-sidebar')).toBeTruthy();
  });

  it('should render the header component', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('talk2db-header')).toBeTruthy();
  });

  it('should render the main content area', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('main')).toBeTruthy();
  });

  it('should render the router-outlet inside main', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const main = compiled.querySelector('main');
    expect(main?.querySelector('router-outlet')).toBeTruthy();
  });

  it('should render the header inside main', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const main = compiled.querySelector('main');
    expect(main?.querySelector('talk2db-header')).toBeTruthy();
  });

  it('should render sidebar outside main', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const sidebar = compiled.querySelector('talk2db-sidebar');
    expect(sidebar?.closest('main')).toBeNull();
  });
});
