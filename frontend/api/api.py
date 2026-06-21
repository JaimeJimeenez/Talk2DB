import os
from typing import Any

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("BACKEND_TIMEOUT_SECONDS", "60"))


def _format_history(history: list[Any]) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []

    for item in history:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant", "system"} and content:
                messages.append({"role": role, "content": str(content)})
            continue

        if isinstance(item, (list, tuple)) and len(item) >= 2:
            user_message, assistant_message = item[0], item[1]
            if user_message:
                messages.append({"role": "user", "content": str(user_message)})
            if assistant_message:
                messages.append({"role": "assistant", "content": str(assistant_message)})

    return messages


def completion(message: str, history: list[Any] | None = None) -> str:
    payload = {
        "message": message,
        "history": _format_history(history or []),
    }

    try:
        response = requests.post(
            f"{BACKEND_URL.rstrip('/')}/completion",
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return f"No he podido conectar con el backend: {exc}"

    data = response.json()
    answer = str(data.get("response", "El backend no devolvio una respuesta valida."))
    command = data.get("command")

    if command:
        answer += f"\n\nSQL generado:\n```sql\n{command}\n```"

    return answer
