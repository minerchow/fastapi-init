import os
import logging
from datetime import timedelta
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# 根据 APP_ENV 加载对应的 .env 文件
app_env = os.getenv("APP_ENV", "development")
env_file = f".env.{app_env}" if app_env != "development" else ".env"
load_dotenv(env_file)

ENV = os.getenv("ENV", app_env)

_PLACEHOLDER_SECRET = "default-secret-key-please-change"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
if not JWT_SECRET_KEY or JWT_SECRET_KEY == _PLACEHOLDER_SECRET:
    if ENV != "development":
        raise RuntimeError(
            "JWT_SECRET_KEY 未配置或仍为占位值，禁止在非 development 环境启动。"
            "请在 .env 中配置强随机密钥。"
        )
    logger.warning("JWT_SECRET_KEY 未配置，使用默认占位密钥（仅限开发环境）")
    JWT_SECRET_KEY = _PLACEHOLDER_SECRET

_ALLOWED_ALGORITHMS = {"HS256", "HS384", "HS512"}
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
if JWT_ALGORITHM not in _ALLOWED_ALGORITHMS:
    raise RuntimeError(f"不支持的 JWT_ALGORITHM: {JWT_ALGORITHM}，仅允许 {sorted(_ALLOWED_ALGORITHMS)}")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
