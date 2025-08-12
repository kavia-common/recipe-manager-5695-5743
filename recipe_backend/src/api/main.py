from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.db import Base, engine
from src.routers import auth as auth_router
from src.routers import recipes as recipes_router
from src.routers import users as users_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create tables on startup (simple approach for this project).
    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()

openapi_tags = [
    {"name": "Health", "description": "API health checks."},
    {"name": "Authentication", "description": "User registration and login."},
    {"name": "Users", "description": "User-related endpoints."},
    {"name": "Recipes", "description": "Recipe CRUD and favorites."},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_tags=openapi_tags,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Basic health check endpoint.",
)
def health_check():
    """Return a simple health status message."""
    return {"message": "Healthy"}


# Include routers
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(recipes_router.router)
