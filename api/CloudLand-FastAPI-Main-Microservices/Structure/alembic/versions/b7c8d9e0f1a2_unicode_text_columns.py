"""convert text columns from varchar to nvarchar for unicode support

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-08-02 14:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    alter_specs = [
        ('tblConstant', 'title', sa.Unicode()),
        ('tblConstant', 'desc', sa.UnicodeText()),
        ('tblConstant', 'constant_value', sa.UnicodeText()),
        ('tblConstant', 'icon', sa.Unicode(100)),
        ('tblConstant', 'color', sa.Unicode(100)),
        ('tblConstant', 'json_data', sa.UnicodeText()),
        ('tblCalendar', 'title', sa.Unicode()),
        ('tblCalendar', 'desc', sa.UnicodeText()),
        ('tblCalendar', 'occasion', sa.Unicode(200)),
        ('tblCalendar', 'additional_description', sa.UnicodeText()),
        ('tblUserConstantPermission', 'title', sa.Unicode()),
        ('tblUserConstantPermission', 'desc', sa.UnicodeText()),
    ]
    for table, column, type_ in alter_specs:
        op.alter_column(table, column, existing_type=sa.Text(), type_=type_)


def downgrade() -> None:
    alter_specs = [
        ('tblConstant', 'title', sa.String()),
        ('tblConstant', 'desc', sa.Text()),
        ('tblConstant', 'constant_value', sa.Text()),
        ('tblConstant', 'icon', sa.String(100)),
        ('tblConstant', 'color', sa.String(100)),
        ('tblConstant', 'json_data', sa.Text()),
        ('tblCalendar', 'title', sa.String()),
        ('tblCalendar', 'desc', sa.Text()),
        ('tblCalendar', 'occasion', sa.String(200)),
        ('tblCalendar', 'additional_description', sa.Text()),
        ('tblUserConstantPermission', 'title', sa.String()),
        ('tblUserConstantPermission', 'desc', sa.Text()),
    ]
    for table, column, type_ in alter_specs:
        op.alter_column(table, column, existing_type=sa.UnicodeText(), type_=type_)
