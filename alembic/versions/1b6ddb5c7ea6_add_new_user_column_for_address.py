"""Add new user column for address

Revision ID: 1b6ddb5c7ea6
Revises: b5d6b25cf2f4
Create Date: 2022-06-24 12:16:59.571078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b6ddb5c7ea6'
down_revision = 'b5d6b25cf2f4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('address_id', sa.Integer(), nullable=True))
    op.create_foreign_key('address_users_fk', source_table='users', referent_table='address',
                          local_cols=['address_id'], remote_cols=['id'], ondelete='CASCADE')


def downgrade():
    op.drop_constraint('address_users_fk', table_name='users')
    op.drop_column('users', 'address_id')
