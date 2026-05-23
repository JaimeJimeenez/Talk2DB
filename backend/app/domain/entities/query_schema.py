from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class QuerySchema:
    id: str
    name: str
    description: str
    business_rules: str
    context: str
    created_at: datetime
    refreshed_at: datetime
