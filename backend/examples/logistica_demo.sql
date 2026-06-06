CREATE SCHEMA logistica_demo;

CREATE TABLE logistica_demo.clientes (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    segmento TEXT NOT NULL CHECK (segmento IN ('retail', 'empresa', 'mayorista')),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE logistica_demo.almacenes (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    capacidad_unidades INTEGER NOT NULL CHECK (capacidad_unidades > 0)
);

CREATE TABLE logistica_demo.productos (
    id TEXT PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    peso_kg NUMERIC(10, 2) NOT NULL CHECK (peso_kg > 0)
);

CREATE TABLE logistica_demo.envios (
    id TEXT PRIMARY KEY,
    cliente_id TEXT NOT NULL REFERENCES logistica_demo.clientes(id),
    almacen_id TEXT NOT NULL REFERENCES logistica_demo.almacenes(id),
    fecha_envio DATE NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('preparacion', 'en_transito', 'entregado', 'cancelado')),
    transportista TEXT NOT NULL,
    coste_envio NUMERIC(12, 2) NOT NULL CHECK (coste_envio >= 0)
);

CREATE TABLE logistica_demo.lineas_envio (
    id TEXT PRIMARY KEY,
    envio_id TEXT NOT NULL REFERENCES logistica_demo.envios(id),
    producto_id TEXT NOT NULL REFERENCES logistica_demo.productos(id),
    cantidad INTEGER NOT NULL CHECK (cantidad > 0)
);

CREATE INDEX ix_logistica_demo_envios_cliente
    ON logistica_demo.envios(cliente_id);

CREATE INDEX ix_logistica_demo_envios_estado
    ON logistica_demo.envios(estado);

INSERT INTO logistica_demo.clientes (id, nombre, ciudad, segmento, activo)
VALUES
    ('c001', 'Mercado Norte', 'Madrid', 'retail', TRUE),
    ('c002', 'Iberia Foods', 'Barcelona', 'empresa', TRUE),
    ('c003', 'Costa Distribucion', 'Valencia', 'mayorista', TRUE),
    ('c004', 'Rutas del Sur', 'Sevilla', 'empresa', FALSE),
    ('c005', 'Bilbao Market', 'Bilbao', 'retail', TRUE);

INSERT INTO logistica_demo.almacenes (id, nombre, ciudad, capacidad_unidades)
VALUES
    ('a001', 'Centro Madrid', 'Madrid', 12000),
    ('a002', 'Hub Mediterraneo', 'Valencia', 18000),
    ('a003', 'Norte Express', 'Bilbao', 9000);

INSERT INTO logistica_demo.productos (id, sku, nombre, categoria, peso_kg)
VALUES
    ('p001', 'SKU-CAF-001', 'Cafe premium', 'alimentacion', 0.50),
    ('p002', 'SKU-ACE-002', 'Aceite oliva', 'alimentacion', 1.20),
    ('p003', 'SKU-EMB-003', 'Caja isotermica', 'embalaje', 2.10),
    ('p004', 'SKU-LIM-004', 'Kit limpieza', 'hogar', 3.40),
    ('p005', 'SKU-TEC-005', 'Sensor temperatura', 'tecnologia', 0.30);

INSERT INTO logistica_demo.envios (id, cliente_id, almacen_id, fecha_envio, estado, transportista, coste_envio)
VALUES
    ('e001', 'c001', 'a001', '2026-05-02', 'entregado', 'DHL', 34.90),
    ('e002', 'c002', 'a002', '2026-05-04', 'en_transito', 'SEUR', 82.50),
    ('e003', 'c003', 'a002', '2026-05-10', 'entregado', 'DHL', 120.00),
    ('e004', 'c001', 'a003', '2026-05-14', 'preparacion', 'Correos Express', 28.75),
    ('e005', 'c005', 'a003', '2026-05-18', 'cancelado', 'SEUR', 0.00),
    ('e006', 'c002', 'a001', '2026-05-22', 'en_transito', 'DHL', 65.20);

INSERT INTO logistica_demo.lineas_envio (id, envio_id, producto_id, cantidad)
VALUES
    ('l001', 'e001', 'p001', 40),
    ('l002', 'e001', 'p002', 20),
    ('l003', 'e002', 'p003', 12),
    ('l004', 'e002', 'p005', 50),
    ('l005', 'e003', 'p001', 120),
    ('l006', 'e003', 'p004', 25),
    ('l007', 'e004', 'p002', 10),
    ('l008', 'e005', 'p005', 15),
    ('l009', 'e006', 'p003', 8),
    ('l010', 'e006', 'p004', 18);
