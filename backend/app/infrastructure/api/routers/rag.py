from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject

from app.core.container import Container

from app.infrastructure.api.schemas.conversations import PromptRequest, PromptResponse
from app.infrastructure.api.security import get_current_user_id
from app.application.use_cases.rag import RagUseCase

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])

@router.post(
    '/completion',
    response_model=PromptResponse,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
@inject
async def completion(
    payload: PromptRequest,
    user_id: str = Depends(get_current_user_id),
    rag_use_case: RagUseCase = Depends(Provide[Container.rag_use_case])
) -> PromptResponse:
    try:
        completion = await rag_use_case.completion(
            payload.prompt,
            payload.schema_id,
            payload.conversation_id,
            user_id,
        )
        response = PromptResponse.model_validate(
            {
                "title": completion.title,
                "conversation_id": completion.conversation_id,
                "answer": completion.answer,
                "message_id": completion.message_id,
                "content": completion.answer,
                "timestamp": completion.timestamp,
                "sql": completion.sql,
                "error": completion.error,
                "artifact": completion.artifact,
                "conversation_title": completion.title,
            }
        )
        return response
    except HTTPException as error:
        raise error
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
