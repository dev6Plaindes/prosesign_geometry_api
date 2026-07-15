"""initial schema: projects table with all columns

Revision ID: c879890cb64a
Revises: 
Create Date: 2026-07-11 18:18:45.261244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'c879890cb64a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('zone', sa.String(length=255), nullable=True),
        sa.Column('tipologia', sa.String(length=255), nullable=True),
        sa.Column('departamento', sa.String(length=255), nullable=True),
        sa.Column('provincia', sa.String(length=255), nullable=True),
        sa.Column('distrito', sa.String(length=255), nullable=True),
        sa.Column('manager', sa.String(length=255), nullable=True),
        sa.Column('client', sa.String(length=255), nullable=True),
        sa.Column('ubication', sa.String(length=255), nullable=True),
        sa.Column('tipo', sa.String(length=255), nullable=True),
        sa.Column('vertices_terreno_utm', sa.JSON(), nullable=True),
        sa.Column('aforo', sa.JSON(), nullable=True),
        sa.Column('vertices_rectangle', sa.JSON(), nullable=True),
        sa.Column('angle', sa.Float(), nullable=True),
        sa.Column('excluded_vertices', sa.JSON(), nullable=True),
        sa.Column('number_floors', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('ambientes', sa.JSON(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_id', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('projects')