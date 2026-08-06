from datetime import datetime

from sqlalchemy import Boolean, CHAR, DateTime, String, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from src.models import BaseTable


class MealRecord(BaseTable):
    """饮食记录表 ORM 模型。"""

    __tablename__ = "meal_records"

    user_id: Mapped[str] = mapped_column(CHAR(36), nullable=False, comment="饮食记录所属用户 UUID")
    dish_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="菜品名称，一条记录只描述一道菜品"
    )
    eaten_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, comment="进食时间"
    )
    source_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="饮食来源：SELF_MADE 自己做，DINING_OUT 外面买，未选择时为空，由应用层校验",
    )
    store_id: Mapped[str | None] = mapped_column(
        CHAR(36), nullable=True, comment="外面买时可关联的店铺 UUID"
    )
    recipe_id: Mapped[str | None] = mapped_column(
        CHAR(36), nullable=True, comment="自己做时可关联的菜谱 UUID"
    )
    note: Mapped[str | None] = mapped_column(
        String(1000), nullable=True, comment="本次饮食记录的个人备注"
    )


class MealRecordImage(BaseTable):
    """饮食记录图片表 ORM 模型。"""

    __tablename__ = "meal_record_images"

    meal_record_id: Mapped[str] = mapped_column(
        CHAR(36), nullable=False, comment="所属饮食记录 UUID"
    )
    original_object_key: Mapped[str] = mapped_column(
        String(512), nullable=False, comment="原始图片在对象存储中的文件键"
    )
    sort_order: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        nullable=False,
        comment="图片展示顺序，从 0 开始，单条记录最多 9 张，由应用层校验",
    )
    is_cover: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("0"),
        comment="是否为当前记录封面：0 否，1 是，由应用层保证单封面",
    )
