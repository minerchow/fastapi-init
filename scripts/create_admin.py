"""
创建第一个管理员用户并绑定 admin 角色（生产环境引导用）
运行方式: PYTHONPATH=. uv run python scripts/create_admin.py <用户名> [密码]
密码省略时交互式输入，避免落入 shell 历史。
依赖: 需先执行 scripts/init_rbac.py 种入角色与权限。
"""
import argparse
import asyncio
import getpass
import sys

from sqlalchemy import select, insert

from config.db_conf import AsyncSessionLocal
from models.role import user_role, Role
from models.user import User
from utils.security import get_hash_password


async def create_admin(username: str, password: str):
    async with AsyncSessionLocal() as db:
        try:
            # 1. 查找 admin 角色
            result = await db.execute(
                select(Role).where(Role.name == "admin", Role.is_deleted == False)
            )
            admin_role = result.scalars().one_or_none()
            if admin_role is None:
                print("错误: 不存在未删除的 admin 角色，请先执行 scripts/init_rbac.py")
                sys.exit(1)

            # 2. 创建或复活用户（username 唯一约束包含软删行）
            result = await db.execute(select(User).where(User.username == username))
            user = result.scalars().one_or_none()

            if user is None:
                user = User(username=username, password=get_hash_password(password))
                db.add(user)
                await db.flush()
                print(f"创建用户: {username} (id={user.id})")
            elif user.is_deleted:
                user.is_deleted = False
                user.password = get_hash_password(password)
                await db.flush()
                print(f"复活已软删用户: {username} (id={user.id})，已重置密码")
            else:
                user.password = get_hash_password(password)
                await db.flush()
                print(f"用户已存在: {username} (id={user.id})，已重置密码")

            # 3. 绑定 admin 角色（幂等）
            result = await db.execute(
                select(user_role).where(
                    user_role.c.user_id == user.id,
                    user_role.c.role_id == admin_role.id,
                )
            )
            if result.first() is None:
                await db.execute(
                    insert(user_role).values(user_id=user.id, role_id=admin_role.id)
                )
                print(f"绑定角色: admin (id={admin_role.id})")
            else:
                print(f"已绑定 admin 角色，跳过")

            await db.commit()
            print("\n完成。该账号登录即拥有全部权限（JWT 只存 user_id，权限实时查库，立即生效）。")

        except Exception as e:
            await db.rollback()
            raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="创建管理员用户并绑定 admin 角色")
    parser.add_argument("username", help="用户名")
    parser.add_argument("password", nargs="?", help="密码，省略则交互式输入")
    args = parser.parse_args()

    pwd = args.password or getpass.getpass(f"为 {args.username} 输入密码: ")
    if not pwd:
        print("错误: 密码不能为空")
        sys.exit(1)

    asyncio.run(create_admin(args.username, pwd))
