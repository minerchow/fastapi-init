"""add_menu_table

Revision ID: d3a9f6c1b842
Revises: b7e1a2c3d4f5
Create Date: 2026-10-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd3a9f6c1b842'
down_revision: Union[str, Sequence[str], None] = 'b7e1a2c3d4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建菜单表。

    刻意手写而非 autogenerate：782f2e8edc1b 证明 autogenerate 会在关联表上生成
    ForeignKeyConstraint（本仓库禁止 DB 级外键），还会把 is_deleted 建成 Integer。

    - parent_id / permission_id 是普通 Integer + 索引，不建外键约束；引用完整性
      由 crud/menu.py 的显式校验（上级菜单不存在 / 以下权限不存在）负责。
    - path 不建唯一约束：软删除会让「删除后重建同一路径」撞库，唯一性由路由层
      过滤 is_deleted == False 的预查询保证。
    - 时间戳与布尔列都不写 server_default，与 models/base.py + models/menu.py 的
      Python 侧默认保持一致（数据只经 ORM 写入）。
    """
    op.create_table(
        'menu',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('path', sa.String(length=100), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_visible', sa.Boolean(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_menu_parent_id'), 'menu', ['parent_id'], unique=False)
    op.create_index(op.f('ix_menu_path'), 'menu', ['path'], unique=False)
    op.create_index(op.f('ix_menu_permission_id'), 'menu', ['permission_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_menu_permission_id'), table_name='menu')
    op.drop_index(op.f('ix_menu_path'), table_name='menu')
    op.drop_index(op.f('ix_menu_parent_id'), table_name='menu')
    op.drop_table('menu')
