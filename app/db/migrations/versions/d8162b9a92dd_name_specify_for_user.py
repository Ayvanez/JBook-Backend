"""name specify for user

Revision ID: d8162b9a92dd
Revises: ad6fbc6cfebe
Create Date: 2021-12-20 20:10:27.740880

"""
from alembic import op
import sqlalchemy as sa


revision = 'd8162b9a92dd'
down_revision = 'ad6fbc6cfebe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('first_name', sa.String(length=250), nullable=True), schema='jbook')
    op.add_column('user', sa.Column('surname', sa.String(length=250), nullable=True), schema='jbook')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'surname', schema='jbook')
    op.drop_column('user', 'first_name', schema='jbook')
    # ### end Alembic commands ###
