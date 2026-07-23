from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.meal_records.model import MealRecord, MealRecordImage
from src.api.meal_records.schema import (
    MealRecordCreate,
    MealRecordImageInput,
    MealRecordImageResponse,
    MealRecordResponse,
    MealRecordUpdate,
    MealSourceType,
)
from src.api.recipes.model import Recipe
from src.api.stores.model import Store
from src.common.exceptions import BusinessException
from src.common.page import PageRequest, PageResult
from src.common.result_code import ResultCodeEnum
from src.rustfs.url import build_public_file_url


async def _validate_relations(
    payload: MealRecordCreate | MealRecordUpdate,
    user_id: UUID,
    session: AsyncSession,
) -> None:
    """
    校验饮食来源与关联店铺、菜谱之间的业务关系及数据归属。

    :param payload: 饮食记录创建或更新参数
    :param user_id: 当前用户 ID
    :param session: 数据库会话
    :return: 无返回值
    """

    if payload.source_type == "SELF_MADE" and payload.store_id is not None:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "自己做的记录不能关联店铺")
    if payload.source_type == "DINING_OUT" and payload.recipe_id is not None:
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "外面买的记录不能关联菜谱")
    if payload.source_type is None and (
        payload.store_id is not None or payload.recipe_id is not None
    ):
        raise BusinessException(ResultCodeEnum.PARAM_ERROR, "未选择饮食来源时不能关联店铺或菜谱")

    user_id_value = str(user_id)
    if payload.store_id is not None:
        store = await session.scalar(
            select(Store).where(Store.id == str(payload.store_id), Store.user_id == user_id_value)
        )
        if store is None:
            raise BusinessException(ResultCodeEnum.PARAM_ERROR, "关联店铺不存在或无权限")

    if payload.recipe_id is not None:
        recipe = await session.scalar(
            select(Recipe).where(
                Recipe.id == str(payload.recipe_id), Recipe.user_id == user_id_value
            )
        )
        if recipe is None:
            raise BusinessException(ResultCodeEnum.PARAM_ERROR, "关联菜谱不存在或无权限")


async def _get_owned_record(
    record_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> MealRecord:
    """
    查询属于当前用户的饮食记录。

    :param record_id: 饮食记录 ID
    :param user_id: 当前用户 ID
    :param session: 数据库会话
    :return: 当前用户的饮食记录
    """

    record = await session.scalar(
        select(MealRecord).where(
            MealRecord.id == str(record_id),
            MealRecord.user_id == str(user_id),
        )
    )
    if record is None:
        # 不区分记录不存在和属于其他用户，避免泄露他人数据。
        raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "饮食记录不存在")
    return record


def _create_images(record_id: str, images: list[MealRecordImageInput]) -> list[MealRecordImage]:
    """
    按请求顺序构建饮食记录图片模型，并将首张图片设为封面。

    :param record_id: 饮食记录 ID
    :param images: 饮食记录图片参数列表
    :return: 待写入数据库的饮食记录图片模型列表
    """

    return [
        MealRecordImage(
            meal_record_id=record_id,
            original_object_key=image.original_object_key,
            processed_object_key=image.processed_object_key,
            sort_order=index,
            is_cover=index == 0,
        )
        for index, image in enumerate(images)
    ]


async def _replace_images(
    record_id: str,
    images: list[MealRecordImageInput],
    session: AsyncSession,
) -> None:
    """
    软删除饮食记录的原图片并创建新图片。

    :param record_id: 饮食记录 ID
    :param images: 新的饮食记录图片参数列表
    :param session: 数据库会话
    :return: 无返回值
    """

    await MealRecordImage.soft_delete_by(session, meal_record_id=record_id)
    session.add_all(_create_images(record_id, images))


def _to_image_response(image: MealRecordImage) -> MealRecordImageResponse:
    """
    将饮食记录图片模型转换为包含公开访问地址的响应数据。

    :param image: 饮食记录图片模型
    :return: 饮食记录图片响应数据
    """

    return MealRecordImageResponse(
        id=image.id,
        original_object_key=image.original_object_key,
        original_url=build_public_file_url(image.original_object_key),
        processed_object_key=image.processed_object_key,
        processed_url=(
            build_public_file_url(image.processed_object_key)
            if image.processed_object_key is not None
            else None
        ),
        sort_order=image.sort_order,
        is_cover=image.is_cover,
    )


def _to_record_response(
    record: MealRecord,
    images: list[MealRecordImage],
) -> MealRecordResponse:
    """
    将饮食记录及其图片转换为完整响应数据。

    :param record: 饮食记录模型
    :param images: 饮食记录图片模型列表
    :return: 饮食记录响应数据
    """

    return MealRecordResponse(
        id=record.id,
        dish_name=record.dish_name,
        eaten_at=record.eaten_at,
        source_type=cast("MealSourceType | None", record.source_type),
        store_id=record.store_id,
        recipe_id=record.recipe_id,
        note=record.note,
        images=[_to_image_response(image) for image in images],
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


async def _get_record_images(
    record_ids: list[str],
    session: AsyncSession,
) -> dict[str, list[MealRecordImage]]:
    """
    批量查询饮食记录图片并按记录 ID 分组。

    :param record_ids: 饮食记录 ID 列表
    :param session: 数据库会话
    :return: 以饮食记录 ID 为键的图片列表
    """

    if not record_ids:
        return {}

    images = (
        await session.scalars(
            select(MealRecordImage)
            .where(MealRecordImage.meal_record_id.in_(record_ids))
            .order_by(MealRecordImage.meal_record_id, MealRecordImage.sort_order)
        )
    ).all()
    grouped_images: dict[str, list[MealRecordImage]] = {record_id: [] for record_id in record_ids}
    for image in images:
        grouped_images[image.meal_record_id].append(image)
    return grouped_images


async def create_meal_record(
    payload: MealRecordCreate,
    user_id: UUID,
    session: AsyncSession,
) -> None:
    """
    创建当前用户的饮食记录及其图片。

    :param payload: 饮食记录创建参数
    :param user_id: 当前用户 ID
    :param session: 数据库会话
    :return: 无返回值
    """

    # 1. 校验饮食来源与关联店铺、菜谱的关系及数据归属
    await _validate_relations(payload, user_id, session)

    # 2. 创建饮食记录，并刷新数据库生成的记录 ID
    record = MealRecord(
        user_id=str(user_id),
        dish_name=payload.dish_name,
        eaten_at=payload.eaten_at,
        source_type=payload.source_type,
        store_id=str(payload.store_id) if payload.store_id is not None else None,
        recipe_id=str(payload.recipe_id) if payload.recipe_id is not None else None,
        note=payload.note,
    )
    session.add(record)
    await session.flush()

    # 3. 按请求顺序创建图片，首张图片作为封面
    session.add_all(_create_images(record.id, payload.images))
    await session.flush()


async def list_meal_records(
    page: PageRequest,
    user_id: UUID,
    session: AsyncSession,
) -> PageResult[MealRecordResponse]:
    """
    分页查询当前用户的饮食记录。

    :param page: 分页及排序参数
    :param user_id: 当前用户 ID
    :param session: 数据库会话
    :return: 饮食记录分页数据
    """

    # 1. 按当前用户统计未删除的饮食记录总数
    user_filter = MealRecord.user_id == str(user_id)
    total = await session.scalar(select(func.count()).select_from(MealRecord).where(user_filter))

    # 2. 按分页和排序参数查询当前页记录
    records = (
        await session.scalars(
            select(MealRecord)
            .where(user_filter)
            .order_by(
                *page.to_order_by({"eaten_at": MealRecord.eaten_at}, [MealRecord.eaten_at.desc()])
            )
            .offset(page.offset)
            .limit(page.page_size)
        )
    ).all()

    # 3. 批量查询当前页图片，避免逐条查询
    images_by_record = await _get_record_images([record.id for record in records], session)

    # 4. 组装记录响应和分页信息
    items = [_to_record_response(record, images_by_record[record.id]) for record in records]
    return PageResult.of(page, total or 0, items)


async def get_meal_record(
    record_id: UUID,
    user_id: UUID,
    session: AsyncSession,
) -> MealRecordResponse:
    """
    查询当前用户的单条饮食记录详情。

    :param record_id: 饮食记录 ID
    :param user_id: 当前用户 ID
    :param session: 数据库会话
    :return: 饮食记录详情
    """

    # 1. 按记录 ID 和当前用户查询记录，避免访问其他用户的数据
    record = await _get_owned_record(record_id, user_id, session)

    # 2. 查询记录图片并组装详情响应
    images = (await _get_record_images([record.id], session))[record.id]
    return _to_record_response(record, images)


async def update_meal_record(
    record_id: UUID,
    payload: MealRecordUpdate,
    user_id: UUID,
    session: AsyncSession,
) -> None:
    """
    更新当前用户的饮食记录及其图片。

    :param record_id: 饮食记录 ID
    :param payload: 饮食记录更新参数
    :param user_id: 当前用户 ID
    :param session: 数据库会话
    :return: 无返回值
    """

    # 1. 查询当前用户的记录，并校验更新后的关联关系
    record = await _get_owned_record(record_id, user_id, session)
    await _validate_relations(payload, user_id, session)

    # 2. 更新饮食记录的基础字段
    record.dish_name = payload.dish_name
    record.eaten_at = payload.eaten_at
    record.source_type = payload.source_type
    record.store_id = str(payload.store_id) if payload.store_id is not None else None
    record.recipe_id = str(payload.recipe_id) if payload.recipe_id is not None else None
    record.note = payload.note

    # 3. 软删除原图片并按请求顺序创建新图片
    await _replace_images(record.id, payload.images, session)
    await session.flush()


async def delete_meal_record(record_id: UUID, user_id: UUID, session: AsyncSession) -> None:
    """
    软删除当前用户的饮食记录及其图片。

    :param record_id: 饮食记录 ID
    :param user_id: 当前用户 ID
    :param session: 数据库会话
    :return: 无返回值
    """

    # 1. 按记录 ID 和当前用户批量软删除记录
    deleted_count = await MealRecord.soft_delete_by(
        session,
        id=str(record_id),
        user_id=str(user_id),
    )

    # 2. 未更新任何记录时，统一按记录不存在处理，避免泄露他人数据
    if deleted_count == 0:
        raise BusinessException(ResultCodeEnum.NOT_FOUND_ERROR, "饮食记录不存在")

    # 3. 批量软删除关联图片
    await MealRecordImage.soft_delete_by(session, meal_record_id=str(record_id))
