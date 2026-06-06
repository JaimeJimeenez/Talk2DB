import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ImportQuerySchemaPayload, QuerySchema, QuerySchemaDetail } from '@domain/models/query-schema';
import { QuerySchemaPort } from '@domain/ports/query-schema';
import { ApiService } from '@infrastructure/api/api';

@Injectable()
export class QuerySchemaAdapter extends QuerySchemaPort {
  private readonly _http = inject(ApiService);

  getSchemas(): Observable<QuerySchema[]> {
    return this._http.get<QuerySchema[]>('query-schemas');
  }

  getSchemaDetail(schemaId: string): Observable<QuerySchemaDetail> {
    return this._http.get<QuerySchemaDetail>(`query-schemas/${schemaId}`);
  }

  importSchema(payload: ImportQuerySchemaPayload): Observable<QuerySchemaDetail> {
    const formData = new FormData();
    formData.append('name', payload.name);
    formData.append('description', payload.description);
    formData.append('business_rules', payload.businessRules);
    formData.append('file', payload.file);

    return this._http.post<QuerySchemaDetail>('query-schemas/import', formData);
  }
}
