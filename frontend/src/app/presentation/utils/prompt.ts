import { QuerySchema } from '@domain/models/query-schema';
import { IDropdown } from '@interfaces/components/dropdown';

export function buildSchemaDropdown(
  schemas: QuerySchema[],
  selectedSchemaName: string,
  isLoading: boolean,
): IDropdown {
  return {
    label: selectedSchemaName,
    icon: { name: 'database', title: 'Schema', size: 16 },
    items: schemas.map(schema => ({
      id: schema.id,
      label: schema.name,
    })),
    emptyLabel: isLoading ? 'Loading...' : 'No schemas',
  };
}
