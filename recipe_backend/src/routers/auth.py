from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.security import create_access_token, get_password_hash, verify_password
from src.db import get_db
from src.models import User
from src.schemas.user import Token, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user with email and password.",
)
def register_user(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserOut:
    """Register a new user account and return its public information."""
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate using email and password and receive a JWT access token.",
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    """Authenticate a user and return a JWT token."""
    user = db.execute(select(User).where(User.email == form_data.username)).scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token, token_type="bearer")
