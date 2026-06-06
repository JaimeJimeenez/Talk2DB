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
    error TEXT,
    artifact JSONB
);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_id
    ON messages (conversation_id);

CREATE INDEX IF NOT EXISTS ix_messages_conversation_timestamp
    ON messages (conversation_id, timestamp, id);

CREATE INDEX IF NOT EXISTS ix_conversations_user_id
    ON conversations (user_id);

ALTER TABLE messages
    ADD COLUMN IF NOT EXISTS artifact JSONB;

CREATE TABLE IF NOT EXISTS rag_runs (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    schema_id UUID NOT NULL REFERENCES query_schemas(id),
    schema_name VARCHAR(63) NOT NULL DEFAULT '',
    prompt TEXT NOT NULL,
    status VARCHAR(16) NOT NULL CHECK (status IN ('success', 'error')),
    created_at TIMESTAMPTZ NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    repair_count INTEGER NOT NULL DEFAULT 0,
    sql_validated BOOLEAN NOT NULL DEFAULT FALSE,
    sql_executed BOOLEAN NOT NULL DEFAULT FALSE,
    generated_sql TEXT,
    error TEXT,
    row_count INTEGER NOT NULL DEFAULT 0,
    truncated BOOLEAN NOT NULL DEFAULT FALSE,
    used_context BOOLEAN NOT NULL DEFAULT FALSE,
    context_message_count INTEGER NOT NULL DEFAULT 0,
    model VARCHAR(255) NOT NULL DEFAULT '',
    retrieved_table_count INTEGER NOT NULL DEFAULT 0,
    retrieved_tables JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE INDEX IF NOT EXISTS ix_rag_runs_created_at
    ON rag_runs (created_at);

CREATE INDEX IF NOT EXISTS ix_rag_runs_status
    ON rag_runs (status);

CREATE INDEX IF NOT EXISTS ix_rag_runs_schema_id
    ON rag_runs (schema_id);

CREATE INDEX IF NOT EXISTS ix_rag_runs_user_id
    ON rag_runs (user_id);

CREATE SCHEMA IF NOT EXISTS ventas;

CREATE TABLE IF NOT EXISTS ventas.clientes (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    segmento TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_alta DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas.productos (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    precio NUMERIC(12, 2) NOT NULL,
    coste NUMERIC(12, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas.pedidos (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES ventas.clientes(id),
    fecha DATE NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('pendiente', 'pagado', 'enviado', 'cancelado')),
    canal TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas.lineas_pedido (
    id TEXT PRIMARY KEY,
    pedido_id TEXT NOT NULL REFERENCES ventas.pedidos(id),
    producto_id TEXT NOT NULL REFERENCES ventas.productos(id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12, 2) NOT NULL
);

INSERT INTO ventas.clientes (id, nombre, segmento, ciudad, activo, fecha_alta)
VALUES
    ('c001', 'Acme Retail', 'retail', 'Madrid', TRUE, '2025-01-15'),
    ('c002', 'Northwind Labs', 'enterprise', 'Barcelona', TRUE, '2025-02-20'),
    ('c003', 'Iberia Market', 'retail', 'Valencia', TRUE, '2025-03-08'),
    ('c004', 'Costa Azul Hotels', 'hospitality', 'Malaga', FALSE, '2024-11-02'),
    ('c005', 'Data Norte', 'enterprise', 'Bilbao', TRUE, '2025-05-18')
ON CONFLICT (id) DO NOTHING;

INSERT INTO ventas.productos (id, nombre, categoria, precio, coste)
VALUES
    ('p001', 'Starter Analytics', 'software', 120.00, 25.00),
    ('p002', 'Pro Analytics', 'software', 280.00, 60.00),
    ('p003', 'Soporte Premium', 'servicios', 450.00, 180.00),
    ('p004', 'Onboarding', 'servicios', 800.00, 320.00),
    ('p005', 'Conector ERP', 'integraciones', 350.00, 90.00)
ON CONFLICT (id) DO NOTHING;

INSERT INTO ventas.pedidos (id, cliente_id, fecha, estado, canal)
VALUES
    ('o001', 'c001', '2026-01-12', 'pagado', 'web'),
    ('o002', 'c002', '2026-01-28', 'enviado', 'ventas'),
    ('o003', 'c003', '2026-02-09', 'pendiente', 'web'),
    ('o004', 'c001', '2026-02-22', 'pagado', 'partner'),
    ('o005', 'c005', '2026-03-05', 'pendiente', 'ventas'),
    ('o006', 'c002', '2026-03-18', 'cancelado', 'web'),
    ('o007', 'c003', '2026-04-03', 'pagado', 'web'),
    ('o008', 'c005', '2026-04-17', 'enviado', 'ventas')
ON CONFLICT (id) DO NOTHING;

INSERT INTO ventas.lineas_pedido (id, pedido_id, producto_id, cantidad, precio_unitario)
VALUES
    ('l001', 'o001', 'p001', 3, 120.00),
    ('l002', 'o001', 'p003', 1, 450.00),
    ('l003', 'o002', 'p002', 5, 280.00),
    ('l004', 'o002', 'p005', 2, 350.00),
    ('l005', 'o003', 'p001', 2, 120.00),
    ('l006', 'o003', 'p004', 1, 800.00),
    ('l007', 'o004', 'p002', 2, 280.00),
    ('l008', 'o005', 'p005', 4, 350.00),
    ('l009', 'o006', 'p003', 1, 450.00),
    ('l010', 'o007', 'p002', 3, 280.00),
    ('l011', 'o007', 'p004', 1, 800.00),
    ('l012', 'o008', 'p003', 2, 450.00),
    ('l013', 'o008', 'p005', 1, 350.00)
ON CONFLICT (id) DO NOTHING;

GRANT USAGE ON SCHEMA ventas TO talk2db_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA ventas TO talk2db_reader;

CREATE SCHEMA IF NOT EXISTS soporte;

CREATE TABLE IF NOT EXISTS soporte.clientes (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    plan TEXT NOT NULL CHECK (plan IN ('starter', 'business', 'enterprise')),
    region TEXT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS soporte.agentes (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    equipo TEXT NOT NULL,
    nivel TEXT NOT NULL CHECK (nivel IN ('junior', 'senior', 'lead'))
);

CREATE TABLE IF NOT EXISTS soporte.tickets (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES soporte.clientes(id),
    agente_id TEXT NOT NULL REFERENCES soporte.agentes(id),
    creado_en DATE NOT NULL,
    cerrado_en DATE,
    prioridad TEXT NOT NULL CHECK (prioridad IN ('baja', 'media', 'alta', 'critica')),
    estado TEXT NOT NULL CHECK (estado IN ('abierto', 'en_progreso', 'resuelto', 'cerrado')),
    categoria TEXT NOT NULL,
    satisfaccion INTEGER CHECK (satisfaccion BETWEEN 1 AND 5)
);

CREATE TABLE IF NOT EXISTS soporte.interacciones (
    id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES soporte.tickets(id),
    canal TEXT NOT NULL CHECK (canal IN ('email', 'chat', 'telefono')),
    fecha DATE NOT NULL,
    minutos INTEGER NOT NULL CHECK (minutos > 0)
);

INSERT INTO soporte.clientes (id, nombre, plan, region, activo)
VALUES
    ('sc001', 'Acme Retail', 'business', 'Madrid', TRUE),
    ('sc002', 'Northwind Labs', 'enterprise', 'Barcelona', TRUE),
    ('sc003', 'Iberia Market', 'starter', 'Valencia', TRUE),
    ('sc004', 'Costa Azul Hotels', 'business', 'Malaga', FALSE),
    ('sc005', 'Data Norte', 'enterprise', 'Bilbao', TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO soporte.agentes (id, nombre, equipo, nivel)
VALUES
    ('sa001', 'Lucia Ramos', 'producto', 'senior'),
    ('sa002', 'Mario Soto', 'billing', 'lead'),
    ('sa003', 'Nerea Vidal', 'integraciones', 'senior'),
    ('sa004', 'Pablo Ruiz', 'producto', 'junior')
ON CONFLICT (id) DO NOTHING;

INSERT INTO soporte.tickets (id, cliente_id, agente_id, creado_en, cerrado_en, prioridad, estado, categoria, satisfaccion)
VALUES
    ('st001', 'sc001', 'sa001', '2026-01-08', '2026-01-09', 'media', 'cerrado', 'producto', 5),
    ('st002', 'sc002', 'sa003', '2026-01-18', '2026-01-22', 'alta', 'resuelto', 'integracion', 4),
    ('st003', 'sc003', 'sa002', '2026-02-04', '2026-02-04', 'baja', 'cerrado', 'facturacion', 5),
    ('st004', 'sc001', 'sa001', '2026-02-13', NULL, 'alta', 'en_progreso', 'producto', NULL),
    ('st005', 'sc005', 'sa003', '2026-03-03', '2026-03-07', 'critica', 'cerrado', 'integracion', 3),
    ('st006', 'sc002', 'sa002', '2026-03-16', '2026-03-17', 'media', 'cerrado', 'facturacion', 4),
    ('st007', 'sc005', 'sa004', '2026-04-02', NULL, 'media', 'abierto', 'producto', NULL),
    ('st008', 'sc003', 'sa004', '2026-04-11', '2026-04-12', 'baja', 'cerrado', 'producto', 4),
    ('st009', 'sc002', 'sa003', '2026-05-06', NULL, 'critica', 'en_progreso', 'integracion', NULL)
ON CONFLICT (id) DO NOTHING;

INSERT INTO soporte.interacciones (id, ticket_id, canal, fecha, minutos)
VALUES
    ('si001', 'st001', 'chat', '2026-01-08', 18),
    ('si002', 'st001', 'email', '2026-01-09', 12),
    ('si003', 'st002', 'email', '2026-01-18', 35),
    ('si004', 'st002', 'telefono', '2026-01-21', 42),
    ('si005', 'st003', 'chat', '2026-02-04', 9),
    ('si006', 'st004', 'chat', '2026-02-13', 25),
    ('si007', 'st004', 'email', '2026-02-14', 16),
    ('si008', 'st005', 'telefono', '2026-03-03', 50),
    ('si009', 'st005', 'email', '2026-03-06', 28),
    ('si010', 'st006', 'chat', '2026-03-16', 14),
    ('si011', 'st007', 'email', '2026-04-02', 20),
    ('si012', 'st008', 'chat', '2026-04-11', 11),
    ('si013', 'st009', 'telefono', '2026-05-06', 55),
    ('si014', 'st009', 'email', '2026-05-08', 24)
ON CONFLICT (id) DO NOTHING;

GRANT USAGE ON SCHEMA soporte TO talk2db_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA soporte TO talk2db_reader;

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

INSERT INTO users (id, username, email, password, created_at, role)
VALUES (
    'a4cc9eb6-7db6-487f-a86a-228fc7244ebe',
    'Jaime Jimenez',
    'jaime@talk2db.com',
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
    'Schema: ventas
Table: clientes
Columns:
- id text
- nombre text
- segmento text
- ciudad text
- activo boolean
- fecha_alta date

Table: productos
Columns:
- id text
- nombre text
- categoria text
- precio numeric
- coste numeric

Table: pedidos
Columns:
- id text
- cliente_id text references ventas.clientes(id)
- fecha date
- estado text values: pendiente, pagado, enviado, cancelado
- canal text

Table: lineas_pedido
Columns:
- id text
- pedido_id text references ventas.pedidos(id)
- producto_id text references ventas.productos(id)
- cantidad integer
- precio_unitario numeric

Business rules:
- Los ingresos se calculan como lineas_pedido.cantidad * lineas_pedido.precio_unitario.
- Excluye pedidos cancelados de metricas de ventas salvo que el usuario los pida explicitamente.
- Clientes activos son clientes.activo = true.
- Para relacionar ingresos con clientes, une lineas_pedido.pedido_id = pedidos.id y pedidos.cliente_id = clientes.id.
- El estado del pedido esta en pedidos.estado, no en lineas_pedido.
- lineas_pedido no tiene cliente_id ni estado.
Examples:
- Pregunta: ¿Qué producto ha generado más ingresos?
  SQL esperado: agrupar lineas_pedido por productos.nombre, unir pedidos para excluir estado cancelado y ordenar por ingresos descendentes.
- Pregunta: Ventas por mes.
  SQL esperado: DATE_TRUNC sobre pedidos.fecha y SUM(cantidad * precio_unitario) excluyendo cancelados.',
    '2026-05-23T00:00:00Z',
    '2026-05-23T00:00:00Z'
)
ON CONFLICT (id) DO UPDATE
SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    business_rules = EXCLUDED.business_rules,
    context = EXCLUDED.context,
    refreshed_at = EXCLUDED.refreshed_at;

INSERT INTO query_schemas (id, name, description, business_rules, context, created_at, refreshed_at)
VALUES (
    '00000000-0000-0000-0000-000000000002',
    'soporte',
    'Schema demo para soporte al cliente',
    'Permite consultas de lectura sobre tickets, agentes, clientes e interacciones de soporte.',
    'Schema: soporte
Table: clientes
Columns:
- id text
- nombre text
- plan text values: starter, business, enterprise
- region text
- activo boolean

Table: agentes
Columns:
- id text
- nombre text
- equipo text
- nivel text values: junior, senior, lead

Table: tickets
Columns:
- id text
- cliente_id text references soporte.clientes(id)
- agente_id text references soporte.agentes(id)
- creado_en date
- cerrado_en date nullable
- prioridad text values: baja, media, alta, critica
- estado text values: abierto, en_progreso, resuelto, cerrado
- categoria text
- satisfaccion integer nullable values 1 to 5

Table: interacciones
Columns:
- id text
- ticket_id text references soporte.tickets(id)
- canal text values: email, chat, telefono
- fecha date
- minutos integer

Business rules:
- Tickets abiertos son tickets.estado IN (''abierto'', ''en_progreso'').
- Tickets resueltos son tickets.estado IN (''resuelto'', ''cerrado'').
- El tiempo de resolucion en dias se calcula como tickets.cerrado_en - tickets.creado_en solo cuando cerrado_en no es null.
- La carga de soporte por canal se calcula desde soporte.interacciones.
- Para metricas por cliente, une tickets.cliente_id = clientes.id.
- Para metricas por agente, une tickets.agente_id = agentes.id.
- Para metricas graficables, devuelve una columna de categoria o mes y una columna numerica agregada.
Examples:
- Pregunta: Tickets creados por mes.
  SQL esperado: DATE_TRUNC sobre tickets.creado_en y COUNT(*) agrupado por mes.
- Pregunta: Minutos de soporte por canal.
  SQL esperado: agrupar soporte.interacciones por canal y sumar minutos.',
    '2026-05-23T00:00:00Z',
    '2026-05-23T00:00:00Z'
)
ON CONFLICT (id) DO UPDATE
SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    business_rules = EXCLUDED.business_rules,
    context = EXCLUDED.context,
    refreshed_at = EXCLUDED.refreshed_at;

INSERT INTO conversations (id, title, created_at, schema_id, user_id)
VALUES (
    '00000000-0000-0000-0000-000000000201',
    'Conversacion demo',
    '2026-05-23T00:00:00Z',
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000101'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO messages (id, conversation_id, role, content, timestamp, sql, error, artifact)
VALUES
(
    '00000000-0000-0000-0000-000000000301',
    '00000000-0000-0000-0000-000000000201',
    'user',
    'Muestra los clientes activos',
    '2026-05-23T00:00:00Z',
    NULL,
    NULL,
    NULL
),
(
    '00000000-0000-0000-0000-000000000302',
    '00000000-0000-0000-0000-000000000201',
    'assistant',
    'Aqui tienes una consulta de ejemplo para clientes activos.',
    '2026-05-23T00:00:01Z',
    'SELECT id, nombre, segmento, ciudad, activo FROM ventas.clientes WHERE activo = true LIMIT 100',
    NULL,
    '{
        "id": "00000000-0000-0000-0000-000000000401",
        "title": "Clientes activos",
        "summary": "Aqui tienes una consulta de ejemplo para clientes activos.",
        "type": "query_result",
        "generatedFrom": "Muestra los clientes activos",
        "sql": "SELECT id, nombre, segmento, ciudad, activo FROM ventas.clientes WHERE activo = true LIMIT 100",
        "columns": [
            { "name": "id", "type": "str" },
            { "name": "nombre", "type": "str" },
            { "name": "segmento", "type": "str" },
            { "name": "ciudad", "type": "str" },
            { "name": "activo", "type": "bool" }
        ],
        "rows": [
            { "id": "c001", "nombre": "Acme Retail", "segmento": "retail", "ciudad": "Madrid", "activo": true },
            { "id": "c002", "nombre": "Northwind Labs", "segmento": "enterprise", "ciudad": "Barcelona", "activo": true },
            { "id": "c003", "nombre": "Iberia Market", "segmento": "retail", "ciudad": "Valencia", "activo": true },
            { "id": "c005", "nombre": "Data Norte", "segmento": "enterprise", "ciudad": "Bilbao", "activo": true }
        ],
        "rowCount": 4,
        "truncated": false,
        "error": null
    }'::jsonb
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO conversations (id, title, created_at, schema_id, user_id)
VALUES (
    '00000000-0000-0000-0000-000000000202',
    'Simulacion de ventas',
    '2026-05-23T00:05:00Z',
    '00000000-0000-0000-0000-000000000001',
    'a4cc9eb6-7db6-487f-a86a-228fc7244ebe'
)
ON CONFLICT (id) DO NOTHING;

UPDATE conversations
SET user_id = 'a4cc9eb6-7db6-487f-a86a-228fc7244ebe'
WHERE id = '00000000-0000-0000-0000-000000000202';

INSERT INTO messages (id, conversation_id, role, content, timestamp, sql, error, artifact)
VALUES
(
    '00000000-0000-0000-0000-000000000303',
    '00000000-0000-0000-0000-000000000202',
    'user',
    'Quiero revisar los clientes activos del schema de ventas',
    '2026-05-23T00:05:00Z',
    NULL,
    NULL,
    NULL
),
(
    '00000000-0000-0000-0000-000000000304',
    '00000000-0000-0000-0000-000000000202',
    'assistant',
    'He preparado una consulta de lectura para listar clientes activos.',
    '2026-05-23T00:05:01Z',
    'SELECT id, nombre FROM ventas.clientes WHERE activo = true LIMIT 100',
    NULL,
    '{
        "id": "00000000-0000-0000-0000-000000000402",
        "title": "Clientes activos del schema ventas",
        "summary": "He preparado una consulta de lectura para listar clientes activos.",
        "type": "query_result",
        "generatedFrom": "Quiero revisar los clientes activos del schema de ventas",
        "sql": "SELECT id, nombre FROM ventas.clientes WHERE activo = true LIMIT 100",
        "columns": [
            { "name": "id", "type": "str" },
            { "name": "nombre", "type": "str" }
        ],
        "rows": [
            { "id": "c001", "nombre": "Acme Retail" },
            { "id": "c002", "nombre": "Northwind Labs" },
            { "id": "c003", "nombre": "Iberia Market" },
            { "id": "c005", "nombre": "Data Norte" }
        ],
        "rowCount": 4,
        "truncated": false,
        "error": null
    }'::jsonb
)
ON CONFLICT (id) DO NOTHING;

UPDATE messages
SET artifact = '{
    "id": "00000000-0000-0000-0000-000000000401",
    "title": "Clientes activos",
    "summary": "Aqui tienes una consulta de ejemplo para clientes activos.",
    "type": "query_result",
    "generatedFrom": "Muestra los clientes activos",
    "sql": "SELECT id, nombre, segmento, ciudad, activo FROM ventas.clientes WHERE activo = true LIMIT 100",
    "columns": [
        { "name": "id", "type": "str" },
        { "name": "nombre", "type": "str" },
        { "name": "segmento", "type": "str" },
        { "name": "ciudad", "type": "str" },
        { "name": "activo", "type": "bool" }
    ],
    "rows": [
        { "id": "c001", "nombre": "Acme Retail", "segmento": "retail", "ciudad": "Madrid", "activo": true },
        { "id": "c002", "nombre": "Northwind Labs", "segmento": "enterprise", "ciudad": "Barcelona", "activo": true },
        { "id": "c003", "nombre": "Iberia Market", "segmento": "retail", "ciudad": "Valencia", "activo": true },
        { "id": "c005", "nombre": "Data Norte", "segmento": "enterprise", "ciudad": "Bilbao", "activo": true }
    ],
    "rowCount": 4,
    "truncated": false,
    "error": null
}'::jsonb
WHERE id = '00000000-0000-0000-0000-000000000302'
  AND artifact IS NULL;

UPDATE messages
SET artifact = '{
    "id": "00000000-0000-0000-0000-000000000402",
    "title": "Clientes activos del schema ventas",
    "summary": "He preparado una consulta de lectura para listar clientes activos.",
    "type": "query_result",
    "generatedFrom": "Quiero revisar los clientes activos del schema de ventas",
    "sql": "SELECT id, nombre FROM ventas.clientes WHERE activo = true LIMIT 100",
    "columns": [
        { "name": "id", "type": "str" },
        { "name": "nombre", "type": "str" }
    ],
    "rows": [
        { "id": "c001", "nombre": "Acme Retail" },
        { "id": "c002", "nombre": "Northwind Labs" },
        { "id": "c003", "nombre": "Iberia Market" },
        { "id": "c005", "nombre": "Data Norte" }
    ],
    "rowCount": 4,
    "truncated": false,
    "error": null
}'::jsonb
WHERE id = '00000000-0000-0000-0000-000000000304'
  AND artifact IS NULL;

GRANT CONNECT ON DATABASE talk2db TO talk2db_reader;
