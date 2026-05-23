DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'talk2db_reader') THEN
        CREATE ROLE talk2db_reader LOGIN PASSWORD 'talk2db_reader';
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS query_schemas (
    id UUID PRIMARY KEY,
    name VARCHAR(63) NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    business_rules TEXT NOT NULL DEFAULT '',
    context TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    refreshed_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    role VARCHAR(16) NOT NULL CHECK (role IN ('user', 'admin'))
);

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    schema_id UUID NOT NULL REFERENCES query_schemas(id),
    user_id UUID NOT NULL REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(16) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    sql TEXT,
    error TEXT
);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_id
    ON messages (conversation_id);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_timestamp
    ON messages (conversation_id, timestamp, id);

CREATE INDEX IF NOT EXISTS ix_conversations_user_id
    ON conversations (user_id);

INSERT INTO users (id, username, email, password, created_at, role)
VALUES (
    '00000000-0000-0000-0000-000000000101',
    'demo_user',
    'demo@example.com',
    '$2b$12$NznAvhY250SQc4lkb9QfH.BSClwi9KJwVaAJJeMCEdVaOMZs4u6Ki',
    '2026-05-23T00:00:00Z',
    'user'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO query_schemas (id, name, description, business_rules, context, created_at, refreshed_at)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'ventas',
    'Schema demo para ventas',
    'Permite consultas de lectura sobre datos comerciales.',
    'Schema: ventas\nTable: customers\nColumns:\n- id uuid\n- name text\n- active boolean',
    '2026-05-23T00:00:00Z',
    '2026-05-23T00:00:00Z'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO conversations (id, title, created_at, schema_id, user_id)
VALUES (
    '00000000-0000-0000-0000-000000000201',
    'Conversacion demo',
    '2026-05-23T00:00:00Z',
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000101'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO messages (id, conversation_id, role, content, timestamp, sql, error)
VALUES
(
    '00000000-0000-0000-0000-000000000301',
    '00000000-0000-0000-0000-000000000201',
    'user',
    'Muestra los clientes activos',
    '2026-05-23T00:00:00Z',
    NULL,
    NULL
),
(
    '00000000-0000-0000-0000-000000000302',
    '00000000-0000-0000-0000-000000000201',
    'assistant',
    'Aqui tienes una consulta de ejemplo para clientes activos.',
    '2026-05-23T00:00:01Z',
    'SELECT * FROM ventas.customers WHERE active = true LIMIT 100',
    NULL
)
ON CONFLICT (id) DO NOTHING;

GRANT CONNECT ON DATABASE talk2db TO talk2db_reader;
