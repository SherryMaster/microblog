"""add profile fields

Revision ID: 9b7d9e5f2a31
Revises: a04efc1a59ab
Create Date: 2026-09-11

"""
from alembic import op
import sqlalchemy as sa


revision = '9b7d9e5f2a31'
down_revision = 'a04efc1a59ab'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('about_me', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_seen')
        batch_op.drop_column('about_me')
