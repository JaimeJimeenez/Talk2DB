export interface QuerySchema {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly business_rules: string;
  readonly created_at: string;
  readonly refreshed_at: string;
  readonly table_count: number;
  readonly column_count: number;
}

export interface QuerySchemaColumn {
  readonly name: string;
  readonly data_type: string;
  readonly nullable: boolean;
  readonly default?: string | null;
}

export interface QuerySchemaConstraint {
  readonly column: string;
  readonly foreign_table_schema: string;
  readonly foreign_table_name: string;
  readonly foreign_column_name: string;
}

export interface QuerySchemaTable {
  readonly name: string;
  readonly columns: QuerySchemaColumn[];
  readonly constraints: QuerySchemaConstraint[];
}

export interface QuerySchemaDetail extends QuerySchema {
  readonly tables: QuerySchemaTable[];
}

export interface ImportQuerySchemaPayload {
  readonly name: string;
  readonly description: string;
  readonly businessRules: string;
  readonly file: File;
}
