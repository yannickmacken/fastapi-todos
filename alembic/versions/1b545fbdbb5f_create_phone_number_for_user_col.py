"""create phone number for user col

Revision ID: 1b545fbdbb5f
Revises: 
Create Date: 2022-05-27 09:00:33.739376

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b545fbdbb5f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'phone_number')
