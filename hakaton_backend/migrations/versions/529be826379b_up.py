"""Up

Revision ID: 529be826379b
Revises: 585467d58724
Create Date: 2022-10-09 06:27:21.180782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '529be826379b'
down_revision = '585467d58724'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('target', sa.Enum('Any', 'TeamsOnly', 'Individual', name='targettaskenum'), nullable=True))
    op.add_column('task', sa.Column('author_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('task', 'author_id')
    op.drop_column('task', 'target')
    # ### end Alembic commands ###