import { Observable } from 'rxjs';

import { QuerySchema } from '@domain/models/query-schema';

export abstract class QuerySchemaPort {
  abstract getSchemas(): Observable<QuerySchema[]>;
}
