from typing import Optional

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Menu(Base):
    __tablename__ = "menu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 自引用父菜单，NULL = 根节点。禁止 DB 级外键，且本仓库没有自引用 relationship 的先例；
    # 菜单树由 crud/menu.py 用一次平铺查询在 Python 内组装（selectin 不递归，且每层一次往返）。
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    # name = 展示文案，与 Role.name / Permission.name 一致。不加独立的 code/key：
    # path 已是前端使用的稳定标识（菜单项的 key 就是路由路径）。
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    # 前端路由路径字符串。故意不加 DB 唯一约束：软删除会让「删除后重建同一路径」撞库，
    # 唯一性由 routers/menu.py 预查询（过滤 is_deleted == False）保证。
    path: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # 同级升序；并列时以 id 升序，保证顺序确定。
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # 手动显隐开关，与权限绑定相互独立，任一为假即隐藏。
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 可见性绑定的权限：持有该权限才可见，NULL = 所有登录用户可见。无 DB 外键。
    permission_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Menu(id={self.id}, path='{self.path}', name='{self.name}')>"
