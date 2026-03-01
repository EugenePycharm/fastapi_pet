"""add user_settings table

Revision ID: 20260301_120000_005
Revises: 004_make_user_id_not_null
Create Date: 2026-03-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260301_120000_005'
down_revision: Union[str, None] = '004_make_user_id_not_null'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаём таблицу user_settings
    op.create_table(
        'user_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('api_key', sa.Text(), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=False, default='gemini-2.5-flash-lite'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Создаём индексы
    op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'], unique=False)
    op.create_index('ix_user_settings_model', 'user_settings', ['model'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_user_settings_model', table_name='user_settings')
    op.drop_index('ix_user_settings_user_id', table_name='user_settings')
    op.drop_table('user_settings')
