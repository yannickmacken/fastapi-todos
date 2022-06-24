"""Add apt number column to address table.

Revision ID: 52164174362c
Revises: 1b6ddb5c7ea6
Create Date: 2022-06-24 12:59:47.464624

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52164174362c'
down_revision = '1b6ddb5c7ea6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('address', sa.Column('apt_num', sa.String(), nullable=True))


def downgrade():
    op.drop_column('address', 'apt_num')
