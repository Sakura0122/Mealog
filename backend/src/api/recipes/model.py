from datetime import datetime

from sqlalchemy import CHAR, DateTime, String, Text, text
from sqlalchemy.dialects.mysql import SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from src.models import BaseTable


class Recipe(BaseTable):
    """菜谱表 ORM 模型。"""

    __tablename__ = "recipes"

    user_id: Mapped[str] = mapped_column(CHAR(36), nullable=False, comment="菜谱所属用户 UUID")
    source_recipe_id: Mapped[str | None] = mapped_column(
        CHAR(36), nullable=True, comment="从分享页保存时对应的原菜谱 UUID，自建菜谱为空"
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="菜谱名称，同一用户下不可重复"
    )
    cover_object_key: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="菜谱封面在对象存储中的文件键"
    )
    steps: Mapped[str | None] = mapped_column(Text, nullable=True, comment="菜谱制作步骤")
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'DRAFT'"),
        comment="菜谱状态：DRAFT 草稿，COMPLETED 已完善，由应用层根据食材和步骤计算并校验",
    )
    share_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        comment="分享过期时间，为空或早于当前时间表示不可访问",
    )


class RecipeIngredient(BaseTable):
    """菜谱食材表 ORM 模型。"""

    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[str] = mapped_column(CHAR(36), nullable=False, comment="所属菜谱 UUID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="食材名称")
    sort_order: Mapped[int] = mapped_column(
        SMALLINT(unsigned=True), nullable=False, comment="食材展示顺序，从 0 开始"
    )
