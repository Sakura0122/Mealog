from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import BaseTable


class User(BaseTable):
    """用户表 ORM 模型。"""

    __tablename__ = "users"

    wechat_openid: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="微信小程序用户 OpenID"
    )
    wechat_unionid: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="微信开放平台 UnionID，未绑定开放平台时为空"
    )
    nickname: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="用户昵称")
    avatar_object_key: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="用户头像在对象存储中的文件键"
    )
