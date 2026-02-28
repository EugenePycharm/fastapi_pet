"""Make user_id nullable in chats table

Revision ID: 002_make_user_id_nullable
Revises: 001_initial_schema
Create Date: 2026-03-01 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '002_make_user_id_nullable'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Делает user_id nullable в таблице chats."""
    op.alter_column('chats', 'user_id', nullable=True)


def downgrade() -> None:
    """Возвращает NOT NULL на user_id."""
    # Сначала удалим чаты без пользователя
    op.execute("DELETE FROM chats WHERE user_id IS NULL")
    op.alter_column('chats', 'user_id', nullable=False)
