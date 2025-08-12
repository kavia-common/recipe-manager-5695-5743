from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.core.config import get_settings


class Base(DeclarativeBase):
    """Base for all SQLAlchemy ORM models."""
    pass


def _get_engine():
    settings = get_settings()
    connect_args = {}
    # SQLite requires check_same_thread option when used with FastAPI
    if settings.DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(settings.DATABASE_URL, connect_args=connect_args, future=True)


engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


# PUBLIC_INTERFACE
def get_db() -> Generator:
    """Yield a SQLAlchemy session and ensure it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
