"""add_remind_snooze_func

Revision ID: f58755a6d46c
Revises: 6ea91430d962
Create Date: 2024-05-10 10:08:47.468691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f58755a6d46c'
down_revision: Union[str, None] = '6ea91430d962'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('remind_target', sa.Column('is_snooze', sa.Boolean(), nullable=True))
    op.add_column('remind_target', sa.Column('previous_remind_message_id', sa.BigInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('remind_target', 'previous_remind_message_id')
    op.drop_column('remind_target', 'is_snooze')
    # ### end Alembic commands ###
