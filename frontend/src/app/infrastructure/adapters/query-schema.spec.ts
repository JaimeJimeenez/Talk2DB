import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { QuerySchemaAdapter } from './query-schema';
import { ApiService } from '@infrastructure/api/api';

describe('QuerySchemaAdapter', () => {
  let adapter: QuerySchemaAdapter;
  let api: {
    get: ReturnType<typeof vi.fn>;
    post: ReturnType<typeof vi.fn>;
  };

  const detail = {
    id: 'schema-1',
    name: 'ventas',
    description: 'Ventas',
    business_rules: '',
    created_at: '2026-05-23T00:00:00Z',
    refreshed_at: '2026-05-23T00:00:00Z',
    table_count: 1,
    column_count: 2,
    tables: [],
  };

  beforeEach(() => {
    api = {
      get: vi.fn((url: string) => of(url.includes('/') ? detail : [detail])),
      post: vi.fn(() => of(detail)),
    };

    TestBed.configureTestingModule({
      providers: [
        QuerySchemaAdapter,
        { provide: ApiService, useValue: api },
      ],
    });

    adapter = TestBed.inject(QuerySchemaAdapter);
  });

  it('loads available schemas', () => {
    adapter.getSchemas().subscribe(schemas => {
      expect(schemas[0].name).toBe('ventas');
    });

    expect(api.get).toHaveBeenCalledWith('query-schemas');
  });

  it('loads schema detail', () => {
    adapter.getSchemaDetail('schema-1').subscribe(schema => {
      expect(schema.id).toBe('schema-1');
    });

    expect(api.get).toHaveBeenCalledWith('query-schemas/schema-1');
  });

  it('posts multipart payload when importing a schema', () => {
    const file = new File(['CREATE TABLE demo.items(id text);'], 'demo.sql', { type: 'text/sql' });

    adapter.importSchema({
      name: 'demo',
      description: 'Demo',
      businessRules: 'Only active rows',
      file,
    }).subscribe(schema => {
      expect(schema.name).toBe('ventas');
    });

    const formData = api.post.mock.calls[0][1] as FormData;
    expect(api.post).toHaveBeenCalledWith('query-schemas/import', expect.any(FormData));
    expect(formData.get('name')).toBe('demo');
    expect(formData.get('business_rules')).toBe('Only active rows');
    expect(formData.get('file')).toBe(file);
  });
});
