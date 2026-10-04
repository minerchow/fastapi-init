from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

# 路径格式：以 / 开头，仅允许字母/数字/下划线/连字符/斜杠。
# 只用于写入校验，读出不校验 —— 若放进 MenuBase，一条手工插入的脏行会让
# MenuResponse / MenuTreeNode 在校验 ORM 对象时直接 500，把列表接口打死。
MENU_PATH_PATTERN = r"^/[A-Za-z0-9_\-/]*$"


class MenuBase(BaseModel):
    name: str = Field(..., max_length=50, description="菜单名称")
    path: str = Field(..., max_length=100, description="前端路由路径")
    icon: Optional[str] = Field(None, max_length=50, description="菜单图标")
    sort_order: int = Field(0, ge=0, description="同级排序，升序")
    is_visible: bool = Field(True, description="是否显示（手动开关）")
    parent_id: Optional[int] = Field(None, description="父菜单ID，NULL 表示根节点")
    permission_id: Optional[int] = Field(None, description="绑定的权限ID，NULL 表示所有登录用户可见")


class MenuCreate(MenuBase):
    # 收紧写入：路径格式非法直接 422。
    path: str = Field(..., max_length=100, pattern=MENU_PATH_PATTERN, description="前端路由路径，以 / 开头")


class MenuUpdate(BaseModel):
    # 约定：Update 不继承 Base，逐字段 Optional，配合 exclude_unset 做部分更新。
    # 显式传 null 的语义：parent_id = null 提升为根，permission_id = null 解除权限绑定。
    name: Optional[str] = Field(None, max_length=50, description="菜单名称")
    path: Optional[str] = Field(None, max_length=100, pattern=MENU_PATH_PATTERN, description="前端路由路径")
    icon: Optional[str] = Field(None, max_length=50, description="菜单图标")
    sort_order: Optional[int] = Field(None, ge=0, description="同级排序，升序")
    is_visible: Optional[bool] = Field(None, description="是否显示（手动开关）")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    permission_id: Optional[int] = Field(None, description="绑定的权限ID")


class MenuResponse(MenuBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MenuTreeNode(BaseModel):
    """管理端全量树与用户导航树共用的节点载荷。

    由 crud/menu.py 在 Python 内构造（不是 ORM 对象），因此不需要 from_attributes。
    时间戳不进树载荷，需要时走 GET /api/menus/{menu_id} 取详情。
    """
    id: int
    parent_id: Optional[int] = None
    name: str
    path: str
    icon: Optional[str] = None
    sort_order: int
    is_visible: bool
    permission_id: Optional[int] = None
    # 绑定权限的 code，冗余下发便于前端展示「这条菜单要哪个权限」；
    # 为 None 有两种含义：未绑定权限，或绑定的权限已被软删除（导航里按隐藏处理）。
    permission_code: Optional[str] = None
    children: List["MenuTreeNode"] = Field(default_factory=list, description="子菜单")


# 自引用模型的 forward ref 需要显式 rebuild 才能确定解析（重复调用是 no-op）。
MenuTreeNode.model_rebuild()
