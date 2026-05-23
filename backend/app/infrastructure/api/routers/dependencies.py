from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.session import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
