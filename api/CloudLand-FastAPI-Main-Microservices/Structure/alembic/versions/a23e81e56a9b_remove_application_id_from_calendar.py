"""remove_application_id_from_calendar

Revision ID: a23e81e56a9b
Revises: c9d0e1f2a3b4
Create Date: 2026-08-18 10:41:15.629216
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = 'a23e81e56a9b'
down_revision: Union[str, None] = 'c9d0e1f2a3b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tblCalendar") as batch_op:
        conn = op.get_bind()
        result = conn.execute(text(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tblCalendar' AND COLUMN_NAME = 'application_id'"
        ))
        if result.fetchone():
            batch_op.drop_column("application_id")


def downgrade() -> None:
    with op.batch_alter_table("tblCalendar") as batch_op:
        conn = op.get_bind()
        result = conn.execute(text(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'tblCalendar' AND COLUMN_NAME = 'application_id'"
        ))
        if not result.fetchone():
            batch_op.add_column(sa.Column("application_id", sa.Uuid(), nullable=True))
