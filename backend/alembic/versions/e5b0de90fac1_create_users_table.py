"""create_users_table

Revision ID: e5b0de90fac1
Revises: 
Create Date: 2026-01-15 00:52:29.778171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e5b0de90fac1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users table."""
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # Create unique index on email for case-insensitive uniqueness
    op.create_index(
        'ix_users_email',
        'users',
        ['email'],
        unique=True
    )


def downgrade() -> None:
    """Drop users table."""
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
