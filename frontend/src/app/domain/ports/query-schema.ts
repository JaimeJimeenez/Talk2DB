import { Observable } from 'rxjs';

import { ImportQuerySchemaPayload, QuerySchema, QuerySchemaDetail } from '@domain/models/query-schema';

export abstract class QuerySchemaPort {
  abstract getSchemas(): Observable<QuerySchema[]>;
  abstract getSchemaDetail(schemaId: string): Observable<QuerySchemaDetail>;
  abstract importSchema(payload: ImportQuerySchemaPayload): Observable<QuerySchemaDetail>;
}
