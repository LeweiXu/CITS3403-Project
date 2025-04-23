"""initial migration

Revision ID: 6e9df555cbcd
Revises: 
Create Date: 2025-04-22 16:36:08.125260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e9df555cbcd'
down_revision = None
branch_labels = None
depends_on = None


"""initial migration

Revision ID: a68b26254119
Revises: 
Create Date: 2025-04-23 19:31:37.996779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a68b26254119'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('username'),
    sa.UniqueConstraint('email')
    )

    op.create_table('media_entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('media_type', sa.String(length=50), nullable=False),
    sa.Column('media_name', sa.String(length=120), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['username'], ['users.username'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('media_entries')
    op.drop_table('users')

