from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.deps import get_current_user
from src.db import get_db
from src.models import Favorite, Recipe, User
from src.schemas.recipe import RecipeCreate, RecipeOut, RecipeUpdate

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def _get_recipe_or_404(db: Session, recipe_id: int) -> Recipe:
    recipe = db.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[RecipeOut],
    summary="List recipes",
    description="List recipes with optional full-text search across title and description.",
)
def list_recipes(
    db: Annotated[Session, Depends(get_db)],
    q: Optional[str] = Query(default=None, description="Search query for title or description"),
    skip: int = Query(default=0, ge=0, description="Records to skip for pagination"),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
) -> List[RecipeOut]:
    """Return a list of recipes optionally filtered by a search query."""
    stmt = select(Recipe)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Recipe.title.ilike(like), Recipe.description.ilike(like)))
    stmt = stmt.offset(skip).limit(limit)
    recipes = db.execute(stmt).scalars().all()
    return recipes


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=RecipeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create recipe",
    description="Create a new recipe owned by the current user.",
)
def create_recipe(
    payload: RecipeCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RecipeOut:
    """Create a new recipe for the current user."""
    recipe = Recipe(
        title=payload.title,
        description=payload.description,
        ingredients=payload.ingredients,
        instructions=payload.instructions,
        tags=payload.tags,
        owner_id=current_user.id,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


# PUBLIC_INTERFACE
@router.get(
    "/{recipe_id}",
    response_model=RecipeOut,
    summary="Get recipe by id",
    description="Return details for a recipe by its ID.",
)
def read_recipe(recipe_id: int, db: Annotated[Session, Depends(get_db)]) -> RecipeOut:
    """Return a single recipe by ID."""
    recipe = _get_recipe_or_404(db, recipe_id)
    return recipe


# PUBLIC_INTERFACE
@router.put(
    "/{recipe_id}",
    response_model=RecipeOut,
    summary="Update recipe",
    description="Update an existing recipe. Only the owner can update.",
)
def update_recipe(
    recipe_id: int,
    payload: RecipeUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RecipeOut:
    """Update fields of a recipe if the current user is the owner."""
    recipe = _get_recipe_or_404(db, recipe_id)
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this recipe")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(recipe, field, value)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


# PUBLIC_INTERFACE
@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete recipe",
    description="Delete a recipe by ID. Only the owner can delete.",
)
def delete_recipe(
    recipe_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a recipe if the current user is the owner."""
    recipe = _get_recipe_or_404(db, recipe_id)
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this recipe")
    db.delete(recipe)
    db.commit()
    return None


# PUBLIC_INTERFACE
@router.post(
    "/{recipe_id}/favorite",
    status_code=status.HTTP_201_CREATED,
    summary="Add favorite",
    description="Mark a recipe as favorite for the current user.",
)
def add_favorite(
    recipe_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Add a recipe to the current user's favorites."""
    recipe = _get_recipe_or_404(db, recipe_id)

    existing = db.execute(
        select(Favorite).where(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe.id)
    ).scalar_one_or_none()
    if not existing:
        fav = Favorite(user_id=current_user.id, recipe_id=recipe.id)
        db.add(fav)
        db.commit()
    return {"message": "Added to favorites"}


# PUBLIC_INTERFACE
@router.delete(
    "/{recipe_id}/favorite",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove favorite",
    description="Remove a recipe from the current user's favorites.",
)
def remove_favorite(
    recipe_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Remove a recipe from the current user's favorites."""
    _ = _get_recipe_or_404(db, recipe_id)

    fav = db.execute(
        select(Favorite).where(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id)
    ).scalar_one_or_none()
    if fav:
        db.delete(fav)
        db.commit()
    return None


# PUBLIC_INTERFACE
@router.get(
    "/favorites/me",
    response_model=List[RecipeOut],
    summary="List my favorite recipes",
    description="Get a list of recipes that the current user has marked as favorites.",
)
def list_my_favorites(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[RecipeOut]:
    """Return the current user's favorite recipes."""
    stmt = (
        select(Recipe)
        .join(Favorite, Favorite.recipe_id == Recipe.id)
        .where(Favorite.user_id == current_user.id)
    )
    recipes = db.execute(stmt).scalars().all()
    return recipes
