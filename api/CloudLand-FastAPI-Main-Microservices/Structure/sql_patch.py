import re

with open('/home/victus/Projects/Bussiness-Management/Back-End/Structure/sql/functions.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

replacement = """WITH UserLockState AS (
    SELECT CASE WHEN EXISTS (
        SELECT 1 FROM tblUserConstantPermission WHERE user_id = @UserId AND (@ApplicationId IS NULL OR application_id = @ApplicationId)
    ) THEN 1 ELSE 0 END AS IsLocked
),
AllPermissionedNodes AS (
    SELECT
        c.id AS Id,
        c.parent_id AS ParentId,
        c.create_at AS CreateAt,
        c.last_modified_at AS LastModifiedAt,
        c.user_created AS UserCreated,
        c.last_modified_user AS LastModifiedUser,
        c.application_id AS ApplicationId,
        c.title AS title,
        c.priority AS Priority,
        c.allow_delete AS AllowDelete,
        c.allow_update AS AllowUpdate,
        c.disabled AS Disabled,
        c.hidden AS hidden,
        c.version AS Version,
        c.constant_value AS ConstantValue,
        c.valid_end_date AS ValidEndDate,
        c.valid_start_date AS ValidStartDate,
        c.value_type AS ValueType,
        c.node_type_id AS NodeTypeId,
        c.color AS Color,
        c.icon AS Icon,
        c.child_must_be_show AS ChildMustBeShow,
        CASE
            WHEN c.node_type_id = c.id THEN c.constant_value
            ELSE nt.constant_value
        END AS NodeType,
        c.[desc] AS [desc]
    FROM tblConstant c
    CROSS JOIN UserLockState uls
    OUTER APPLY (
        SELECT constant_value
        FROM tblConstant
        WHERE id = c.node_type_id AND id <> c.id
    ) nt
    WHERE EXISTS (
        SELECT 1 FROM tblUserConstantPermission up
        WHERE up.constant_id = c.id
          AND (
                (@UserId IS NOT NULL AND uls.IsLocked = 1 AND up.user_id = @UserId)
                OR (uls.IsLocked = 0 AND @RoleIds IS NOT NULL AND up.role_id IN (SELECT TRY_CAST(value AS uniqueidentifier) FROM STRING_SPLIT(@RoleIds, ',')))
                OR (uls.IsLocked = 0 AND @GroupIds IS NOT NULL AND up.group_id IN (SELECT TRY_CAST(value AS uniqueidentifier) FROM STRING_SPLIT(@GroupIds, ',')))
          )
          AND (@ApplicationId IS NULL OR up.application_id = @ApplicationId)
    )
      AND (@ApplicationId IS NULL OR c.application_id = @ApplicationId)
)"""

old_pattern = r"WITH AllPermissionedNodes AS \([\s\S]*?AND \(@ApplicationId IS NULL OR c\.application_id = @ApplicationId\)\n\)"
new_sql = re.sub(old_pattern, replacement, sql)

with open('/home/victus/Projects/Bussiness-Management/Back-End/Structure/sql/functions.sql', 'w', encoding='utf-8') as f:
    f.write(new_sql)
print('Patched functions.sql')
