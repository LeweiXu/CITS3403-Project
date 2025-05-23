"""Add comment column to Entries table

Revision ID: 7fd7fc347bc5
Revises: b876127cee6d
Create Date: 2025-04-24 14:24:40.940401

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fd7fc347bc5'
down_revision = 'b876127cee6d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Entries', schema=None) as batch_op:
        batch_op.add_column(sa.Column('comment', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Entries', schema=None) as batch_op:
        batch_op.drop_column('comment')

    # ### end Alembic commands ###
