from langgraph.graph import END, START, StateGraph

from rag.sql import generate_sql, validate_sql, execute_sql, write_answer
from rag.schema import read_schema
from models.graph import DbGraphState

def build_graph():
    builder = StateGraph(DbGraphState)

    builder.add_node("read_schema", read_schema)
    builder.add_node("generate_sql", generate_sql)
    builder.add_node("validate_sql", validate_sql)
    builder.add_node("execute_sql", execute_sql)
    builder.add_node("write_answer", write_answer)

    builder.add_edge(START, "read_schema")
    builder.add_edge("read_schema", "generate_sql")
    builder.add_edge("generate_sql", "validate_sql")
    builder.add_edge("validate_sql", "execute_sql")
    builder.add_edge("execute_sql", "write_answer")
    builder.add_edge("write_answer", END)

    db_graph = builder.compile()
    return db_graph

db_graph = build_graph()