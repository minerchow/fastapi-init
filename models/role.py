from typing import Optional, List
from sqlalchemy import Integer, String, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

# 角色-权限 关联表
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permission.id"), primary_key=True),
)

# 用户-角色 关联表
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Integer, default=0, nullable=False)

    # 关联
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permission,
        backref="roles",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"
