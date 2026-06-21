from fastapi import FastAPI

from models.chat import Completion, Response
from rag.builder import db_graph
from rag.sql import SqlGenerationError

app = FastAPI(title="Talk2DB Backend")

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/completion", response_model=Response)
async def completion(request: Completion) -> Response:
    try:
        result = db_graph.invoke({
            "question": request.message,
            "schema": "",
            "sql": "",
            "command": "",
            "rows": [],
            "answer": "",
        })
    except SqlGenerationError as exc:
        return Response(
            response=(
                "No he podido generar una consulta SQL de lectura valida para esa pregunta. "
                f"Detalle: {exc}"
            )
        )

    return Response(response=result["answer"], command=result.get("command"))
