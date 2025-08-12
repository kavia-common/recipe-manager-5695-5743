from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class Favorite(Base):
    """Association table representing user favorites of recipes."""
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe_favorite"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    """User model for authentication and ownership."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recipes: Mapped[List["Recipe"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    favorites: Mapped[List["Recipe"]] = relationship(
        "Recipe",
        secondary="favorites",
        primaryjoin="User.id==Favorite.user_id",
        secondaryjoin="Recipe.id==Favorite.recipe_id",
        back_populates="liked_by",
        viewonly=True,
    )


class Recipe(Base):
    """Recipe model with core fields."""
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingredients: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    owner: Mapped[User] = relationship(back_populates="recipes")

    liked_by: Mapped[List[User]] = relationship(
        "User",
        secondary="favorites",
        primaryjoin="Recipe.id==Favorite.recipe_id",
        secondaryjoin="User.id==Favorite.user_id",
        back_populates="favorites",
        viewonly=True,
    )
