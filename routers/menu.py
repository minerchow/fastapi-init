from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from models.user import User
from schemas.menu import MenuCreate, MenuUpdate, MenuResponse
from crud.menu import (
    get_menu_by_id, get_menu_by_path, create_menu, update_menu, delete_menu,
    get_full_menu_tree, get_user_nav_tree,
)
from utils.response import success_response
from utils.auth import get_current_user
from utils.permissions import (
    require_permission, MENU_READ, MENU_CREATE, MENU_UPDATE, MENU_DELETE,
)

router = APIRouter(prefix="/api/menus", tags=["menus"])


# ==================== 用户导航树 ====================
# 静态路径必须声明在 /{menu_id} 之前：否则 /api/menus/nav 会被 menu_id: int 捕获，
# 在路径参数解析阶段返回 422 而不是走到预期分支。这是最容易复发的坑。

@router.get("/nav")
async def get_my_menus(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """当前用户可见的菜单树。

    只需登录态，不能要求 MENU_READ —— 普通用户的侧边栏也要用它。
    可见性由每个菜单绑定的权限决定：未绑定则所有登录用户可见；
    子菜单全部不可见时父节点一并裁剪。
    """
    tree = await get_user_nav_tree(db, user)
    return success_response(
        message="获取菜单导航成功",
        data=[node.model_dump() for node in tree]
    )


# ==================== 菜单管理（仅管理员） ====================

@router.get("/tree")
async def list_menu_tree(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(MENU_READ))
):
    """管理端全量树，不分页（菜单是配置表，参照 /api/roles/all），含被隐藏的菜单。"""
    tree = await get_full_menu_tree(db)
    return success_response(
        message="获取菜单树成功",
        data=[node.model_dump() for node in tree]
    )


@router.get("/{menu_id}")
async def get_menu_detail(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(MENU_READ))
):
    menu = await get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    return success_response(
        message="获取菜单详情成功",
        data=MenuResponse.model_validate(menu).model_dump()
    )


@router.post("")
async def create_new_menu(
    menu_data: MenuCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(MENU_CREATE))
):
    # menu.path 没有 DB 唯一约束（软删除会让「删了再建同一路径」撞库），
    # 唯一性靠这里过滤 is_deleted == False 的预查询保证。
    existing = await get_menu_by_path(db, menu_data.path)
    if existing:
        raise HTTPException(status_code=400, detail="菜单路径已存在")
    menu = await create_menu(db, menu_data)
    return success_response(
        message="创建菜单成功",
        data=MenuResponse.model_validate(menu).model_dump()
    )


@router.put("/{menu_id}")
async def update_existing_menu(
    menu_id: int,
    menu_data: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(MENU_UPDATE))
):
    menu = await get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    # 只在真的改名时查重，否则 PUT 自己的当前值会撞上自己。
    if menu_data.path and menu_data.path != menu.path:
        existing = await get_menu_by_path(db, menu_data.path)
        if existing:
            raise HTTPException(status_code=400, detail="菜单路径已存在")
    updated_menu = await update_menu(db, menu, menu_data)
    return success_response(
        message="更新菜单成功",
        data=MenuResponse.model_validate(updated_menu).model_dump()
    )


@router.delete("/{menu_id}")
async def delete_existing_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(MENU_DELETE))
):
    menu = await get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    deleted_menu = await delete_menu(db, menu)
    return success_response(
        message="删除菜单成功",
        data=MenuResponse.model_validate(deleted_menu).model_dump()
    )
