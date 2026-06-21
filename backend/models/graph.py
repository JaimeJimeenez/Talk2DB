from typing import Any, TypedDict

class DbGraphState(TypedDict):
    question: str
    schema: str
    sql: str
    command: str
    rows: list[dict[str, Any]]
    answer: str
