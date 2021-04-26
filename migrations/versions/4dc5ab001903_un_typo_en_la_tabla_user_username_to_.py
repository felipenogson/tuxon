"""un typo en la tabla user (username to name)

Revision ID: 4dc5ab001903
Revises: f83a19af41fb
Create Date: 2021-03-28 06:21:38.288410

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4dc5ab001903'
down_revision = 'f83a19af41fb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('name', sa.String(length=64), nullable=True))
    op.drop_index('ix_user_username', table_name='user')
    op.create_index(op.f('ix_user_name'), 'user', ['name'], unique=True)
    op.drop_column('user', 'username')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('username', mysql.VARCHAR(length=64), nullable=True))
    op.drop_index(op.f('ix_user_name'), table_name='user')
    op.create_index('ix_user_username', 'user', ['username'], unique=True)
    op.drop_column('user', 'name')
    # ### end Alembic commands ###
