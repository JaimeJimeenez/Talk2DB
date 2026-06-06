import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideLucideIcons, LucideArrowUp, LucideChevronDown, LucideDatabase } from '@lucide/angular';
import { of } from 'rxjs';

import { Prompt } from './prompt';
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

describe('Prompt', () => {
  let component: Prompt;
  let fixture: ComponentFixture<Prompt>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Prompt],
      providers: [
        { provide: ConversationPort, useClass: MockConversationAdapter },
        { provide: QuerySchemaPort, useClass: MockQuerySchemaAdapter },
        provideLucideIcons(LucideArrowUp, LucideChevronDown, LucideDatabase),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Prompt);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('renders available schemas', () => {
    fixture.componentRef.setInput('submitMode', 'emit');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.querySelector('talk2db-dropdown')?.textContent).toContain('ventas');
  });

  it('does not render schema dropdown when sending in an existing chat', () => {
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.querySelector('talk2db-dropdown')).toBeNull();
  });

  it('selects a schema with the dropdown', () => {
    fixture.componentRef.setInput('submitMode', 'emit');
    fixture.detectChanges();

    component.selectSchema('schema-1');

    expect(component.promptForm.controls.schemaId.value).toBe('schema-1');
  });
});
