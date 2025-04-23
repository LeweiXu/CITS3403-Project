"""moved username FK to Activities table, standardized names

Revision ID: a68b26254119
Revises: bbafb28dcf75
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
    op.create_table('Users',
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('username'),
    sa.UniqueConstraint('email')
    )
    op.create_table('Activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('start_entry_id', sa.Integer(), nullable=False),
    sa.Column('end_entry_id', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['username'], ['Users.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('activity_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('media_type', sa.String(length=50), nullable=False),
    sa.Column('media_name', sa.String(length=120), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['activity_id'], ['Activities.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('media_entries')
    op.drop_table('users')
    op.drop_table('current_activities')


def downgrade():
    op.drop_table('Entries')
    op.drop_table('Users')
    op.drop_table('Activities')

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
    op.create_table('current_activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_entry_id', sa.Integer(), nullable=False),
    sa.Column('end_entry_id', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['username'], ['Users.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
