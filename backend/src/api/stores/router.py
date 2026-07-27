from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.api.stores import service as store_service
from src.api.stores.schema import StoreCreate, StoreResponse
from src.common.page import PageRequest, PageResult
from src.common.result import Result
from src.core.dependencies import CurrentUserIdDep, SessionDep

router = APIRouter(prefix="/stores", tags=["店铺"])


@router.get("", response_model=Result[PageResult[StoreResponse]], summary="分页查询历史店铺")
async def list_stores(
    user_id: CurrentUserIdDep,
    session: SessionDep,
    page: Annotated[PageRequest, Depends()],
    keyword: Annotated[
        str | None, Query(max_length=128, description="店铺名称或地址关键字")
    ] = None,
) -> Result[PageResult[StoreResponse]]:
    stores = await store_service.list_stores(page, user_id, session, keyword)
    return Result.success(stores)


@router.post("", response_model=Result[StoreResponse], summary="保存地图店铺")
async def create_store(
    payload: StoreCreate,
    user_id: CurrentUserIdDep,
    session: SessionDep,
) -> Result[StoreResponse]:
    store = await store_service.create_store(payload, user_id, session)
    return Result.success(store)
