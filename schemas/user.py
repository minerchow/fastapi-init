from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from utils.enums import UserRole


class BaseResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


class UserBase(BaseModel):
    username: str = Field(..., max_length=50, description="用户名")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="密码")


class UserResponse(UserBase):
    id: int
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str = "user"

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str = Field(..., max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginResponse(BaseModel):
    user: UserResponse
    token: TokenData


class UserRoleUpdate(BaseModel):
    role: UserRole = Field(..., description="用户角色")
