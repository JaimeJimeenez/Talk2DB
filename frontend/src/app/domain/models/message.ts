export type MessageRole = 'user' | 'assistant';

export interface QueryArtifactColumn {
    readonly name: string;
    readonly type: string;
}

export interface QueryArtifact {
    readonly id: string;
    readonly title: string;
    readonly summary: string;
    readonly type: 'query_result';
    readonly generatedFrom: string;
    readonly sql: string | null;
    readonly columns: QueryArtifactColumn[];
    readonly rows: Record<string, unknown>[];
    readonly rowCount: number;
    readonly truncated: boolean;
    readonly error: string | null;
}

export interface Message {
    readonly id: string;
    readonly role: MessageRole;
    readonly content: string;
    readonly timestamp: Date;
    readonly sql?: string | null;
    readonly error?: string | null;
    readonly artifact?: QueryArtifact | null;
    readonly conversationTitle?: string | null;
}
