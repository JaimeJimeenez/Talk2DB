from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def seed_schema_context(container: Any) -> None:
    schemas_use_case = container.schemas_use_case()
    schema_loader = container.schema_loader()
    schema_context = container.schema_context()

    try:
        schemas = await schemas_use_case.get_schemas()
    except Exception as error:
        logger.warning("Could not load query schemas for RAG context bootstrap: %s", error)
        return

    indexed_documents = 0
    indexed_schemas = 0
    for query_schema in schemas:
        try:
            database_schema = await schema_loader.load_database_schema(query_schema.name)
            guidance = "\n\n".join(
                value.strip()
                for value in (query_schema.business_rules, query_schema.context)
                if value.strip()
            )
            indexed_documents += await schema_context.ensure_schema_index(
                database_schema,
                guidance=guidance,
            )
            indexed_schemas += 1
        except Exception as error:
            logger.warning(
                "Could not bootstrap RAG context for schema '%s': %s",
                query_schema.name,
                error,
            )

    if indexed_schemas:
        logger.info(
            "Bootstrapped RAG context for %s schemas and %s table documents.",
            indexed_schemas,
            indexed_documents,
        )
