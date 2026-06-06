import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { RagMetricsAdapter } from './rag-metrics';
import { ApiService } from '@infrastructure/api/api';

describe('RagMetricsAdapter', () => {
  let adapter: RagMetricsAdapter;
  let api: {
    get: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    api = {
      get: vi.fn((url: string) => {
        if (url === 'rag/metrics/runs') {
          return of([
            {
              id: 'run-1',
              created_at: '2026-06-03T10:00:00.000Z',
              status: 'error',
              schema_id: 'schema-1',
              schema_name: 'ventas',
              conversation_id: 'conversation-1',
              message_id: 'message-1',
              prompt: 'Ventas por mes',
              generated_sql: 'SELECT 1',
              error: 'Invalid SQL syntax',
              duration_ms: 300,
              attempt_count: 5,
              repair_count: 4,
              row_count: 0,
              used_context: true,
            },
          ]);
        }
        return of({
          total_runs: 3,
          successful_runs: 2,
          failed_runs: 1,
          success_rate: 0.6667,
          average_duration_ms: 250,
          average_repair_count: 0.33,
          average_row_count: 12,
          runs_by_day: [{ label: '2026-06-03', total: 3, successful: 2, failed: 1, average_duration_ms: 0 }],
          latency_by_day: [{ label: '2026-06-03', total: 3, successful: 0, failed: 0, average_duration_ms: 250 }],
          runs_by_schema: [{ schema_id: 'schema-1', schema_name: 'ventas', count: 3 }],
          errors_by_type: [{ label: 'Invalid SQL syntax', count: 1 }],
          row_count_buckets: [{ label: '0', count: 1 }],
        });
      }),
    };

    TestBed.configureTestingModule({
      providers: [
        RagMetricsAdapter,
        { provide: ApiService, useValue: api },
      ],
    });

    adapter = TestBed.inject(RagMetricsAdapter);
  });

  it('maps summary metrics from the API', () => {
    adapter.getSummary({ schemaId: 'schema-1' }).subscribe(summary => {
      expect(summary.totalRuns).toBe(3);
      expect(summary.averageDurationMs).toBe(250);
      expect(summary.runsBySchema[0].schemaName).toBe('ventas');
      expect(summary.runsByDay[0].successful).toBe(2);
    });

    expect(api.get).toHaveBeenCalledWith('rag/metrics/summary', { schema_id: 'schema-1' });
  });

  it('maps recent runs from the API', () => {
    adapter.getRuns({ status: 'error', limit: 10 }).subscribe(runs => {
      expect(runs[0].createdAt).toBeInstanceOf(Date);
      expect(runs[0].generatedSql).toBe('SELECT 1');
      expect(runs[0].usedContext).toBe(true);
    });

    expect(api.get).toHaveBeenCalledWith('rag/metrics/runs', { limit: 10, status: 'error' });
  });
});
