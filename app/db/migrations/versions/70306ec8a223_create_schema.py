"""create schema

Revision ID: 70306ec8a223
Revises: 
Create Date: 2021-12-18 03:09:13.922667

"""
from alembic import op
import sqlalchemy as sa


revision = '70306ec8a223'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA jbook;')


def downgrade() -> None:
    op.execute('DROP SCHEMA jbook;')
