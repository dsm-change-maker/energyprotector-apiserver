"""empty message

Revision ID: bcc679dabb3a
Revises: 176bda910bd4
Create Date: 2021-02-18 01:29:37.511408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcc679dabb3a'
down_revision = '176bda910bd4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('raspberry', sa.Column('start_date', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('raspberry', 'start_date')
    # ### end Alembic commands ###
