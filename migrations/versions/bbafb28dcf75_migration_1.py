"""Added Activities table

Revision ID: bbafb28dcf75
Revises: 6e9df555cbcd
Create Date: 2025-04-23 15:53:34.887422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbafb28dcf75'
down_revision = '6e9df555cbcd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('current_activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_entry_id', sa.Integer(), nullable=False),
    sa.Column('end_entry_id', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('current_activities')