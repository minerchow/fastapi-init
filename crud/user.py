from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from schemas.user import UserCreate
from utils.security import get_hash_password


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    query = select(User).where(User.username == username, User.is_deleted == False)
    result = await db.execute(query)
    return result.scalars().one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    query = select(User).where(User.id == user_id, User.is_deleted == False)
    result = await db.execute(query)
    return result.scalars().one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    hashed_password = get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_role(db: AsyncSession, user: User, role: str) -> User:
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user


async def soft_delete_user(db: AsyncSession, user: User) -> User:
    user.is_deleted = True
    await db.commit()
    await db.refresh(user)
    return user
