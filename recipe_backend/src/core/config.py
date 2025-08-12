import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Recipe Manager API")
    PROJECT_DESCRIPTION: str = os.getenv(
        "PROJECT_DESCRIPTION",
        "REST API for managing recipes with authentication and favorites.",
    )
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./recipes.db")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # Comma-separated CORS origins, or * for all
    _cors_origins: str = os.getenv("CORS_ORIGINS", "*")

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Return a list of allowed CORS origins."""
        if self._cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self._cors_origins.split(",") if o.strip()]


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return singleton settings instance loaded from env."""
    return _get_settings()


@lru_cache()
def _get_settings() -> Settings:
    return Settings()
