from pydantic import BaseModel, EmailStr, Field

class SignupResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    token: str

class SignupRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)
