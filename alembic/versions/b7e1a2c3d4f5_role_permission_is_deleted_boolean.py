"""role/permission is_deleted Integer -> Boolean

Revision ID: b7e1a2c3d4f5
Revises: 782f2e8edc1b
Create Date: 2026-10-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7e1a2c3d4f5'
down_revision: Union[str, Sequence[str], None] = '782f2e8edc1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'role', 'is_deleted',
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        existing_nullable=False,
        existing_server_default=sa.text('0'),
    )
    op.alter_column(
        'permission', 'is_deleted',
        existing_type=sa.Integer(),
        type_=sa.Boolean(),
        existing_nullable=False,
        existing_server_default=sa.text('0'),
    )


def downgrade() -> None:
    op.alter_column(
        'role', 'is_deleted',
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        existing_nullable=False,
        existing_server_default=sa.text('0'),
    )
    op.alter_column(
        'permission', 'is_deleted',
        existing_type=sa.Boolean(),
        type_=sa.Integer(),
        existing_nullable=False,
        existing_server_default=sa.text('0'),
    )
