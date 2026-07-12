from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
from fastapi import Depends, HTTPException, status

from utils.enums import UserRole
from utils.auth import get_current_user

if TYPE_CHECKING:
    from models.user import User


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        user_role = UserRole(user.role)
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return user


allow_user = RoleChecker([UserRole.USER, UserRole.AUTHOR, UserRole.ADMIN])
allow_author = RoleChecker([UserRole.AUTHOR, UserRole.ADMIN])
allow_admin = RoleChecker([UserRole.ADMIN])


async def get_current_user_optional(
    user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    return user
