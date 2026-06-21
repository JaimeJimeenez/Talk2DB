import os

DATABASE_URL: str = os.environ['DATABASE_URL']
LLM_MODEL: str = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-Coder-0.5B-Instruct")
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://vllm:8000/v1")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "EMPTY")

INFORMATION_SCHEMA_QUERY: str = """
    SELECT
        tc.table_name,
        kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    WHERE tc.table_schema = 'public'
        AND tc.constraint_type = 'PRIMARY KEY'
    ORDER BY tc.table_name, kcu.ordinal_position
"""

FOREIGN_QUERY: str = """
    SELECT
        kcu.table_name,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage ccu
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema
    WHERE tc.table_schema = 'public'
        AND tc.constraint_type = 'FOREIGN KEY'
    ORDER BY kcu.table_name, kcu.column_name
"""
