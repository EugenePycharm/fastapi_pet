"""Change messages.role from enum to string

Revision ID: 003_change_role_to_string
Revises: 002_make_user_id_nullable
Create Date: 2026-03-01 03:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_change_role_to_string'
down_revision: Union[str, None] = '002_make_user_id_nullable'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Изменяет тип колонки role с enum на string."""
    # Удаляем enum type (сначала нужно удалить зависимость)
    op.execute("ALTER TABLE messages ALTER COLUMN role TYPE VARCHAR(20) USING role::text")
    op.execute("DROP TYPE IF EXISTS messagerole")


def downgrade() -> None:
    """Возвращает enum type."""
    # Создаём enum type
    op.execute("CREATE TYPE messagerole AS ENUM ('user', 'assistant', 'system')")
    op.execute("ALTER TABLE messages ALTER COLUMN role TYPE messagerole USING role::messagerole")
