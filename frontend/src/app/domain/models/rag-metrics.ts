export type RagRunStatus = 'success' | 'error';

export interface RagMetricPoint {
  readonly label: string;
  readonly total: number;
  readonly successful: number;
  readonly failed: number;
  readonly averageDurationMs: number;
}

export interface RagMetricBucket {
  readonly label: string;
  readonly count: number;
}

export interface RagSchemaMetric {
  readonly schemaId: string;
  readonly schemaName: string;
  readonly count: number;
}

export interface RagMetricsSummary {
  readonly totalRuns: number;
  readonly successfulRuns: number;
  readonly failedRuns: number;
  readonly successRate: number;
  readonly averageDurationMs: number;
  readonly averageRepairCount: number;
  readonly averageRowCount: number;
  readonly runsByDay: RagMetricPoint[];
  readonly latencyByDay: RagMetricPoint[];
  readonly runsBySchema: RagSchemaMetric[];
  readonly errorsByType: RagMetricBucket[];
  readonly rowCountBuckets: RagMetricBucket[];
}

export interface RagRun {
  readonly id: string;
  readonly createdAt: Date;
  readonly status: RagRunStatus;
  readonly schemaId: string;
  readonly schemaName: string;
  readonly conversationId: string;
  readonly messageId: string;
  readonly prompt: string;
  readonly generatedSql: string | null;
  readonly error: string | null;
  readonly durationMs: number;
  readonly attemptCount: number;
  readonly repairCount: number;
  readonly rowCount: number;
  readonly usedContext: boolean;
}

export interface RagMetricsFilters {
  readonly from?: string;
  readonly to?: string;
  readonly schemaId?: string;
}
