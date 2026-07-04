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
├── cache/              # 缓存模块
├── config/             # 配置文件
├── crud/               # 数据库操作层
├── models/             # SQLAlchemy 模型
├── routers/            # API 路由
├── schemas/            # Pydantic 数据模型
├── utils/              # 工具函数
├── migrations/         # 数据库迁移脚本
├── main.py             # 应用入口
├── pyproject.toml      # 项目配置
├── .env                # 环境变量
└── app_db.sql          # 数据库初始化脚本
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
