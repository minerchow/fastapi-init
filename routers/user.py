from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse, UserLogin, LoginResponse, TokenData, RefreshTokenRequest, UserRoleUpdate
from crud.user import get_user_by_username, create_user, get_user_by_id, update_user_role
from utils.response import success_response
from utils.auth import get_current_user, create_tokens, verify_refresh_token
from utils.security import verify_password
from utils.permissions import allow_admin

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    new_user = await create_user(db, user_data)
    return success_response(
        message="注册成功",
        data=UserResponse.model_validate(new_user)
    )


@router.post("/login")
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, login_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    tokens = create_tokens(user.id)
    
    return success_response(
        message="登录成功",
        data=LoginResponse(
            user=UserResponse.model_validate(user),
            token=TokenData(**tokens)
        )
    )


@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await verify_refresh_token(request.refresh_token, db)
    tokens = create_tokens(user.id)
    
    return success_response(
        message="Token刷新成功",
        data=TokenData(**tokens)
    )


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(
        message="获取用户信息成功",
        data=UserResponse.model_validate(user)
    )


@router.put("/{user_id}/role")
async def change_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(allow_admin)
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    updated_user = await update_user_role(db, user, role_data.role.value)
    return success_response(
        message="修改用户角色成功",
        data=UserResponse.model_validate(updated_user)
    )
