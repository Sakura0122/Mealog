from decimal import Decimal

from sqlalchemy import CHAR, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import BaseTable


class Store(BaseTable):
    """店铺表 ORM 模型。"""

    __tablename__ = "stores"

    user_id: Mapped[str] = mapped_column(CHAR(36), nullable=False, comment="店铺所属用户 UUID")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="店铺名称")
    address: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="店铺地址")
    latitude: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7), nullable=True, comment="店铺纬度，范围 -90 到 90"
    )
    longitude: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7), nullable=True, comment="店铺经度，范围 -180 到 180"
    )
