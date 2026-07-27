from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.recipes import service as recipe_service
from src.api.recipes.schema import (
    RecipeCreate,
    RecipeListItemResponse,
    RecipeResponse,
    RecipeStatus,
    RecipeUpdate,
)
from src.common.page import PageRequest, PageResult
from src.common.result import Result
from src.core.dependencies import CurrentUserIdDep, SessionDep

router = APIRouter(prefix="/recipes", tags=["菜谱"])


@router.post("", response_model=Result[None], summary="新增菜谱")
async def create_recipe(
    payload: RecipeCreate,
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[None]:
    await recipe_service.create_recipe(payload, user_id, session)
    return Result.success()


@router.get(
    "",
    response_model=Result[PageResult[RecipeListItemResponse]],
    summary="分页查询菜谱",
)
async def list_recipes(
    user_id: CurrentUserIdDep,
    session: SessionDep,
    page: Annotated[PageRequest, Depends()],
    keyword: Annotated[str | None, Query(max_length=100, description="菜谱名称关键字")] = None,
    status: Annotated[RecipeStatus | None, Query(description="菜谱状态")] = None,
) -> Result[PageResult[RecipeListItemResponse]]:
    res = await recipe_service.list_recipes(page, user_id, session, keyword, status)
    return Result.success(res)


@router.get("/{recipe_id}", response_model=Result[RecipeResponse], summary="查询菜谱详情")
async def get_recipe(
    recipe_id: UUID,
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[RecipeResponse]:
    res = await recipe_service.get_recipe(recipe_id, user_id, session)
    return Result.success(res)


@router.put("/{recipe_id}", response_model=Result[None], summary="更新菜谱")
async def update_recipe(
    recipe_id: UUID,
    payload: RecipeUpdate,
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[None]:
    await recipe_service.update_recipe(recipe_id, payload, user_id, session)
    return Result.success()


@router.delete("/{recipe_id}", response_model=Result[None], summary="删除菜谱")
async def delete_recipe(
    recipe_id: UUID,
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[None]:
    await recipe_service.delete_recipe(recipe_id, user_id, session)
    return Result.success()
