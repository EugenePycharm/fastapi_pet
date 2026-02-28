"""Make user_id NOT NULL in chats table

Revision ID: 004_make_user_id_not_null
Revises: 003_change_role_to_string
Create Date: 2026-03-01 03:20:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '004_make_user_id_not_null'
down_revision: Union[str, None] = '003_change_role_to_string'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Делает user_id NOT NULL в таблице chats."""
    # Удаляем чаты без пользователя (если есть)
    op.execute("DELETE FROM chats WHERE user_id IS NULL")
    op.alter_column('chats', 'user_id', nullable=False)


def downgrade() -> None:
    """Возвращает NULLABLE на user_id."""
    op.alter_column('chats', 'user_id', nullable=True)
