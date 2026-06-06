import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { QuerySchema, QuerySchemaDetail, QuerySchemaTable } from '@domain/models/query-schema';
import { QuerySchemaPort } from '@domain/ports/query-schema';
import { Icon } from '@components/icon/icon';
import { AlertsService } from '@services/alerts';

@Component({
  selector: 'talk2db-schema',
  imports: [FormsModule, Icon],
  templateUrl: './schema.html',
  styleUrl: './schema.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Schema {
  private readonly _schemas = inject(QuerySchemaPort);
  private readonly _alerts = inject(AlertsService);

  readonly schemas = signal<QuerySchema[]>([]);
  readonly selectedSchema = signal<QuerySchemaDetail | null>(null);
  readonly selectedSchemaId = signal('');
  readonly isLoading = signal(false);
  readonly isLoadingDetail = signal(false);
  readonly isImporting = signal(false);
  readonly loadError = signal(false);
  readonly showImportPanel = signal(false);

  readonly importName = signal('');
  readonly importDescription = signal('');
  readonly importBusinessRules = signal('');
  readonly importFile = signal<File | null>(null);

  readonly selectedTables = computed(() => this.selectedSchema()?.tables ?? []);
  readonly hasSchemas = computed(() => this.schemas().length > 0);
  readonly canImport = computed(() =>
    !!this.importName().trim()
    && !!this.importFile()
    && !this.isImporting()
  );

  constructor() {
    this.loadSchemas();
  }

  loadSchemas(): void {
    this.isLoading.set(true);
    this.loadError.set(false);
    this._schemas.getSchemas()
      .pipe(finalize(() => this.isLoading.set(false)))
      .subscribe({
        next: schemas => {
          this.schemas.set(schemas);
          const nextId = this.selectedSchemaId() || schemas[0]?.id || '';
          if (nextId) {
            this.selectSchema(nextId);
          } else {
            this.selectedSchema.set(null);
          }
        },
        error: () => {
          this.loadError.set(true);
          this._alerts.error('Error', 'No se han podido cargar los schemas.');
        },
      });
  }

  selectSchema(schemaId: string): void {
    if (!schemaId) return;
    this.selectedSchemaId.set(schemaId);
    this.isLoadingDetail.set(true);
    this._schemas.getSchemaDetail(schemaId)
      .pipe(finalize(() => this.isLoadingDetail.set(false)))
      .subscribe({
        next: schema => this.selectedSchema.set(schema),
        error: () => this._alerts.error('Error', 'No se ha podido cargar el detalle del schema.'),
      });
  }

  toggleImportPanel(): void {
    this.showImportPanel.update(value => !value);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.importFile.set(input.files?.[0] ?? null);
  }

  importSchema(): void {
    const file = this.importFile();
    if (!file || !this.importName().trim()) {
      this._alerts.warning('Faltan datos', 'Introduce un nombre y selecciona un fichero .sql.');
      return;
    }

    this.isImporting.set(true);
    this._schemas.importSchema({
      name: this.importName().trim(),
      description: this.importDescription().trim(),
      businessRules: this.importBusinessRules().trim(),
      file,
    })
      .pipe(finalize(() => this.isImporting.set(false)))
      .subscribe({
        next: schema => {
          this._alerts.success('Schema importado', `${schema.name} ya está disponible para RAG.`);
          this._resetImportForm();
          this.showImportPanel.set(false);
          this.selectedSchemaId.set(schema.id);
          this.loadSchemas();
        },
        error: error => {
          const detail = error?.error?.detail || 'El fichero SQL no ha pasado las validaciones.';
          this._alerts.error('Importación rechazada', detail);
        },
      });
  }

  trackBySchema(index: number, schema: QuerySchema): string {
    return schema.id || `${schema.name}-${index}`;
  }

  trackByTable(index: number, table: QuerySchemaTable): string {
    return table.name || `${index}`;
  }

  private _resetImportForm(): void {
    this.importName.set('');
    this.importDescription.set('');
    this.importBusinessRules.set('');
    this.importFile.set(null);
  }
}
