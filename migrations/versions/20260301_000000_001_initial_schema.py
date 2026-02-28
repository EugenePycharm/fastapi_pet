"""Initial schema - create users, sessions, chats, messages tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-03-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создание всех таблиц базы данных."""
    
    # === Таблица users ===
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, comment='Уникальный email пользователя'),
        sa.Column('hashed_password', sa.Text(), nullable=False, comment='Хеш пароля'),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False, comment='Статус активности пользователя'),
        sa.Column('is_superuser', sa.Boolean(), server_default='false', nullable=False, comment='Флаг администратора'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    op.create_index('ix_users_is_active', 'users', ['is_active'], unique=False)
    op.create_index('ix_users_email_active', 'users', ['email', 'is_active'], unique=False)
    op.create_index('ix_users_created_at', 'users', ['created_at'], unique=False)
    
    # === Таблица sessions ===
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID пользователя'),
        sa.Column('refresh_token', sa.Text(), nullable=False, comment='Хеш refresh токена'),
        sa.Column('user_agent', sa.String(512), nullable=True, comment='User-Agent клиента'),
        sa.Column('ip_address', sa.String(45), nullable=True, comment='IP адрес клиента'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False, comment='Дата истечения сессии'),
        sa.Column('is_revoked', sa.Boolean(), server_default='false', nullable=False, comment='Флаг отзыва сессии'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('refresh_token'),
    )
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'], unique=False)
    op.create_index('ix_sessions_refresh_token', 'sessions', ['refresh_token'], unique=False)
    op.create_index('ix_sessions_expires_at', 'sessions', ['expires_at'], unique=False)
    op.create_index('ix_sessions_is_revoked', 'sessions', ['is_revoked'], unique=False)
    op.create_index('ix_sessions_user_expires', 'sessions', ['user_id', 'expires_at'], unique=False)
    op.create_index('ix_sessions_active', 'sessions', ['user_id', 'is_revoked', 'expires_at'], unique=False)
    
    # === Таблица chats ===
    op.create_table(
        'chats',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID владельца чата'),
        sa.Column('title', sa.String(255), nullable=False, comment='Название чата'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_chats_user_id', 'chats', ['user_id'], unique=False)
    op.create_index('ix_chats_user_created', 'chats', ['user_id', 'created_at'], unique=False)
    op.create_index('ix_chats_title', 'chats', ['title'], unique=False)
    
    # === Таблица messages ===
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.func.gen_random_uuid(), nullable=False),
        sa.Column('chat_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID чата'),
        sa.Column('role', sa.Enum('user', 'assistant', 'system', name='messagerole'), nullable=False, comment='Роль отправителя'),
        sa.Column('content', sa.Text(), nullable=False, comment='Текст сообщения'),
        sa.Column('token_count', sa.Integer(), nullable=True, comment='Количество токенов'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_messages_chat_id', 'messages', ['chat_id'], unique=False)
    op.create_index('ix_messages_role', 'messages', ['role'], unique=False)
    op.create_index('ix_messages_chat_created', 'messages', ['chat_id', 'created_at'], unique=False)
    op.create_index('ix_messages_chat_role', 'messages', ['chat_id', 'role'], unique=False)


def downgrade() -> None:
    """Откат миграции - удаление всех таблиц."""
    # Удаляем таблицы в порядке, обратном созданию (с учётом FK)
    op.drop_table('messages')
    op.drop_table('chats')
    op.drop_table('sessions')
    op.drop_table('users')
    
    # Удаляем enum type
    op.execute('DROP TYPE IF EXISTS messagerole')
