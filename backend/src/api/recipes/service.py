from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.meal_records.model import MealRecord
from src.api.recipes.model import Recipe, RecipeIngredient
from src.api.recipes.schema import (
    RecipeCreate,
    RecipeListItemResponse,
    RecipeResponse,
    RecipeStatus,
    RecipeUpdate,
)
from src.common.exceptions import BusinessException
from src.common.page import PageRequest, PageResult
from src.common.result_code import ResultCodeEnum
from src.rustfs.url import build_public_file_url


async def create_recipe(payload: RecipeCreate, user_id: UUID, session: AsyncSession) -> None:
    """创建当前用户的菜谱及有序食材。"""

    # 菜名在同一用户下保持唯一，避免列表和饮食记录联想出现同名歧义。
    await _validate_unique_name(payload.name, user_id, session)
    recipe = Recipe(
        user_id=str(user_id),
        name=payload.name,
        cover_object_key=payload.cover_object_key,
        steps=payload.steps,
        status=_calculate_status(payload.ingredients, payload.steps),
    )
    session.add(recipe)
    await session.flush()

    session.add_all(_create_ingredients(recipe.id, payload.ingredients))
    await session.flush()


async def list_recipes(
    page: PageRequest,
    user_id: UUID,
    session: AsyncSession,
    keyword: str | None = None,
    status: RecipeStatus | None = None,
) -> PageResult[RecipeListItemResponse]:
    """按关键字和状态分页查询当前用户的菜谱。"""

    filters = [Recipe.user_id == str(user_id)]
    normalized_keyword = keyword.strip() if keyword is not None else ""
    if normalized_keyword:
        filters.append(Recipe.name.contains(normalized_keyword, autoescape=True))
    if status is not None:
        filters.append(Recipe.status == status)

    usage_count = _usage_count_subquery()
    total = await session.scalar(select(func.count()).select_from(Recipe).where(*filters))
    rows = (
        await session.execute(
            select(Recipe, usage_count)
            .where(*filters)
            .order_by(
                *page.to_order_by(
                    {"name": Recipe.name, "updated_at": Recipe.updated_at},
                    [Recipe.updated_at.desc()],
                )
            )
            .offset(page.offset)
            .limit(page.page_size)
        )
    ).all()

    items = [_to_list_item_response(recipe, count) for recipe, count in rows]
    return PageResult.of(page, total or 0, items)


async def get_recipe(recipe_id: UUID, user_id: UUID, session: AsyncSession) -> RecipeResponse:
    """查询当前用户的菜谱详情。"""

    recipe = await _get_owned_recipe(recipe_id, user_id, session)
    ingredients = await _get_ingredients(recipe.id, session)
    usage_count = await session.scalar(
        select(func.count()).select_from(MealRecord).where(MealRecord.recipe_id == recipe.id)
    )
    return _to_recipe_response(recipe, ingredients, usage_count or 0)


async def update_recipe(
    recipe_id: UUID,
    payload: RecipeUpdate,
    user_id: UUID,
    session: AsyncSession,
) -> None:
    """更新当前用户的菜谱及有序食材。"""

    recipe = await _get_owned_recipe(recipe_id, user_id, session)
    await _validate_unique_name(payload.name, user_id, session, recipe.id)

    recipe.name = payload.name
    recipe.cover_object_key = payload.cover_object_key
    recipe.steps = payload.steps
    recipe.status = _calculate_status(payload.ingredients, payload.steps)

    # 食材以请求顺序为准，整体替换可保证排序和值与编辑表单完全一致。
    await RecipeIngredient.soft_delete_by(session, recipe_id=recipe.id)
    session.add_all(_create_ingredients(recipe.id, payload.ingredients))
    await session.flush()


async def delete_recipe(recipe_id: UUID, user_id: UUID, session: AsyncSession) -> None:
    """软删除当前用户的菜谱及其食材。"""

    deleted_count = await Recipe.soft_delete_by(
        session,
        id=str(recipe_id),
        user_id=str(user_id),
    )
    if deleted_count == 0:
        # 不区分不存在和属于其他用户，避免泄露他人菜谱信息。
        raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "菜谱不存在")

    await RecipeIngredient.soft_delete_by(session, recipe_id=str(recipe_id))


async def _get_owned_recipe(
    recipe_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> Recipe:
    recipe = await session.scalar(
        select(Recipe).where(
            Recipe.id == str(recipe_id),
            Recipe.user_id == str(user_id),
        )
    )
    if recipe is None:
        raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "菜谱不存在")
    return recipe


async def _validate_unique_name(
    name: str,
    user_id: UUID,
    session: AsyncSession,
    excluded_recipe_id: str | None = None,
) -> None:
    statement = select(Recipe.id).where(
        Recipe.user_id == str(user_id),
        Recipe.name == name,
    )
    if excluded_recipe_id is not None:
        statement = statement.where(Recipe.id != excluded_recipe_id)
    if await session.scalar(statement) is not None:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "菜谱名称已存在")


async def _get_ingredients(recipe_id: str, session: AsyncSession) -> list[RecipeIngredient]:
    return list(
        (
            await session.scalars(
                select(RecipeIngredient)
                .where(RecipeIngredient.recipe_id == recipe_id)
                .order_by(RecipeIngredient.sort_order)
            )
        ).all()
    )


def _create_ingredients(recipe_id: str, names: list[str]) -> list[RecipeIngredient]:
    return [
        RecipeIngredient(recipe_id=recipe_id, name=name, sort_order=index)
        for index, name in enumerate(names)
    ]


def _calculate_status(ingredients: list[str], steps: str | None) -> RecipeStatus:
    # 产品状态只由食材和步骤是否完整决定，封面不影响草稿状态。
    return "COMPLETED" if ingredients and steps is not None else "DRAFT"


def _usage_count_subquery():
    return (
        select(func.count())
        .select_from(MealRecord)
        .where(MealRecord.recipe_id == Recipe.id)
        .correlate(Recipe)
        .scalar_subquery()
    )


def _to_list_item_response(recipe: Recipe, usage_count: int) -> RecipeListItemResponse:
    return RecipeListItemResponse(
        id=recipe.id,
        name=recipe.name,
        cover_url=(
            build_public_file_url(recipe.cover_object_key)
            if recipe.cover_object_key is not None
            else None
        ),
        status=cast("RecipeStatus", recipe.status),
        usage_count=usage_count,
        updated_at=recipe.updated_at,
    )


def _to_recipe_response(
    recipe: Recipe,
    ingredients: list[RecipeIngredient],
    usage_count: int,
) -> RecipeResponse:
    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        cover_object_key=recipe.cover_object_key,
        cover_url=(
            build_public_file_url(recipe.cover_object_key)
            if recipe.cover_object_key is not None
            else None
        ),
        ingredients=[ingredient.name for ingredient in ingredients],
        steps=recipe.steps,
        status=cast("RecipeStatus", recipe.status),
        usage_count=usage_count,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
    )
