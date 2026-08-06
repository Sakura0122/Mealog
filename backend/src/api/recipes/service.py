from datetime import datetime, timedelta
from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.meal_records.model import MealRecord
from src.api.recipes.model import Recipe, RecipeIngredient
from src.api.recipes.schema import (
    RecipeCreate,
    RecipeCreatedResponse,
    RecipeListItemResponse,
    RecipeResponse,
    RecipeSavedResponse,
    RecipeShareResponse,
    RecipeStatus,
    RecipeUpdate,
)
from src.common.exceptions import BusinessException
from src.common.page import PageRequest, PageResult
from src.common.result_code import ResultCodeEnum
from src.rustfs.url import build_public_file_url


async def create_recipe(
    payload: RecipeCreate,
    user_id: UUID,
    session: AsyncSession,
) -> RecipeCreatedResponse:
    """创建当前用户的菜谱及有序食材。"""

    # 菜名在同一用户下保持唯一，避免列表和饮食记录联想出现同名歧义。
    await _validate_unique_name(payload.name, user_id, session)
    _validate_cover_keys(payload)
    recipe = Recipe(
        user_id=str(user_id),
        name=payload.name,
        cover_object_key=payload.cover_object_key,
        cover_processed_object_key=payload.cover_processed_object_key,
        steps=payload.steps,
        status=_calculate_status(payload.ingredients, payload.steps),
    )
    session.add(recipe)
    await session.flush()

    session.add_all(_create_ingredients(recipe.id, payload.ingredients))
    await session.flush()
    return RecipeCreatedResponse(id=recipe.id)


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


async def share_recipe(recipe_id: UUID, user_id: UUID, session: AsyncSession) -> None:
    """为当前用户的菜谱刷新分享有效期。"""

    recipe = await _get_owned_recipe(recipe_id, user_id, session)
    # 每次主动分享都刷新有效期，旧分享路径无需更换即可继续使用。
    recipe.share_expires_at = datetime.now() + timedelta(days=7)
    await session.flush()


async def get_shared_recipe(recipe_id: UUID, session: AsyncSession) -> RecipeShareResponse:
    """查询仍在有效期内的分享菜谱。"""

    recipe = await _get_active_shared_recipe(recipe_id, session)
    ingredients = await _get_ingredients(recipe.id, session)
    return _to_share_response(recipe, ingredients)


async def save_shared_recipe(
    recipe_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> RecipeSavedResponse:
    """将有效的分享菜谱复制到当前用户的菜谱中。"""

    source = await _get_active_shared_recipe(recipe_id, session)
    if source.user_id == str(user_id):
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "不能保存自己的菜谱")

    existing_copy = await session.scalar(
        select(Recipe.id).where(
            Recipe.user_id == str(user_id),
            Recipe.source_recipe_id == source.id,
        )
    )
    if existing_copy is not None:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "该分享菜谱已保存")

    await _validate_unique_name(source.name, user_id, session)
    source_ingredients = await _get_ingredients(source.id, session)
    recipe = Recipe(
        user_id=str(user_id),
        source_recipe_id=source.id,
        name=source.name,
        cover_object_key=source.cover_object_key,
        cover_processed_object_key=source.cover_processed_object_key,
        steps=source.steps,
        status=source.status,
    )
    session.add(recipe)
    await session.flush()

    # 保存动作复制当前分享内容，后续原菜谱修改不会影响用户已保存的副本。
    session.add_all(
        _create_ingredients(recipe.id, [ingredient.name for ingredient in source_ingredients])
    )
    await session.flush()
    return RecipeSavedResponse(id=recipe.id)


async def update_recipe(
    recipe_id: UUID,
    payload: RecipeUpdate,
    user_id: UUID,
    session: AsyncSession,
) -> None:
    """更新当前用户的菜谱及有序食材。"""

    recipe = await _get_owned_recipe(recipe_id, user_id, session)
    await _validate_unique_name(payload.name, user_id, session, recipe.id)
    _validate_cover_keys(payload)

    recipe.name = payload.name
    recipe.cover_object_key = payload.cover_object_key
    recipe.cover_processed_object_key = payload.cover_processed_object_key
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
    """
    查询属于当前用户的菜谱。

    :param recipe_id: 菜谱 ID
    :param user_id: 当前用户 ID
    :param session: 数据库会话
    :return: 当前用户的菜谱
    """

    recipe = await session.scalar(
        select(Recipe).where(
            Recipe.id == str(recipe_id),
            Recipe.user_id == str(user_id),
        )
    )
    if recipe is None:
        raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "菜谱不存在")
    return recipe


def _validate_cover_keys(payload: RecipeCreate | RecipeUpdate) -> None:
    """校验菜谱缩略图必须依附于对应的原始封面。"""

    if payload.cover_object_key is None and payload.cover_processed_object_key is not None:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "菜谱缩略图缺少原始封面")


async def _get_active_shared_recipe(recipe_id: UUID, session: AsyncSession) -> Recipe:
    """查询未过期的分享菜谱，失效状态统一按不存在处理。"""

    recipe = await session.scalar(
        select(Recipe).where(
            Recipe.id == str(recipe_id),
            Recipe.share_expires_at.is_not(None),
            Recipe.share_expires_at >= datetime.now(),
        )
    )
    if recipe is None:
        raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "分享不存在或已过期")
    return recipe


async def _validate_unique_name(
    name: str,
    user_id: UUID,
    session: AsyncSession,
    excluded_recipe_id: str | None = None,
) -> None:
    """
    校验菜谱名称在当前用户下是否唯一。

    :param name: 待校验的菜谱名称
    :param user_id: 当前用户 ID
    :param session: 数据库会话
    :param excluded_recipe_id: 编辑时需要排除的当前菜谱 ID
    :return: 无返回值
    """

    statement = select(Recipe.id).where(
        Recipe.user_id == str(user_id),
        Recipe.name == name,
    )
    if excluded_recipe_id is not None:
        statement = statement.where(Recipe.id != excluded_recipe_id)
    if await session.scalar(statement) is not None:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "菜谱名称已存在")


async def _get_ingredients(recipe_id: str, session: AsyncSession) -> list[RecipeIngredient]:
    """
    按录入顺序查询菜谱的食材。

    :param recipe_id: 菜谱 ID
    :param session: 数据库会话
    :return: 按展示顺序排列的食材列表
    """

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
    """
    按请求中的名称顺序构建菜谱食材模型。

    :param recipe_id: 菜谱 ID
    :param names: 食材名称列表
    :return: 待写入数据库的食材模型列表
    """

    return [
        RecipeIngredient(recipe_id=recipe_id, name=name, sort_order=index)
        for index, name in enumerate(names)
    ]


def _calculate_status(ingredients: list[str], steps: str | None) -> RecipeStatus:
    """
    根据食材和制作步骤的完整性计算菜谱状态。

    :param ingredients: 菜谱食材名称列表
    :param steps: 菜谱制作步骤
    :return: 草稿或已完善状态
    """

    # 产品状态只由食材和步骤是否完整决定，封面不影响草稿状态。
    return "COMPLETED" if ingredients and steps is not None else "DRAFT"


def _usage_count_subquery():
    """
    构建统计每个菜谱有效饮食记录数量的相关子查询。

    :return: 可嵌入菜谱列表查询的标量子查询
    """

    return (
        select(func.count())
        .select_from(MealRecord)
        .where(MealRecord.recipe_id == Recipe.id)
        .correlate(Recipe)
        .scalar_subquery()
    )


def _to_list_item_response(recipe: Recipe, usage_count: int) -> RecipeListItemResponse:
    """
    将菜谱模型转换为列表项响应，并补充公开封面地址和使用次数。

    :param recipe: 菜谱模型
    :param usage_count: 菜谱关联的有效饮食记录数量
    :return: 菜谱列表项响应
    """

    cover_object_key = recipe.cover_processed_object_key or recipe.cover_object_key
    return RecipeListItemResponse(
        id=recipe.id,
        name=recipe.name,
        cover_url=build_public_file_url(cover_object_key) if cover_object_key else None,
        status=cast("RecipeStatus", recipe.status),
        usage_count=usage_count,
        updated_at=recipe.updated_at,
    )


def _to_recipe_response(
    recipe: Recipe,
    ingredients: list[RecipeIngredient],
    usage_count: int,
) -> RecipeResponse:
    """
    将菜谱及其食材转换为完整详情响应。

    :param recipe: 菜谱模型
    :param ingredients: 按展示顺序排列的食材模型
    :param usage_count: 菜谱关联的有效饮食记录数量
    :return: 菜谱详情响应
    """

    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        cover_object_key=recipe.cover_object_key,
        cover_processed_object_key=recipe.cover_processed_object_key,
        cover_url=(
            build_public_file_url(recipe.cover_object_key)
            if recipe.cover_object_key is not None
            else None
        ),
        cover_processed_url=(
            build_public_file_url(recipe.cover_processed_object_key)
            if recipe.cover_processed_object_key is not None
            else None
        ),
        ingredients=[ingredient.name for ingredient in ingredients],
        steps=recipe.steps,
        status=cast("RecipeStatus", recipe.status),
        usage_count=usage_count,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
    )


def _to_share_response(
    recipe: Recipe,
    ingredients: list[RecipeIngredient],
) -> RecipeShareResponse:
    """将菜谱转换为不包含归属和存储键的公开分享响应。"""

    return RecipeShareResponse(
        id=recipe.id,
        name=recipe.name,
        cover_url=(
            build_public_file_url(recipe.cover_object_key)
            if recipe.cover_object_key is not None
            else None
        ),
        cover_processed_url=(
            build_public_file_url(recipe.cover_processed_object_key)
            if recipe.cover_processed_object_key is not None
            else None
        ),
        ingredients=[ingredient.name for ingredient in ingredients],
        steps=recipe.steps,
    )
