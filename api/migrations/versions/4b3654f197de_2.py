"""2

Revision ID: 4b3654f197de
Revises: 2a917ca528e1
Create Date: 2023-09-12 21:54:58.070360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b3654f197de'
down_revision: Union[str, None] = '2a917ca528e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('taskmeta', 'from_task',
               existing_type=sa.INTEGER(),
               nullable=False,
               schema='ocm')
    op.drop_constraint('taskmeta_from_task_fkey', 'taskmeta', schema='ocm', type_='foreignkey')
    op.create_foreign_key(None, 'taskmeta', 'celery_taskmeta', ['from_task'], ['id'], source_schema='ocm', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'taskmeta', schema='ocm', type_='foreignkey')
    op.create_foreign_key('taskmeta_from_task_fkey', 'taskmeta', 'celery_taskmeta', ['from_task'], ['id'], source_schema='ocm')
    op.alter_column('taskmeta', 'from_task',
               existing_type=sa.INTEGER(),
               nullable=True,
               schema='ocm')
    # ### end Alembic commands ###