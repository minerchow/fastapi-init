"""
菜单基础数据初始化脚本
运行方式: PYTHONPATH=. uv run python scripts/init_menus.py
前置: 先执行 alembic upgrade head 与 scripts/init_rbac.py（菜单要绑定的权限码需已存在）

不并进 init_rbac.py 的原因：那边幂等的是「权限码 + 角色授予」，这里幂等的是
「path + 父层级 + 权限绑定」，自然键不同；合并还会让 init_rbac.py 依赖一张它
本来不知道存在的 menu 表。

幂等键 = menu.path（含软删除行：命中已软删除的同路径行则复活并同步字段）。
父菜单依赖列表顺序，父必须排在子之前。
"""
import asyncio
from config.db_conf import AsyncSessionLocal
from models.menu import Menu
from models.permission import Permission
from sqlalchemy import select


# 与前端 src/config/menu.ts 当前硬编码的树一一对应。
# 父节点一律不绑定权限：不存在「并集码」这种东西，为父节点造一个 system:manage
# 就得在每次叶子权限变化时手工维护；而「子项全部不可见则裁掉父项」的规则
# （见 crud/menu.filter_menus_for_user）已经自动表达了并集语义，父节点只负责结构。
MENUS = [
    {"path": "/home", "name": "首页", "parent": None, "permission_code": None, "sort_order": 1},
    {"path": "/home/user", "name": "用户管理", "parent": None, "permission_code": None, "sort_order": 2},
    {"path": "/home/user/list", "name": "用户列表", "parent": "/home/user", "permission_code": "user:read", "sort_order": 1},
    {"path": "/home/system", "name": "系统管理", "parent": None, "permission_code": None, "sort_order": 3},
    {"path": "/home/system/role", "name": "角色管理", "parent": "/home/system", "permission_code": "role:read", "sort_order": 1},
    # 绑 role:read 而非发明 permission:read —— GET /api/permissions 用的就是 ROLE_READ
    # （routers/role.py）。代价是 role:read 会同时揭示角色管理和权限管理两页。
    {"path": "/home/system/permission", "name": "权限管理", "parent": "/home/system", "permission_code": "role:read", "sort_order": 2},
    # 侧边栏改读 /api/menus/nav 之后，这条菜单行就是管理页唯一的入口：
    # 没有它，admin 也看不到「菜单管理」。绑 menu:read = 能看到入口的人正好是能操作菜单的人。
    {"path": "/home/system/menu", "name": "菜单管理", "parent": "/home/system", "permission_code": "menu:read", "sort_order": 3},
]


async def init_menus():
    async with AsyncSessionLocal() as db:
        try:
            # 1. 权限 code -> id
            print("正在读取权限...")
            result = await db.execute(
                select(Permission.id, Permission.code).where(Permission.is_deleted == False)
            )
            permission_map = {code: pid for pid, code in result.all()}

            # 2. 现有菜单（含软删除）path -> 行
            print("\n正在初始化菜单...")
            result = await db.execute(select(Menu))
            existing_by_path = {m.path: m for m in result.scalars().all()}
            menu_id_by_path = {
                m.path: m.id for m in existing_by_path.values() if not m.is_deleted
            }

            for spec in MENUS:
                if spec["permission_code"] and spec["permission_code"] not in permission_map:
                    raise RuntimeError(
                        f"权限码不存在或已被软删除: {spec['permission_code']}"
                    )

                parent_id = None
                if spec["parent"] is not None:
                    if spec["parent"] not in menu_id_by_path:
                        raise RuntimeError(f"父菜单不存在，请检查列表顺序: {spec['parent']}")
                    parent_id = menu_id_by_path[spec["parent"]]

                permission_id = (
                    permission_map.get(spec["permission_code"]) if spec["permission_code"] else None
                )
                row = existing_by_path.get(spec["path"])

                if row is None:
                    row = Menu(
                        path=spec["path"],
                        name=spec["name"],
                        parent_id=parent_id,
                        permission_id=permission_id,
                        sort_order=spec["sort_order"],
                        is_visible=True,
                        icon=None,
                    )
                    db.add(row)
                    await db.flush()
                    menu_id_by_path[spec["path"]] = row.id
                    print(f"  创建菜单: {spec['path']} - {spec['name']}")
                else:
                    if row.is_deleted:
                        row.is_deleted = False
                        print(f"  恢复菜单: {spec['path']}")
                    row.name = spec["name"]
                    row.parent_id = parent_id
                    row.permission_id = permission_id
                    row.sort_order = spec["sort_order"]
                    await db.flush()
                    menu_id_by_path[spec["path"]] = row.id
                    print(f"  菜单已存在: {spec['path']} (id={row.id})，已同步层级/绑定")

            await db.commit()
            print("\n菜单基础数据初始化完成!")

        except Exception as e:
            await db.rollback()
            raise e


if __name__ == "__main__":
    asyncio.run(init_menus())
