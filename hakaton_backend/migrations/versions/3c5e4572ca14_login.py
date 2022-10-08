"""login

Revision ID: 3c5e4572ca14
Revises: 3ba90715b052
Create Date: 2022-10-08 14:04:37.746629

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c5e4572ca14'
down_revision = '3ba90715b052'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('date', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_task_date'), 'task', ['date'], unique=False)
    op.add_column('user', sa.Column('login', sa.String(length=120), nullable=True))
    op.create_index(op.f('ix_user_login'), 'user', ['login'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_login'), table_name='user')
    op.drop_column('user', 'login')
    op.drop_index(op.f('ix_task_date'), table_name='task')
    op.drop_column('task', 'date')
    # ### end Alembic commands ###