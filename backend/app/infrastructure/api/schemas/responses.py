from __future__ import annotations

from typing import Generic, Optional, TypeVar, List
from dataclasses import field, dataclass
from enum import Enum
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class ResponseTypes(Enum):
    PARAMETERS_ERROR = "parameters_error"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    SUCCESS = "success"
    SYSTEM_ERROR = "system_error"

class ResponseStatus(Enum):
    PARAMETERS_ERROR = 400
    NOT_FOUND = 404
    UNAUTHORIZED = 401
    SUCCESS = 200
    SYSTEM_ERROR = 500

class ErrorCode(Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    ENGINE_ERROR = "ENGINE_ERROR"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"

class ResponseFailure:

    def __init__(self, type: ResponseTypes, message: str | Exception):
        self._status = type.value
        self.status_code = ResponseStatus[type.name].value
        self.message = self._format_message(message)

    def _format_message(self, message: str | Exception) -> str:
        if isinstance(message, Exception):
            return f"{message.__class__.__name__}: {str(message)}"
        return str(message)
    
    @property
    def value(self):
        return { 'type': self._status, 'message': self.message }
    
class ResponseSuccess:

    def __init__(self, value=None):
        self._status = ResponseTypes.SUCCESS
        self._status_code = ResponseTypes.SUCCESS.value
        self._value = value

    def __bool__(self):
        return True
    
    def __json__(self):
        return { "type": self._status, "value": self._value }
    
class BaseResponse(BaseModel, Generic[T]):
    data: Optional[T]

def get_response(result: T | List[T]) -> BaseResponse[T]:
    return BaseResponse[List[T]](data=result) if isinstance(result, list) else BaseResponse[T](data=result)

@dataclass(frozen=True)
class Failure:
    code: ErrorCode
    message: str
    details: Optional[str] = field(default=None)

    @staticmethod
    def validation(message: str, details: Optional[str] = None) -> Failure:
        return Failure(code=ErrorCode.VALIDATION_ERROR, message=message, details=details)
    
    @staticmethod
    def not_found(message: str) -> Failure:
        return Failure(code=ErrorCode.NOT_FOUND, message=message)
    
    @staticmethod
    def engine_error(message: str, details: Optional[str] = None) -> Failure:
        return Failure(code=ErrorCode.ENGINE_ERROR, message=message, details=details)
    
    @staticmethod
    def unexpected_error(message: str) -> Failure:
        return Failure(code=ErrorCode.UNEXPECTED_ERROR, message=message)
    
@dataclass(frozen=True)
class Result(Generic[T]):
    _value: Optional[T] = field(default=None)
    _failure: Optional[Failure] = field(default=None)

    @staticmethod
    def ok(value: T) -> Result[T]:
        return Result(_value=value)
    
    @staticmethod
    def fail(failure: Failure) -> Result[T]:
        return Result(_failure=failure)
    
    @property
    def is_ok(self) -> bool:
        return self._failure is None
    
    @property
    def value(self) -> T:
        if not self.is_ok:
            raise RuntimeError("Cannot access value of a failed result.")
        return self._value

    @property
    def is_failure(self) -> bool:
        if self._is_ok:
            raise RuntimeError("Cannot access failure of a successful result.")
        return self._failure