import json
from urllib import request


class OpenAITextClient:
    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def complete(self, instructions: str, prompt: str) -> str:
        payload = json.dumps(
            {"model": self._model, "instructions": instructions, "input": prompt}
        ).encode()
        req = request.Request(
            "https://api.openai.com/v1/responses",
            data=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=60) as response:
            body = json.loads(response.read().decode())
        return "".join(
            content["text"]
            for item in body.get("output", [])
            if item.get("type") == "message"
            for content in item.get("content", [])
            if content.get("type") == "output_text"
        )
