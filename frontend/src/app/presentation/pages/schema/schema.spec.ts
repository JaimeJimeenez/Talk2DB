import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideLucideIcons, LucideFilePlus2, LucideRefreshCw, LucideUpload } from '@lucide/angular';
import { of } from 'rxjs';

import { Schema } from './schema';
import { ImportQuerySchemaPayload, QuerySchemaDetail } from '@domain/models/query-schema';
import { QuerySchemaPort } from '@domain/ports/query-schema';

const schemaDetail: QuerySchemaDetail = {
  id: 'schema-1',
  name: 'ventas',
  description: 'Schema demo',
  business_rules: 'Excluir cancelados',
  created_at: '2026-05-23T00:00:00Z',
  refreshed_at: '2026-05-23T00:00:00Z',
  table_count: 1,
  column_count: 2,
  tables: [
    {
      name: 'clientes',
      columns: [
        { name: 'id', data_type: 'text', nullable: false },
        { name: 'nombre', data_type: 'text', nullable: false },
      ],
      constraints: [],
    },
  ],
};

class MockQuerySchemaAdapter extends QuerySchemaPort {
  readonly importSchemaSpy = vi.fn();

  getSchemas() {
    return of([schemaDetail]);
  }

  getSchemaDetail() {
    return of(schemaDetail);
  }

  importSchema(payload: ImportQuerySchemaPayload) {
    this.importSchemaSpy(payload);
    return of({ ...schemaDetail, id: 'schema-2', name: payload.name });
  }
}

describe('Schema', () => {
  let component: Schema;
  let fixture: ComponentFixture<Schema>;
  let schemas: MockQuerySchemaAdapter;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Schema],
      providers: [
        { provide: QuerySchemaPort, useClass: MockQuerySchemaAdapter },
        provideLucideIcons(LucideUpload, LucideRefreshCw, LucideFilePlus2),
      ],
    }).compileComponents();

    schemas = TestBed.inject(QuerySchemaPort) as MockQuerySchemaAdapter;
    fixture = TestBed.createComponent(Schema);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
  });

  it('renders the schema catalog and table detail', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.textContent).toContain('Esquemas de bases de datos');
    expect(compiled.textContent).toContain('ventas');
    expect(compiled.textContent).toContain('clientes');
    expect(compiled.textContent).toContain('nombre');
  });

  it('opens import panel and imports a SQL file', () => {
    const file = new File(['CREATE TABLE demo.items(id text);'], 'demo.sql', { type: 'text/sql' });

    component.toggleImportPanel();
    component.importName.set('demo');
    component.importDescription.set('Demo');
    component.importBusinessRules.set('Only active rows');
    component.importFile.set(file);
    component.importSchema();

    expect(schemas.importSchemaSpy).toHaveBeenCalledWith({
      name: 'demo',
      description: 'Demo',
      businessRules: 'Only active rows',
      file,
    });
  });
});
