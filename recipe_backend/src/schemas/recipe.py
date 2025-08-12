from typing import Optional

from pydantic import BaseModel, Field


class RecipeBase(BaseModel):
    title: str = Field(..., description="Title of the recipe")
    description: Optional[str] = Field(None, description="Description of the recipe")
    ingredients: Optional[str] = Field(None, description="Ingredients list (text)")
    instructions: Optional[str] = Field(None, description="Instructions (text)")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Title of the recipe")
    description: Optional[str] = Field(None, description="Description of the recipe")
    ingredients: Optional[str] = Field(None, description="Ingredients list (text)")
    instructions: Optional[str] = Field(None, description="Instructions (text)")
    tags: Optional[str] = Field(None, description="Comma-separated tags")


class RecipeOut(RecipeBase):
    id: int = Field(..., description="Recipe ID")
    owner_id: int = Field(..., description="Owner user ID")

    class Config:
        from_attributes = True
