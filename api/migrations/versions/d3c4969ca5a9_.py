"""empty message

Revision ID: d3c4969ca5a9
Revises: 4b3654f197de
Create Date: 2023-09-12 22:04:28.996585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3c4969ca5a9'
down_revision: Union[str, None] = '4b3654f197de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('taskmeta', sa.Column('from_task_id', sa.String(length=155), nullable=False), schema='ocm')
    op.drop_constraint('taskmeta_from_task_fkey', 'taskmeta', schema='ocm', type_='foreignkey')
    op.create_foreign_key(None, 'taskmeta', 'celery_taskmeta', ['from_task_id'], ['task_id'], source_schema='ocm', ondelete='CASCADE')
    op.drop_column('taskmeta', 'from_task', schema='ocm')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('taskmeta', sa.Column('from_task', sa.INTEGER(), autoincrement=False, nullable=False), schema='ocm')
    op.drop_constraint(None, 'taskmeta', schema='ocm', type_='foreignkey')
    op.create_foreign_key('taskmeta_from_task_fkey', 'taskmeta', 'celery_taskmeta', ['from_task'], ['id'], source_schema='ocm', ondelete='CASCADE')
    op.drop_column('taskmeta', 'from_task_id', schema='ocm')
    # ### end Alembic commands ###
