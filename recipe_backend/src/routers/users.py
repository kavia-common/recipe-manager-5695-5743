from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.deps import get_current_user
from src.db import get_db
from src.models import User
from src.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["Users"])


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user",
    description="Return the current authenticated user's information.",
)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserOut:
    """Return the current authenticated user."""
    # db is injected to keep dependency signature consistent for future use
    return current_user
