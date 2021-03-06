"""empty message

Revision ID: cef7b39da1c9
Revises: 8b1f67e48125
Create Date: 2022-05-29 16:31:17.977729

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cef7b39da1c9'
down_revision = '8b1f67e48125'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_login', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_login')
    # ### end Alembic commands ###
