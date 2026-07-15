"""add missing columns: content_pdf to projects, content_svg to niveles_step, rectangle columns

Revision ID: 3ff1a4efff9d
Revises: 093e16b1dbf6
Create Date: 2026-07-11 18:23:55.603297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '3ff1a4efff9d'
down_revision: Union[str, Sequence[str], None] = '093e16b1dbf6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add content_pdf column to projects (MEDIUMBLOB for PDF binary storage)
    op.add_column('projects', sa.Column('content_pdf', sa.LargeBinary(), nullable=True))
    
    # Add content_svg column to niveles_step (LONGTEXT for SVG content)
    op.add_column('niveles_step', sa.Column('content_svg', mysql.LONGTEXT(), nullable=True))
    
    # Add rectangle columns to projects (for max rectangle feature)
    op.add_column('projects', sa.Column('vertices_rectangle', sa.JSON(), nullable=True))
    op.add_column('projects', sa.Column('angle', sa.Float(), nullable=True))
    op.add_column('projects', sa.Column('excluded_vertices', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('projects', 'content_pdf')
    op.drop_column('niveles_step', 'content_svg')
    op.drop_column('projects', 'vertices_rectangle')
    op.drop_column('projects', 'angle')
    op.drop_column('projects', 'excluded_vertices')