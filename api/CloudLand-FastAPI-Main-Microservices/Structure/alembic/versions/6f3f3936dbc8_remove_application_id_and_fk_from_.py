"""remove_application_id_and_fk_from_calendar

Revision ID: 6f3f3936dbc8
Revises: b7c8d9e0f1a2
Create Date: 2026-08-06 00:09:41.848121
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql


revision: str = '6f3f3936dbc8'
down_revision: Union[str, None] = 'b7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DECLARE @fk_name NVARCHAR(128);
        SELECT @fk_name = fk.name
        FROM sys.foreign_keys fk
        INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        WHERE fk.parent_object_id = OBJECT_ID('tblCalendar')
          AND OBJECT_NAME(fkc.referenced_object_id) = 'tblConstant';
        
        IF @fk_name IS NOT NULL
        BEGIN
            EXEC('ALTER TABLE tblCalendar DROP CONSTRAINT ' + @fk_name);
        END
        """
    )

    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.columns 
            WHERE name = 'application_id' 
              AND object_id = OBJECT_ID('tblCalendar')
        )
        BEGIN
            ALTER TABLE tblCalendar DROP COLUMN application_id;
        END
        """
    )


def downgrade() -> None:
    # Re-add application_id column to tblCalendar
    op.add_column('tblCalendar', sa.Column('application_id', mssql.UNIQUEIDENTIFIER(), nullable=True))
