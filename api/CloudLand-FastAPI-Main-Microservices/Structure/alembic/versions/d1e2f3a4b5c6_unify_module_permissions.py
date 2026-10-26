"""unify module permissions into tblUserConstantPermission and drop tblAppModulePermission

Revision ID: d1e2f3a4b5c6
Revises: c9d0e1f2a3b4
Create Date: 2026-08-25 09:16:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, None] = 'a23e81e56a9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add module_key and action_key columns to tblUserConstantPermission if they do not exist
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns 
            WHERE object_id = OBJECT_ID('tblUserConstantPermission') 
              AND name = 'module_key'
        )
        BEGIN
            ALTER TABLE tblUserConstantPermission ADD module_key NVARCHAR(100) NULL;
        END
        """
    )

    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.columns 
            WHERE object_id = OBJECT_ID('tblUserConstantPermission') 
              AND name = 'action_key'
        )
        BEGIN
            ALTER TABLE tblUserConstantPermission ADD action_key NVARCHAR(100) NULL;
        END
        """
    )

    # 2. Add indices on module_key and action_key
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes 
            WHERE name = 'ix_tblUserConstantPermission_module_key' 
              AND object_id = OBJECT_ID('tblUserConstantPermission')
        )
        BEGIN
            CREATE INDEX ix_tblUserConstantPermission_module_key 
            ON tblUserConstantPermission (module_key);
        END
        """
    )

    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes 
            WHERE name = 'ix_tblUserConstantPermission_action_key' 
              AND object_id = OBJECT_ID('tblUserConstantPermission')
        )
        BEGIN
            CREATE INDEX ix_tblUserConstantPermission_action_key 
            ON tblUserConstantPermission (action_key);
        END
        """
    )

    # 3. Migrate any existing records from tblAppModulePermission to tblUserConstantPermission
    op.execute(
        """
        IF EXISTS (
            SELECT 1 FROM sys.objects 
            WHERE name = 'tblAppModulePermission' 
              AND type = 'U'
        )
        BEGIN
            INSERT INTO tblUserConstantPermission (
                id, application_id, role_id, user_id, group_id, constant_id,
                module_key, action_key, has_permission,
                create_at, last_modified_at, user_created, last_modified_user,
                title, [desc], allow_delete, allow_update, disabled, hidden, version
            )
            SELECT 
                NEWID(), m.application_id, m.role_id, m.user_id, NULL, NULL,
                m.module_key, m.action_key, m.has_permission,
                m.create_at, m.last_modified_at, m.user_created, m.last_modified_user,
                ISNULL(m.title, N''), m.[desc], m.allow_delete, m.allow_update, m.disabled, m.hidden, ISNULL(m.version, 1)
            FROM tblAppModulePermission m
            WHERE NOT EXISTS (
                SELECT 1 FROM tblUserConstantPermission c
                WHERE c.application_id = m.application_id
                  AND ISNULL(c.role_id, '00000000-0000-0000-0000-000000000000') = ISNULL(m.role_id, '00000000-0000-0000-0000-000000000000')
                  AND ISNULL(c.user_id, '00000000-0000-0000-0000-000000000000') = ISNULL(m.user_id, '00000000-0000-0000-0000-000000000000')
                  AND c.module_key = m.module_key
                  AND c.action_key = m.action_key
            );

            DROP TABLE tblAppModulePermission;
        END
        """
    )


def downgrade() -> None:
    # 1. Re-create tblAppModulePermission if needed
    op.execute(
        """
        IF NOT EXISTS (
            SELECT 1 FROM sys.objects 
            WHERE name = 'tblAppModulePermission' 
              AND type = 'U'
        )
        BEGIN
            CREATE TABLE tblAppModulePermission (
                id UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
                application_id UNIQUEIDENTIFIER NOT NULL,
                role_id UNIQUEIDENTIFIER NULL,
                user_id UNIQUEIDENTIFIER NULL,
                module_key NVARCHAR(100) NOT NULL,
                action_key NVARCHAR(100) NOT NULL,
                has_permission BIT NOT NULL DEFAULT 1,
                create_at DATETIMEOFFSET NOT NULL,
                last_modified_at DATETIMEOFFSET NOT NULL,
                user_created UNIQUEIDENTIFIER NOT NULL,
                last_modified_user UNIQUEIDENTIFIER NOT NULL,
                title NVARCHAR(MAX) NULL,
                [desc] NVARCHAR(MAX) NULL,
                allow_delete BIT NOT NULL DEFAULT 0,
                allow_update BIT NOT NULL DEFAULT 1,
                disabled BIT NOT NULL DEFAULT 0,
                hidden BIT NOT NULL DEFAULT 0,
                version INT NOT NULL DEFAULT 1
            );
        END
        """
    )
