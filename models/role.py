from typing import Optional, List
from sqlalchemy import Boolean, Integer, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

# 角色-权限 关联表
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, primary_key=True),
    Column("permission_id", Integer, primary_key=True),
)

# 用户-角色 关联表
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, primary_key=True),
    Column("role_id", Integer, primary_key=True),
)


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 关联。secondaryjoin 过滤软删除权限，防止已删权限继续生效。
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permission,
        primaryjoin="Role.id == role_permission.c.role_id",
        secondaryjoin="and_(Permission.id == role_permission.c.permission_id, Permission.is_deleted == False)",
        backref="roles",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"
