import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { QuerySchema } from '@domain/models/query-schema';
import { QuerySchemaPort } from '@domain/ports/query-schema';
import { ApiService } from '@infrastructure/api/api';

@Injectable()
export class QuerySchemaAdapter extends QuerySchemaPort {
  private readonly _http = inject(ApiService);

  getSchemas(): Observable<QuerySchema[]> {
    return this._http.get<QuerySchema[]>('query-schemas');
  }
}
