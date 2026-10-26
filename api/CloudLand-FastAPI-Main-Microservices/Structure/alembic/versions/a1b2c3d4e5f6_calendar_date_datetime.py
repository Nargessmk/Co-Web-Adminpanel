"""convert tblCalendar.date to datetime (gregorian)

Revision ID: a1b2c3d4e5f6
Revises: 5f4a9c2d3b71
Create Date: 2026-08-02 13:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import jdatetime


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '5f4a9c2d3b71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _to_gregorian(value):
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return jdatetime.datetime.strptime(value.strip(), '%Y/%m/%d').togregorian()
        except ValueError:
            return None
    return value


def _to_persian(value):
    if value is None:
        return None
    return jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d')


def upgrade() -> None:
    op.add_column('tblCalendar', sa.Column('date_g', sa.DateTime(), nullable=True))
    bind = op.get_bind()
    rows = bind.execute(sa.text('SELECT id, date FROM tblCalendar')).fetchall()
    for rid, value in rows:
        converted = _to_gregorian(value)
        if converted is not None:
            bind.execute(
                sa.text('UPDATE tblCalendar SET date_g = :converted WHERE id = :rid'),
                {'converted': converted, 'rid': rid},
            )
    op.drop_column('tblCalendar', 'date')
    op.alter_column('tblCalendar', 'date_g', new_column_name='date', existing_type=sa.DateTime(), nullable=False)


def downgrade() -> None:
    op.add_column('tblCalendar', sa.Column('date_old', sa.String(50), nullable=True))
    bind = op.get_bind()
    rows = bind.execute(sa.text('SELECT id, date FROM tblCalendar')).fetchall()
    for rid, value in rows:
        converted = _to_persian(value)
        if converted is not None:
            bind.execute(
                sa.text('UPDATE tblCalendar SET date_old = :converted WHERE id = :rid'),
                {'converted': converted, 'rid': rid},
            )
    op.drop_column('tblCalendar', 'date')
    op.alter_column('tblCalendar', 'date_old', new_column_name='date', existing_type=sa.String(50), nullable=False)
