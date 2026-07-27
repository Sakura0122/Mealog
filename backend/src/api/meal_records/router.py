from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.meal_records import service as meal_record_service
from src.api.meal_records.schema import (
    MealRecordCalendarResponse,
    MealRecordCreate,
    MealRecordCreateResponse,
    MealRecordListItemResponse,
    MealRecordResponse,
    MealRecordUpdate,
)
from src.common.page import PageRequest, PageResult
from src.common.result import Result
from src.core.dependencies import CurrentUserIdDep, SessionDep

router = APIRouter(prefix="/meal-records", tags=["饮食记录"])


@router.post("", response_model=Result[MealRecordCreateResponse], summary="新增饮食记录")
async def create_record(
    payload: MealRecordCreate,
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[MealRecordCreateResponse]:
    record_id = await meal_record_service.create_meal_record(payload, user_id, session)
    return Result.success(MealRecordCreateResponse(id=record_id))


@router.get(
    "",
    response_model=Result[PageResult[MealRecordListItemResponse]],
    summary="分页查询饮食记录",
)
async def list_records(
    user_id: CurrentUserIdDep,
    session: SessionDep,
    page: Annotated[PageRequest, Depends()],
    target_date: Annotated[
        date | None,
        Query(alias="date", description="进食日期，格式为 YYYY-MM-DD"),
    ] = None,
) -> Result[PageResult[MealRecordListItemResponse]]:
    res = await meal_record_service.list_meal_records(page, user_id, session, target_date)
    return Result.success(res)


@router.get(
    "/calendar",
    response_model=Result[MealRecordCalendarResponse],
    summary="查询饮食记录月历",
)
async def get_record_calendar(
    month: Annotated[
        str,
        Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="月份，格式为 YYYY-MM"),
    ],
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[MealRecordCalendarResponse]:
    res = await meal_record_service.get_meal_record_calendar(month, user_id, session)
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
