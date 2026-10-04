from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from fastapi import Depends, HTTPException, status

from utils.auth import get_current_user

if TYPE_CHECKING:
    from models.user import User


# ==================== 权限码常量 ====================

ARTICLE_READ = "article:read"
ARTICLE_CREATE = "article:create"
ARTICLE_UPDATE = "article:update"
ARTICLE_UPDATE_OWN = "article:update:own"
ARTICLE_DELETE = "article:delete"
ARTICLE_DELETE_OWN = "article:delete:own"

USER_READ = "user:read"
USER_CREATE = "user:create"
USER_UPDATE = "user:update"
USER_DELETE = "user:delete"
USER_ASSIGN_ROLE = "user:assign_role"

ROLE_READ = "role:read"
ROLE_CREATE = "role:create"
ROLE_UPDATE = "role:update"
ROLE_DELETE = "role:delete"


# ==================== 属主检查 ====================

def check_own_or_permission(user: "User", full_permission: str, owner_id: Optional[int]) -> None:
    """跨属主资源检查：拥有 full_permission 可操作任意资源，否则只能操作自己的。"""
    if owner_id == user.id or user.has_permission(full_permission):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="只能操作自己创建的资源"
    )


# ==================== 基于角色的检查 ====================

def require_role(role_name: str):
    """
    基于角色的依赖注入（RBAC 新方案）

    使用方式:
        @router.get("/items")
        async def get_items(user = Depends(require_role("admin"))):
            ...
    """
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.has_role(role_name):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"需要 {role_name} 角色"
        )
    return role_checker


def require_permission(permission_code: str):
    """
    基于权限的依赖注入（RBAC 新方案）

    使用方式:
        @router.post("/articles")
        async def create_article(user = Depends(require_permission("article:create"))):
            ...
    """
    def permission_checker(user: User = Depends(get_current_user)) -> User:
        if user.has_permission(permission_code):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"需要 {permission_code} 权限"
        )
    return permission_checker


def require_any_role(*role_names: str):
    """
    需要拥有任意一个指定角色

    使用方式:
        @router.delete("/items/{id}")
        async def delete_item(user = Depends(require_any_role("admin", "editor"))):
            ...
    """
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if any(user.has_role(name) for name in role_names):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"需要以下角色之一: {', '.join(role_names)}"
        )
    return role_checker


def require_any_permission(*permission_codes: str):
    """
    需要拥有任意一个指定权限

    使用方式:
        @router.delete("/items/{id}")
        async def delete_item(user = Depends(require_any_permission("article:delete", "admin:all"))):
            ...
    """
    def permission_checker(user: User = Depends(get_current_user)) -> User:
        if any(user.has_permission(code) for code in permission_codes):
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"需要以下权限之一: {', '.join(permission_codes)}"
        )
    return permission_checker


# ==================== 可选认证 ====================

async def get_current_user_optional(
    user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    return user
