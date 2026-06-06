import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';

import { Metrics } from './metrics';
import { RagMetricsFacade } from '@domain/facades/rag-metrics';

describe('Metrics', () => {
  let fixture: ComponentFixture<Metrics>;
  const summary = signal({
    totalRuns: 3,
    successfulRuns: 2,
    failedRuns: 1,
    successRate: 0.6667,
    averageDurationMs: 250,
    averageRepairCount: 0.33,
    averageRowCount: 12,
    runsByDay: [{ label: '2026-06-03', total: 3, successful: 2, failed: 1, averageDurationMs: 0 }],
    latencyByDay: [{ label: '2026-06-03', total: 3, successful: 0, failed: 0, averageDurationMs: 250 }],
    runsBySchema: [{ schemaId: 'schema-1', schemaName: 'ventas', count: 3 }],
    errorsByType: [{ label: 'Invalid SQL syntax', count: 1 }],
    rowCountBuckets: [{ label: '0', count: 1 }],
  });
  const failedRuns = signal([
    {
      id: 'run-1',
      createdAt: new Date('2026-06-03T10:00:00.000Z'),
      status: 'error' as const,
      schemaId: 'schema-1',
      schemaName: 'ventas',
      conversationId: 'conversation-1',
      messageId: 'message-1',
      prompt: 'Ventas por mes',
      generatedSql: 'SELECT 1',
      error: 'Invalid SQL syntax',
      durationMs: 300,
      attemptCount: 5,
      repairCount: 4,
      rowCount: 0,
      usedContext: true,
    },
  ]);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Metrics],
      providers: [
        {
          provide: RagMetricsFacade,
          useValue: {
            summary: summary.asReadonly(),
            failedRuns: failedRuns.asReadonly(),
            isLoading: signal(false).asReadonly(),
            hasData: signal(true).asReadonly(),
            load: vi.fn(),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Metrics);
    fixture.detectChanges();
  });

  it('renders the metrics dashboard', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.textContent).toContain('Métricas RAG');
    expect(compiled.textContent).toContain('Completions');
    expect(compiled.textContent).toContain('67%');
    expect(compiled.textContent).toContain('Ventas por mes');
    expect(compiled.textContent).toContain('SELECT 1');
  });
});
