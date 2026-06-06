from uuid import uuid4
from datetime import datetime, UTC, timedelta
from typing import TYPE_CHECKING

from app.application.rag import RagResult, RagService

from app.domain.entities.rag_metrics import RagRun
from app.domain.entities.message import Message, MessageRole
from app.domain.errors import ConversationNotFoundError

if TYPE_CHECKING:
    from app.application.use_cases.conversations import ConversationsUseCase
    from app.application.use_cases.rag_metrics import RagMetricsUseCase

class ConversationCompletion:
    def __init__(
        self,
        title: str,
        conversation_id: str,
        answer: str,
        message_id: str,
        timestamp: datetime,
        sql: str | None,
        error: str | None,
        artifact: dict | None,
    ) -> None:
        self.title = title
        self.conversation_id = conversation_id
        self.answer = answer
        self.message_id = message_id
        self.timestamp = timestamp
        self.sql = sql
        self.error = error
        self.artifact = artifact

class RagUseCase:
    def __init__(
        self,
        rag_service: RagService,
        conversations_use_case: "ConversationsUseCase",
        rag_metrics_use_case: "RagMetricsUseCase | None" = None,
    ) -> None:
        self._rag_service = rag_service
        self._conversations_use_case = conversations_use_case
        self._rag_metrics_use_case = rag_metrics_use_case

    async def completion(
        self,
        prompt: str,
        schema_id: str,
        conversation_id: str | None = None,
        user_id: str | None = None
    ) -> ConversationCompletion:
        if user_id is None:
            raise ValueError("User id required")
        
        if conversation_id is None:
            conversation = await self._conversations_use_case.new_conversation(prompt, schema_id, user_id)
        else:
            conversation = await self._conversations_use_case.get_conversation(conversation_id, user_id)
            if conversation is None:
                raise ConversationNotFoundError(conversation_id)
        if self._should_generate_title(conversation):
            conversation.title = await self.generate_conversation_title(prompt)
        conversation_context = self._conversation_context(conversation.messages)
        try:
            rag_result: RagResult = await self._rag_service.answer(
                prompt,
                schema_id,
                conversation_context=conversation_context,
            )
        except Exception as error:
            rag_result = RagResult(
                answer="No he podido completar la consulta con el SQL generado.",
                sql=getattr(error, "generated_sql", None),
                columns=[],
                rows=[],
                row_count=0,
                error=str(error),
                trace=getattr(error, "trace", None),
            )
        user_timestamp = datetime.now(UTC)
        assistant_timestamp = datetime.now(UTC)
        if assistant_timestamp <= user_timestamp:
            assistant_timestamp = user_timestamp + timedelta(microseconds=1)
        assistant_message = Message(
            id=str(uuid4()),
            role=MessageRole.ASSISTANT,
            content=rag_result.answer,
            timestamp=assistant_timestamp,
            sql=rag_result.sql,
            error=rag_result.error,
            artifact=self._conversations_use_case._artifact_from_rag_result(prompt, rag_result),
            conversation_title=conversation.title,
        )
        conversation.messages.extend(
            [
                Message(
                    id=str(uuid4()),
                    role=MessageRole.USER,
                    content=prompt,
                    timestamp=user_timestamp,
                ),
                assistant_message,
            ]
        )
        saved_conversation = await self._conversations_use_case.save_conversation(conversation)
        await self._save_metrics(
            prompt=prompt,
            schema_id=schema_id,
            schema_name=rag_result.trace.schema_name if rag_result.trace else getattr(conversation, "schema_name", "") or "",
            user_id=user_id,
            conversation_id=saved_conversation.id,
            assistant_message=assistant_message,
            rag_result=rag_result,
        )

        return ConversationCompletion(
            title=saved_conversation.title,
            conversation_id=saved_conversation.id,
            answer=rag_result.answer,
            message_id=assistant_message.id,
            timestamp=assistant_message.timestamp,
            sql=assistant_message.sql,
            error=assistant_message.error,
            artifact=assistant_message.artifact,
        )

    async def _save_metrics(
        self,
        *,
        prompt: str,
        schema_id: str,
        schema_name: str,
        user_id: str,
        conversation_id: str,
        assistant_message: Message,
        rag_result: RagResult,
    ) -> None:
        if self._rag_metrics_use_case is None or rag_result.trace is None:
            return

        trace = rag_result.trace
        await self._rag_metrics_use_case.save_run(
            RagRun(
                id=str(uuid4()),
                conversation_id=conversation_id,
                message_id=assistant_message.id,
                user_id=user_id,
                schema_id=schema_id,
                schema_name=schema_name,
                prompt=prompt,
                status=trace.status,
                created_at=assistant_message.timestamp,
                started_at=trace.started_at,
                completed_at=trace.completed_at,
                duration_ms=trace.duration_ms,
                attempt_count=trace.attempt_count,
                repair_count=trace.repair_count,
                sql_validated=trace.sql_validated,
                sql_executed=trace.sql_executed,
                generated_sql=assistant_message.sql,
                error=assistant_message.error,
                row_count=trace.row_count,
                truncated=trace.truncated,
                used_context=trace.used_context,
                context_message_count=trace.context_message_count,
                model=trace.model,
                retrieved_table_count=len(trace.retrieved_tables),
                retrieved_tables=trace.retrieved_tables,
            )
        )

    async def generate_conversation_title(self, prompt: str) -> str:
        return await self._rag_service.title_for(prompt)

    @staticmethod
    def _should_generate_title(conversation) -> bool:
        return not conversation.messages and conversation.title.strip().lower() in {
            "",
            "new conversation",
            "nueva conversación",
        }

    @staticmethod
    def _conversation_context(messages: list[Message]) -> str:
        relevant_messages = messages[-8:]
        lines: list[str] = []
        for message in relevant_messages:
            content = " ".join(message.content.strip().split())
            if not content:
                continue
            if len(content) > 500:
                content = f"{content[:497]}..."
            lines.append(f"{message.role.value}: {content}")
            if message.role == MessageRole.ASSISTANT and message.sql:
                sql = " ".join(message.sql.strip().split())
                if len(sql) > 800:
                    sql = f"{sql[:797]}..."
                lines.append(f"assistant_sql: {sql}")
        return "\n".join(lines)
