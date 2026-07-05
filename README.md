# FastAPI Scaffold

一个基于 FastAPI 的项目脚手架，集成了 SQLAlchemy、Redis、JWT 认证等功能。

## 技术栈

- **Python**: 3.13+
- **Web 框架**: FastAPI
- **ORM**: SQLAlchemy (异步)
- **数据库**: MySQL
- **缓存**: Redis
- **认证**: JWT (PyJWT)
- **包管理**: uv

## 前置要求

- Python 3.13 或更高版本
- MySQL 8.0+
- Redis
- [uv](https://docs.astral.sh/uv/) 包管理工具

## 快速启动

### 1. 安装 uv

如果尚未安装 uv，请参考 [官方文档](https://docs.astral.sh/uv/getting-started/installation/) 进行安装。

### 2. 安装依赖

```bash
uv sync
```

### 3. 配置环境变量

复制 `.env` 文件并根据实际情况修改配置：

```bash
# .env 文件已存在，主要配置项如下：
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=app_db

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=123456

# JWT 配置
JWT_SECRET_KEY=fastapiapp-dev
JWT_ALGORITHM=HS256
```

### 4. 初始化数据库

在 MySQL 中创建数据库并导入初始数据：

```bash
mysql -u root -p < app_db.sql
```

或者手动执行 `app_db.sql` 文件中的 SQL 语句。

## 数据库迁移（Alembic）

项目使用 [Alembic](https://alembic.sqlalchemy.org/) 管理数据库表结构的变更。

### 安装与初始化

```bash
# 1. 安装 Alembic
uv add alembic

# 2. 初始化目录结构
alembic init alembic
```

### 修改 `alembic/env.py`

将自动生成的文件替换为以下内容（适配 async SQLAlchemy + aiomysql）：

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── 导入模型 ──
from models import Base

target_metadata = Base.metadata

# ── 复用项目数据库配置 ──
from config.db_conf import ASYNC_DATABASE_URL

config.set_main_option("sqlalchemy.url", ASYNC_DATABASE_URL)


def run_migrations_offline() -> None:
    """离线模式：只生成 SQL 脚本，不连接数据库"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """在线模式：使用 async engine 执行迁移"""
    configuration = config.get_section(config.config_ini_section, {})
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 修改 `alembic.ini`

注释或删除 `sqlalchemy.url` 行（已在 `env.py` 中动态设置）：

```ini
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

### 确保导出所有模型

修改 `models/__init__.py`，确保所有模型类都被导入，否则 Alembic 无法自动发现：

```python
from .user import Base, User
from .article import Article

__all__ = ["Base", "User", "Article"]
```

### 日常使用

```bash
# 1. 修改 ORM 模型（models/*.py）

# 2. 自动生成迁移脚本
alembic revision --autogenerate -m "add user avatar field"

# 3. 检查生成的脚本（在 alembic/versions/ 目录下）

# 4. 应用到数据库
alembic upgrade head

# 5. 查看当前版本
alembic current

# 6. 查看迁移历史
alembic history

# 7. 回滚
alembic downgrade -1              # 回退一步
alembic downgrade <revision_id>   # 回退到指定版本

# 8. 仅查看 SQL（不下发）
alembic upgrade head --sql
```

### 多电脑同步

```bash
git pull                    # 拉取最新代码（包含新的迁移脚本）
alembic upgrade head        # 自动执行所有未应用的迁移
```

### 离线模式（生成纯 SQL 文件）

适合 DBA 审核或无法直连数据库的场景：

```bash
alembic upgrade head --sql > migration.sql
```

### 5. 启动服务

> **Windows 用户注意**: 由于 uv 在 Windows 上的兼容性问题，建议使用虚拟环境的 Python 直接运行。

**PowerShell:**
```powershell
# 设置 UTF-8 编码（Windows 必需）
$env:PYTHONIOENCODING="utf-8"

# 启动开发服务器
.\.venv\Scripts\python.exe -m fastapi dev main.py
```

**Git Bash / MSYS2:**
```bash
# 设置 UTF-8 编码
export PYTHONIOENCODING=utf-8

# 启动开发服务器
./.venv/Scripts/python.exe -m fastapi dev main.py
```

服务默认运行在 `http://127.0.0.1:8000`

### 6. 访问 API 文档

启动后可以通过以下地址访问自动生成的 API 文档：

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## 项目结构

```
fastapi-init/
├── cache/                        # 缓存抽象层
│   └── base_cache.py             #   带前缀的Redis缓存基类
├── config/                       # 配置层
│   ├── __init__.py               #   统一导出
│   ├── db_conf.py                #   数据库引擎/会话工厂
│   ├── cache_config.py           #   Redis客户端配置
│   └── jwt_config.py             #   JWT参数配置
├── crud/                         # 数据库操作层
│   ├── __init__.py               #   统一导出
│   ├── user.py                   #   用户CRUD（查询/创建/改角色）
│   └── article.py                #   文章CRUD（含分页）
├── models/                       # ORM模型层
│   ├── __init__.py               #   统一导出
│   ├── user.py                   #   User模型 + Base基类 + UserRole枚举
│   └── article.py                #   Article模型（关联User）
├── routers/                      # API路由层
│   ├── __init__.py               #   统一导出
│   ├── health.py                 #   GET /health 健康检查
│   ├── user.py                   #   /api/users 注册/登录/刷新token等
│   └── article.py                #   /api/articles 文章CRUD
├── schemas/                      # Pydantic序列化层
│   ├── __init__.py               #   统一导出
│   ├── user.py                   #   用户请求/响应模型
│   └── article.py                #   文章请求/响应模型
├── utils/                        # 工具层
│   ├── __init__.py               #   统一导出
│   ├── response.py               #   统一JSON响应格式
│   ├── security.py               #   bcrypt密码哈希
│   ├── auth.py                   #   JWT令牌创建/解码
│   ├── permissions.py            #   角色权限检查
│   ├── exception.py              #   异常处理映射
│   └── exception_handlers.py     #   异常处理器注册
├── alembic/                       # Alembic 迁移配置
│   ├── env.py                     #   迁移环境配置
│   ├── script.py.mako             #   迁移脚本模板
│   └── versions/                  #   生成的迁移脚本
├── alembic.ini                    # Alembic 配置文件
├── migrations/                   # 手动 SQL 迁移脚本（旧）
├── .env                          # 开发环境变量
├── .env.test                     # 测试环境变量
├── .env.pre                      # 预发布环境变量
├── .env.production               # 生产环境变量
├── .python-version               # Python版本锁定（3.13）
├── .gitignore
├── pyproject.toml                # 项目依赖配置
├── app_db.sql                    # 数据库初始化脚本
├── uv.lock                       # 依赖版本锁定
├── README.md                     # 说明文档
└── main.py                       # 应用入口
```

## 默认账号

项目包含两个默认测试账号：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| xiaoming | 需要自行设置 | admin |
| xiaoming2 | 需要自行设置 | author |

> 注意：密码已在数据库中加密存储，请根据实际业务需求创建新用户。

## 多环境配置

项目支持以下环境配置：

| 环境 | 配置文件 | 说明 |
|------|----------|------|
| development | `.env` | 开发环境（默认） |
| test | `.env.test` | 测试环境 |
| pre | `.env.pre` | 预发布环境 |
| production | `.env.production` | 生产环境 |

### 切换环境

通过设置 `APP_ENV` 环境变量来指定使用哪个配置文件：

**PowerShell:**
```powershell
# 开发环境（默认）
$env:APP_ENV="development"; .\.venv\Scripts\python.exe -m fastapi dev main.py

# 测试环境
$env:APP_ENV="test"; .\.venv\Scripts\python.exe -m fastapi dev main.py

# 预发布环境
$env:APP_ENV="pre"; .\.venv\Scripts\python.exe -m fastapi dev main.py

# 生产环境
$env:APP_ENV="production"; .\.venv\Scripts\python.exe -m fastapi run main.py
```

**Git Bash / MSYS2:**
```bash
# 开发环境（默认）
APP_ENV=development ./.venv/Scripts/python.exe -m fastapi dev main.py

# 测试环境
APP_ENV=test ./.venv/Scripts/python.exe -m fastapi  main.py

# 预发布环境
APP_ENV=pre ./.venv/Scripts/python.exe -m fastapi  main.py

# 生产环境
APP_ENV=production ./.venv/Scripts/python.exe -m fastapi run main.py
```

**Linux/Mac:**
```bash
# 测试环境
APP_ENV=test uv run fastapi dev main.py

# 预发布环境
APP_ENV=pre uv run fastapi dev main.py

# 生产环境
APP_ENV=production uv run fastapi run main.py
```

## 开发

### 运行开发服务器（自动重载）

**PowerShell:**
```powershell
$env:PYTHONIOENCODING="utf-8"; .\.venv\Scripts\python.exe -m fastapi dev main.py
```

**Git Bash:**
```bash
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe -m fastapi dev main.py
```

**Linux/Mac:**
```bash
uv run fastapi dev main.py
```

### 运行生产服务器

**PowerShell:**
```powershell
$env:PYTHONIOENCODING="utf-8"; .\.venv\Scripts\python.exe -m fastapi run main.py
```

**Git Bash:**
```bash
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe -m fastapi run main.py
```

**Linux/Mac:**
```bash
uv run fastapi run main.py
```
