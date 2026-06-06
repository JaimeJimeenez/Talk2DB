from datetime import datetime

from pydantic import BaseModel


class QuerySchemaResponse(BaseModel):
    id: str
    name: str
    description: str
    business_rules: str
    created_at: datetime
    refreshed_at: datetime
