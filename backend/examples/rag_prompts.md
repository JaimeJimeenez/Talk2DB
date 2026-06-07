# RAG demo prompts

`backend/schema.sql` initializes PostgreSQL with two queryable demo domains:

- `ventas`: clientes, productos, pedidos and lineas_pedido.
- `soporte`: clientes, agentes, tickets and interacciones.

At backend startup, Talk2DB also warms the Qdrant `schema_context` collection for the registered `query_schemas`. If Qdrant or Ollama is not ready yet, startup continues and the same index is built lazily on the first RAG query.

## Ventas

- Muestra los clientes activos.
- Que producto ha generado mas ingresos?
- Ventas por mes excluyendo pedidos cancelados.
- Ingresos por canal de venta.
- Margen por categoria de producto.
- Clientes con mas ingresos acumulados.
- Pedidos pendientes con nombre de cliente.
- Ticket medio por pedido pagado o enviado.
- Comparame ingresos de software frente a servicios.
- Que ciudades tienen mas clientes activos?

## Soporte

- Tickets abiertos por prioridad.
- Tickets creados por mes.
- Tiempo medio de resolucion por categoria.
- Minutos de soporte por canal.
- Satisfaccion media por agente.
- Clientes enterprise con tickets criticos abiertos.
- Carga de tickets por equipo de soporte.
- Agentes con mas tickets resueltos.
- Evolucion mensual de tickets cerrados.
- Tickets sin cerrar con nombre de cliente y agente.

## Follow-up examples

1. Ventas por mes excluyendo pedidos cancelados.
2. Ahora separalo por canal.
3. Dame solo el mes con mas ingresos.

1. Tickets abiertos por prioridad.
2. Para esos tickets, dime que agentes los llevan.
3. Y cuanto tiempo de interacciones acumulan por canal?

## Optional imported schema

`backend/examples/logistica_demo.sql` is an extra schema intended to test the admin import flow. It is not loaded by default in `backend/schema.sql`.
