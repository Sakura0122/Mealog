from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from src.api.meal_records import service as meal_record_service
from src.api.meal_records.schema import MealRecordCreate, MealRecordResponse, MealRecordUpdate
from src.common.page import PageRequest, PageResult
from src.common.result import Result
from src.core.dependencies import CurrentUserIdDep, SessionDep

router = APIRouter(prefix="/meal-records", tags=["饮食记录"])


@router.post("", response_model=Result[None], summary="新增饮食记录")
async def create_record(
    payload: MealRecordCreate,
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[None]:
    await meal_record_service.create_meal_record(payload, user_id, session)
    return Result.success()


@router.get("", response_model=Result[PageResult[MealRecordResponse]], summary="分页查询饮食记录")
async def list_records(
    user_id: CurrentUserIdDep,
    session: SessionDep,
    page: Annotated[PageRequest, Query()],
) -> Result[PageResult[MealRecordResponse]]:
    res = await meal_record_service.list_meal_records(page, user_id, session)
    return Result.success(res)


@router.get("/{record_id}", response_model=Result[MealRecordResponse], summary="查询饮食记录详情")
async def get_record(
    record_id: UUID,
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[MealRecordResponse]:
    res = await meal_record_service.get_meal_record(record_id, user_id, session)
    return Result.success(res)


@router.put("/{record_id}", response_model=Result[None], summary="更新饮食记录")
async def update_record(
    record_id: UUID,
    payload: MealRecordUpdate,
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[None]:
    await meal_record_service.update_meal_record(record_id, payload, user_id, session)
    return Result.success()


@router.delete("/{record_id}", response_model=Result[None], summary="删除饮食记录")
async def delete_record(
    record_id: UUID,
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[None]:
    await meal_record_service.delete_meal_record(record_id, user_id, session)
    return Result.success()
