"""Initial migration: create chats and messages tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create chats and messages tables with indexes."""
    
    # Create chats table
    op.create_table(
        'chats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_chats_created_at', 'chats', ['created_at'])
    op.create_index(op.f('ix_chats_id'), 'chats', ['id'], unique=False)
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(length=5000), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['chat_id'],
            ['chats.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_chat_id', 'messages', ['chat_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)


def downgrade() -> None:
    """Drop messages and chats tables."""
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_index('idx_messages_created_at', table_name='messages')
    op.drop_index('idx_messages_chat_id', table_name='messages')
    op.drop_table('messages')
    
    op.drop_index(op.f('ix_chats_id'), table_name='chats')
    op.drop_index('idx_chats_created_at', table_name='chats')
    op.drop_table('chats')
