"""add application_id for multi-tenant isolation

Revision ID: 5f4a9c2d3b71
Revises: 92e16c6de1ec
Create Date: 2026-08-01 10:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5f4a9c2d3b71'
down_revision: Union[str, None] = '92e16c6de1ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in ('tblConstant', 'tblCalendar', 'tblUserConstantPermission'):
        op.add_column(table, sa.Column('application_id', sa.Uuid(), nullable=True))


def downgrade() -> None:
    for table in ('tblConstant', 'tblCalendar', 'tblUserConstantPermission'):
        op.drop_column(table, 'application_id')
