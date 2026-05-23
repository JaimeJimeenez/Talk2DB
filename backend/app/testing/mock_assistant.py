from app.domain.ports.assistant import AssistantGateway, AssistantReply


class MockAssistantGateway(AssistantGateway):
    async def reply_to(self, content: str, schema_id: str) -> AssistantReply:
        return AssistantReply(
            content=(
            "Mock response: I received your request and will generate SQL for "
            f"'{content}'."
            ),
            sql=f"SELECT * FROM {schema_id}.example LIMIT 100",
        )
