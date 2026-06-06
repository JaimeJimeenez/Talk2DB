from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from functools import wraps

from app.infrastructure.api.lib.auth import authenticate

from app.infrastructure.api.schemas.responses import ResponseFailure, ResponseSuccess

def _build_success_response(response):
    if isinstance(response, JSONResponse):
        return response
    
    if isinstance(response, ResponseFailure):
        raise HTTPException(status_code=response.status_code, detail=response.message)
    
    if isinstance(response, ResponseSuccess):
        return JSONResponse(
            status_code=response.status_code,
            content={
                "status": response.status.value,
                "message": None,
                "data": jsonable_encoder(response.value)
            }
        )
    payload = response.model_dump() if hasattr(response, "model_dump") else response
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "message": None,
            "data": jsonable_encoder(payload)
        }
    )

def _to_http_exception(exception) -> HTTPException:
    if isinstance(exception, HTTPException):
        return exception
    return HTTPException(status_code=500, detail=str(exception))

def handle_request(func):
    """
        Decorator to handle API requests, converting domain responses to HTTP responses and handling exceptions.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            authenticate(*args, **kwargs)
            response = await func(*args, **kwargs)
            return _build_success_response(response)
        except HTTPException as http_exception:
            raise http_exception
        except Exception as exception:
            http_exception = _to_http_exception(exception)
            raise http_exception
    return wrapper