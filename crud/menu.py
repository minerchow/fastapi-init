from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.menu import Menu
from models.permission import Permission
from models.user import User
from schemas.menu import MenuCreate, MenuTreeNode, MenuUpdate

# 菜单树最大层级（根为 1）。前端 antd Menu 目前渲染两级，这里留一级余量。
# 只在 validate_parent_placement 强制；树组装不设深度闸门，
# 否则历史深数据会在管理树里静默消失（宁可在界面上看得见并修好）。
MENU_MAX_DEPTH = 3


# ==================== 查询 ====================

async def get_menu_by_id(db: AsyncSession, menu_id: int) -> Menu | None:
    query = select(Menu).where(Menu.id == menu_id, Menu.is_deleted == False)
    result = await db.execute(query)
    return result.scalars().one_or_none()


async def get_menu_by_path(db: AsyncSession, path: str) -> Menu | None:
    """路径唯一性预查询（menu.path 没有 DB 唯一约束，见 models/menu.py）。"""
    query = select(Menu).where(Menu.path == path, Menu.is_deleted == False)
    result = await db.execute(query)
    return result.scalars().one_or_none()


async def get_all_menus(db: AsyncSession) -> list[Menu]:
    """一次平铺查询取回全部未删除菜单，树在 Python 内组装（无 N+1）。"""
    query = (
        select(Menu)
        .where(Menu.is_deleted == False)
        .order_by(Menu.sort_order.asc(), Menu.id.asc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def count_child_menus(db: AsyncSession, menu_id: int) -> int:
    query = select(func.count(Menu.id)).where(
        Menu.parent_id == menu_id, Menu.is_deleted == False
    )
    result = await db.execute(query)
    return int(result.scalar() or 0)


async def get_permission_code_map(
    db: AsyncSession, permission_ids: set[int | None]
) -> dict[int, str]:
    """把被引用的 permission_id 一次性解析成 code，避免逐行查询。

    已软删除或不存在的权限不会出现在结果里 —— 调用方据此判定「绑定失效 = 隐藏」。
    """
    ids = {pid for pid in permission_ids if pid is not None}
    if not ids:
        return {}
    query = select(Permission.id, Permission.code).where(
        Permission.id.in_(ids), Permission.is_deleted == False
    )
    result = await db.execute(query)
    return {row[0]: row[1] for row in result.all()}


async def require_permission_exists(db: AsyncSession, permission_id: int) -> None:
    codes = await get_permission_code_map(db, {permission_id})
    if permission_id not in codes:
        raise HTTPException(status_code=400, detail=f"以下权限不存在: {[permission_id]}")


# ==================== 树组装（纯函数，不碰 DB） ====================

def group_menus_by_parent(menus: list[Menu]) -> dict[int | None, list[Menu]]:
    """按父节点分组，并按 (sort_order, id) 升序排定同级顺序。

    两条容错，都表现为「提升为根」而不是丢数据：
    1) parent_id 指向已软删除或不存在的菜单（孤儿）；
    2) parent_id 指向自己（脏数据）。
    """
    ids = {m.id for m in menus}
    children_map: dict[int | None, list[Menu]] = defaultdict(list)
    for m in menus:
        parent = m.parent_id if (m.parent_id in ids and m.parent_id != m.id) else None
        children_map[parent].append(m)
    for bucket in children_map.values():
        bucket.sort(key=lambda m: (m.sort_order, m.id))
    return children_map


def _to_node(
    menu: Menu, children: list[MenuTreeNode], permission_codes: dict[int, str]
) -> MenuTreeNode:
    permission_code = (
        permission_codes.get(menu.permission_id) if menu.permission_id is not None else None
    )
    return MenuTreeNode(
        id=menu.id,
        parent_id=menu.parent_id,
        name=menu.name,
        path=menu.path,
        icon=menu.icon,
        sort_order=menu.sort_order,
        is_visible=menu.is_visible,
        permission_id=menu.permission_id,
        permission_code=permission_code,
        children=children,
    )


def _assemble_tree(
    menus: list[Menu],
    permission_codes: dict[int, str],
    keep,
) -> list[MenuTreeNode]:
    """通用装配：keep(menu, has_children, visible_children) -> bool 决定节点去留。

    复杂度 O(menus)，查询次数 0（数据已在上层一次取回）。
    visiting 集合是纯防御：真环里的节点全都带 parent 且父节点在集合内，
    因此没有任何成员会落在根上，从根出发本来就到达不了它们。
    """
    children_map = group_menus_by_parent(menus)
    visiting: set[int] = set()

    def attach(parent_id: int | None) -> list[MenuTreeNode]:
        nodes: list[MenuTreeNode] = []
        for child in children_map.get(parent_id, []):
            if child.id in visiting:
                continue
            visiting.add(child.id)
            has_children = bool(children_map.get(child.id))
            visible_children = attach(child.id)
            visiting.discard(child.id)
            if keep(child, has_children, visible_children):
                nodes.append(_to_node(child, visible_children, permission_codes))
        return nodes

    return attach(None)


def build_menu_tree(
    menus: list[Menu], permission_codes: dict[int, str] | None = None
) -> list[MenuTreeNode]:
    """管理端全量树：不做可见性裁剪，隐藏的菜单管理员也要能看见并修改。"""
    return _assemble_tree(
        menus,
        permission_codes or {},
        lambda menu, has_children, visible_children: True,
    )


def get_user_permission_codes(user: User) -> set[str]:
    """收集当前用户的全部权限码。

    User.roles 与 Role.permissions 都是 lazy="selectin"，get_current_user 取回的
    User 已级联加载完毕，因此这里不触发任何额外查询。
    """
    return {perm.code for role in user.roles for perm in role.permissions}


def filter_menus_for_user(
    menus: list[Menu], user_codes: set[str], permission_codes: dict[int, str]
) -> list[MenuTreeNode]:
    """用户导航树。自上而下判定可见，自下而上裁剪空父。

    - is_visible == False        → 整棵子树隐藏
    - 绑定了权限：用户没有该 code，或该权限已被软删除 → 隐藏（deny-by-default）
    - 未绑定权限                 → 所有登录用户可见
    - 有子节点但可见子节点为空   → 裁掉父节点（纯叶子不受此规则影响）
    """
    def keep(menu: Menu, has_children: bool, visible_children: list[MenuTreeNode]) -> bool:
        if not menu.is_visible:
            return False
        if menu.permission_id is not None:
            code = permission_codes.get(menu.permission_id)
            if code is None or code not in user_codes:
                return False
        if has_children and not visible_children:
            return False
        return True

    return _assemble_tree(menus, permission_codes, keep)


async def get_full_menu_tree(db: AsyncSession) -> list[MenuTreeNode]:
    menus = await get_all_menus(db)
    codes = await get_permission_code_map(
        db, {m.permission_id for m in menus if m.permission_id is not None}
    )
    return build_menu_tree(menus, codes)


async def get_user_nav_tree(db: AsyncSession, user: User) -> list[MenuTreeNode]:
    """共 2 次查询（菜单一次、被引用权限一次），与菜单条数无关。"""
    menus = await get_all_menus(db)
    codes = await get_permission_code_map(
        db, {m.permission_id for m in menus if m.permission_id is not None}
    )
    return filter_menus_for_user(menus, get_user_permission_codes(user), codes)


# ==================== 层级 / 环校验（纯函数） ====================

def _parent_depth(by_id: dict[int, Menu], menu_id: int | None, parent_id: int) -> int:
    """返回目标父节点所在的层级（根节点为 1）。沿 parent_id 向上走，visited 保证终止。"""
    depth = 0
    current: int | None = parent_id
    visited: set[int] = set()
    while current is not None:
        if menu_id is not None and current == menu_id:
            raise HTTPException(status_code=400, detail="上级菜单不能选择自己或自己的子菜单")
        if current in visited:
            raise HTTPException(status_code=400, detail="现有菜单层级存在环，请先修复数据")
        node = by_id.get(current)
        if node is None:
            raise HTTPException(status_code=400, detail="上级菜单不存在")
        visited.add(current)
        current = node.parent_id
        depth += 1
    return depth


def _subtree_height(children_map: dict[int | None, list[Menu]], menu_id: int) -> int:
    """menu_id 自身子树的高度（叶子为 1）。迭代 + seen，脏数据环也不会死循环。"""
    height = 0
    stack: list[tuple[int, int]] = [(menu_id, 1)]
    seen: set[int] = set()
    while stack:
        node_id, level = stack.pop()
        if node_id in seen:
            continue
        seen.add(node_id)
        height = max(height, level)
        for child in children_map.get(node_id, []):
            stack.append((child.id, level + 1))
    return height


def validate_parent_placement(
    menus: list[Menu], menu_id: int | None, parent_id: int | None
) -> None:
    """创建（menu_id=None）与改父（menu_id=已有 id）共用。

    新建节点高度视为 1；移动已有节点时把它的整棵子树高度一起计入，
    否则「把三级子树挂到二级父节点下」就能绕过深度限制。
    """
    by_id = {m.id: m for m in menus}
    children_map = group_menus_by_parent(menus)
    height = _subtree_height(children_map, menu_id) if menu_id is not None else 1
    parent_depth = _parent_depth(by_id, menu_id, parent_id) if parent_id is not None else 0
    if parent_depth + height > MENU_MAX_DEPTH:
        raise HTTPException(status_code=400, detail=f"菜单层级不能超过 {MENU_MAX_DEPTH} 级")


# ==================== 写入 ====================

async def create_menu(db: AsyncSession, menu_data: MenuCreate) -> Menu:
    menus = await get_all_menus(db)
    validate_parent_placement(menus, None, menu_data.parent_id)
    if menu_data.permission_id is not None:
        await require_permission_exists(db, menu_data.permission_id)

    menu = Menu(
        name=menu_data.name,
        path=menu_data.path,
        icon=menu_data.icon,
        sort_order=menu_data.sort_order,
        is_visible=menu_data.is_visible,
        parent_id=menu_data.parent_id,
        permission_id=menu_data.permission_id,
    )
    db.add(menu)
    await db.flush()
    await db.refresh(menu)
    return menu


async def update_menu(db: AsyncSession, menu: Menu, menu_data: MenuUpdate) -> Menu:
    update_data = menu_data.model_dump(exclude_unset=True)

    if "parent_id" in update_data and update_data["parent_id"] != menu.parent_id:
        menus = await get_all_menus(db)
        validate_parent_placement(menus, menu.id, update_data["parent_id"])

    if update_data.get("permission_id") is not None:
        await require_permission_exists(db, update_data["permission_id"])

    # 与 crud/role.py:75-77 不同：Menu 没有 relationship 字段，
    # 所以这里不需要跳过任何键，update_data 的每个键都是真实列。
    for field, value in update_data.items():
        setattr(menu, field, value)

    await db.flush()
    await db.refresh(menu)
    return menu


async def delete_menu(db: AsyncSession, menu: Menu) -> Menu:
    """软删除。存在未删除子菜单时拒绝。

    菜单是共享配置且带权限绑定：级联软删会静默摧毁一棵子树且无从撤销
    （对照 crud/user.py:77-84 的用户→文章级联，那是属主内容，不是共享配置）；
    把子节点孤儿化到根则会擅自改变它们的导航层级。
    """
    if await count_child_menus(db, menu.id) > 0:
        raise HTTPException(status_code=400, detail="存在子菜单，无法删除")
    menu.is_deleted = True
    await db.flush()
    await db.refresh(menu)
    return menu
