from datetime import datetime
from typing import Any, cast
from uuid import uuid7

from sqlalchemy import CHAR, DateTime, FetchedValue, event, func, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    with_loader_criteria,
)


class BaseTable(DeclarativeBase):
    """所有业务表共享的 ORM 基类。"""

    __abstract__ = True

    id: Mapped[str] = mapped_column(
        CHAR(36), primary_key=True, default=lambda: str(uuid7()), comment="业务表主键 UUID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        server_onupdate=FetchedValue(),
        comment="最后更新时间",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True, comment="软删除时间，为空表示未删除"
    )

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now()

    def restore(self) -> None:
        self.deleted_at = None

    @classmethod
    async def soft_delete_by(cls, session: AsyncSession, **conditions: Any) -> int:
        """
        批量软删除符合条件的业务数据。

        :param session: 数据库会话
        :param conditions: 与模型字段同名的等值查询条件
        :return: 软删除的数据条数
        """

        result = cast(
            "CursorResult[Any]",
            await session.execute(
                update(cls)
                .filter_by(**conditions)
                .where(cls.deleted_at.is_(None))
                .values(deleted_at=datetime.now())
            ),
        )
        return result.rowcount


@event.listens_for(Session, "before_flush")
def _convert_deletes_to_soft_deletes(
    session: Session, _flush_context: Any, _instances: Any
) -> None:
    for instance in tuple(session.deleted):
        if isinstance(instance, BaseTable):
            instance.soft_delete()
            session.add(instance)


@event.listens_for(Session, "do_orm_execute")
def _exclude_deleted_rows(execute_state: Any) -> None:
    if (
        not execute_state.is_select
        or execute_state.is_column_load
        or execute_state.is_relationship_load
        or execute_state.execution_options.get("include_deleted", False)
    ):
        return

    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(
            BaseTable,
            lambda model: model.deleted_at.is_(None),
            include_aliases=True,
        )
    )
