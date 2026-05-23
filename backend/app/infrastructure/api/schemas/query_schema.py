from datetime import datetime

from pydantic import BaseModel, Field


class RegisterQuerySchemaRequest(BaseModel):
    name: str = Field(min_length=1, max_length=63)
    description: str = ""
    business_rules: str = ""


class QuerySchemaResponse(BaseModel):
    id: str
    name: str
    description: str
    business_rules: str
    created_at: datetime
    refreshed_at: datetime
