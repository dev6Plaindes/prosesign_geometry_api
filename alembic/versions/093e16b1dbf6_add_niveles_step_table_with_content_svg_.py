"""add niveles_step table with content_svg column

Revision ID: 093e16b1dbf6
Revises: c879890cb64a
Create Date: 2026-07-11 18:19:05.167404

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '093e16b1dbf6'
down_revision: Union[str, Sequence[str], None] = 'c879890cb64a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'niveles_step',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('content_step', sa.JSON(), nullable=True),
        sa.Column('id_project', sa.Integer(), nullable=False),
        sa.Column('nivel', sa.Integer(), nullable=False),
        sa.Column('content_svg', mysql.LONGTEXT(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['id_project'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('ix_niveles_step_id_project', 'niveles_step', ['id_project'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_niveles_step_id_project', table_name='niveles_step')
    op.drop_table('niveles_step')