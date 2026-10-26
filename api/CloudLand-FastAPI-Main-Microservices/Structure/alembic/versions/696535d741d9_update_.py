"""update GetConstantsRecursiveWithPermissions logic

Revision ID: 696535d741d9
Revises: d1e2f3a4b5c6
Create Date: 2026-08-25 11:30:20.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '696535d741d9'
down_revision: Union[str, None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    context = op.get_context()
    if context.dialect.name == "mssql":
        import os
        sql_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', 'functions.sql')
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        import re
        match = re.search(r'CREATE OR ALTER FUNCTION dbo\.GetConstantsRecursiveWithPermissions.*?SELECT\n\s+h\.Id', sql_content, re.IGNORECASE | re.DOTALL)
        if match:
            func_sql = match.group(0)
            func_sql = func_sql[:func_sql.rfind('SELECT\n')]
            op.execute(text(func_sql))
        else:
            raise Exception("Function not found in functions.sql")


def downgrade() -> None:
    pass
