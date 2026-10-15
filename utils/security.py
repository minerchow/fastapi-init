import anyio
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# bcrypt 是刻意设计得很慢的同步 CPU 操作（约 100ms+），
# 直接在协程里调用会阻塞整个事件循环，因此统一丢到线程池执行。
# 同步版本保留给脚本等非异步环境使用。

async def get_hash_password_async(password: str) -> str:
    return await anyio.to_thread.run_sync(get_hash_password, password)


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    return await anyio.to_thread.run_sync(verify_password, plain_password, hashed_password)
