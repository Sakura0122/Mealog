from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.meal_records.model import MealRecord
from src.api.stores.model import Store
from src.api.stores.schema import StoreCreate, StoreResponse
from src.common.page import PageRequest, PageResult


async def list_stores(
    page: PageRequest,
    user_id: UUID,
    session: AsyncSession,
    keyword: str | None = None,
) -> PageResult[StoreResponse]:
    """按名称或地址分页查询当前用户保存的店铺。"""

    filters = [Store.user_id == str(user_id)]
    normalized_keyword = keyword.strip() if keyword is not None else ""
    if normalized_keyword:
        filters.append(
            or_(
                Store.name.contains(normalized_keyword, autoescape=True),
                Store.address.contains(normalized_keyword, autoescape=True),
            )
        )

    usage_count = _usage_count_subquery()
    total = await session.scalar(select(func.count()).select_from(Store).where(*filters))
    rows = (
        await session.execute(
            select(Store, usage_count)
            .where(*filters)
            .order_by(
                *page.to_order_by(
                    {"name": Store.name, "updated_at": Store.updated_at},
                    [usage_count.desc(), Store.updated_at.desc()],
                )
            )
            .offset(page.offset)
            .limit(page.page_size)
        )
    ).all()

    return PageResult.of(
        page,
        total or 0,
        [_to_store_response(store, count) for store, count in rows],
    )


async def create_store(
    payload: StoreCreate,
    user_id: UUID,
    session: AsyncSession,
) -> StoreResponse:
    """保存地图店铺；同一用户再次选择同一坐标时复用已有店铺。"""

    # 地图坐标按数据库精度比较，避免同一地点因浮点表示差异重复保存。
    latitude = _normalize_coordinate(payload.latitude)
    longitude = _normalize_coordinate(payload.longitude)
    store = await session.scalar(
        select(Store).where(
            Store.user_id == str(user_id),
            Store.latitude == latitude,
            Store.longitude == longitude,
        )
    )
    if store is None:
        store = Store(
            user_id=str(user_id),
            name=payload.name,
            address=payload.address,
            latitude=latitude,
            longitude=longitude,
        )
        session.add(store)
        await session.flush()
    elif store.name != payload.name or store.address != payload.address:
        # 腾讯地图信息发生变化时同步最新名称和地址，不创建重复历史项。
        store.name = payload.name
        store.address = payload.address
        await session.flush()

    # 响应包含数据库生成或更新的时间字段，刷新后再读取可避免异步延迟加载。
    await session.refresh(store)

    usage_count = await session.scalar(
        select(func.count()).select_from(MealRecord).where(MealRecord.store_id == store.id)
    )
    return _to_store_response(store, usage_count or 0)


def _normalize_coordinate(value: Decimal) -> Decimal:
    """将地图坐标统一到数据库保存的 7 位小数精度。"""

    return value.quantize(Decimal("0.0000001"))


def _usage_count_subquery():
    """构建统计每个店铺有效饮食记录数量的相关子查询。"""

    return (
        select(func.count())
        .select_from(MealRecord)
        .where(MealRecord.store_id == Store.id)
        .correlate(Store)
        .scalar_subquery()
    )


def _to_store_response(store: Store, usage_count: int) -> StoreResponse:
    """将店铺模型转换为带使用次数的响应。"""

    return StoreResponse(
        id=store.id,
        name=store.name,
        address=store.address,
        latitude=store.latitude,
        longitude=store.longitude,
        usage_count=usage_count,
        updated_at=store.updated_at,
    )
