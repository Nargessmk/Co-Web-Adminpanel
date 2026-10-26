CREATE OR ALTER FUNCTION dbo.GetConstantsRecursive(
    @ConstantRootId uniqueidentifier,
    @ApplicationId uniqueidentifier = NULL
)
RETURNS TABLE
AS
RETURN
WITH recursive_cte AS (
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
        c.title AS RootTitle,
        1 AS level,
        CAST('01' AS VARCHAR(MAX)) AS [Rank],
        CASE
            WHEN c.node_type_id = c.id THEN c.constant_value
            ELSE nt.constant_value
        END AS NodeType,
        c.[desc] AS [desc]
    FROM tblConstant c
    OUTER APPLY (
        SELECT constant_value
        FROM tblConstant
        WHERE id = c.node_type_id AND id <> c.id
    ) nt
    WHERE c.id = @ConstantRootId
      AND (@ApplicationId IS NULL OR c.application_id = @ApplicationId)

    UNION ALL

    SELECT
        r.id AS Id,
        r.parent_id AS ParentId,
        r.create_at AS CreateAt,
        r.last_modified_at AS LastModifiedAt,
        r.user_created AS UserCreated,
        r.last_modified_user AS LastModifiedUser,
        r.application_id AS ApplicationId,
        r.title AS title,
        r.priority AS Priority,
        r.allow_delete AS AllowDelete,
        r.allow_update AS AllowUpdate,
        r.disabled AS Disabled,
        r.hidden AS hidden,
        r.version AS Version,
        r.constant_value AS ConstantValue,
        r.valid_end_date AS ValidEndDate,
        r.valid_start_date AS ValidStartDate,
        r.value_type AS ValueType,
        r.node_type_id AS NodeTypeId,
        r.color AS Color,
        r.icon AS Icon,
        r.child_must_be_show AS ChildMustBeShow,
        rc.RootTitle + ',' + r.title AS RootTitle,
        rc.level + 1 AS level,
        rc.[Rank] + '-' + RIGHT('00' + CAST(RANK() OVER (PARTITION BY rc.[Rank] ORDER BY r.title) AS VARCHAR(MAX)), 2) AS [Rank],
        CASE
            WHEN r.node_type_id = r.id THEN r.constant_value
            ELSE nt.constant_value
        END AS NodeType,
        r.[desc] AS [desc]
    FROM tblConstant r
    INNER JOIN recursive_cte rc ON r.parent_id = rc.Id
    OUTER APPLY (
        SELECT constant_value
        FROM tblConstant
        WHERE id = r.node_type_id AND id <> r.id
    ) nt
    WHERE rc.ChildMustBeShow = 1
      AND (@ApplicationId IS NULL OR r.application_id = @ApplicationId)
)
SELECT *
FROM recursive_cte;
GO

CREATE OR ALTER FUNCTION dbo.GetConstantsRecursiveWithPermissions(
    @ConstantRootId uniqueidentifier,
    @UserId uniqueidentifier = NULL,
    @RoleIds NVARCHAR(MAX) = NULL,
    @GroupIds NVARCHAR(MAX) = NULL,
    @ApplicationId uniqueidentifier = NULL
)
RETURNS TABLE
AS
RETURN
WITH UserLockState AS (
    SELECT CASE WHEN EXISTS (
        SELECT 1 FROM tblUserConstantPermission 
        WHERE user_id = @UserId 
          AND module_key = '_user_lock'
          AND (@ApplicationId IS NULL OR application_id = @ApplicationId)
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
),
CompleteHierarchy AS (
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
        c.title AS RootTitle,
        1 AS level,
        CAST('01' AS VARCHAR(MAX)) AS [Rank],
        CASE
            WHEN c.node_type_id = c.id THEN c.constant_value
            ELSE nt.constant_value
        END AS NodeType,
        c.[desc] AS [desc]
    FROM tblConstant c
    OUTER APPLY (
        SELECT constant_value
        FROM tblConstant
        WHERE id = c.node_type_id AND id <> c.id
    ) nt
    WHERE c.id = @ConstantRootId
      AND (@ApplicationId IS NULL OR c.application_id = @ApplicationId)

    UNION ALL

    SELECT
        r.id AS Id,
        r.parent_id AS ParentId,
        r.create_at AS CreateAt,
        r.last_modified_at AS LastModifiedAt,
        r.user_created AS UserCreated,
        r.last_modified_user AS LastModifiedUser,
        r.application_id AS ApplicationId,
        r.title AS title,
        r.priority AS Priority,
        r.allow_delete AS AllowDelete,
        r.allow_update AS AllowUpdate,
        r.disabled AS Disabled,
        r.hidden AS hidden,
        r.version AS Version,
        r.constant_value AS ConstantValue,
        r.valid_end_date AS ValidEndDate,
        r.valid_start_date AS ValidStartDate,
        r.value_type AS ValueType,
        r.node_type_id AS NodeTypeId,
        r.color AS Color,
        r.icon AS Icon,
        r.child_must_be_show AS ChildMustBeShow,
        h.RootTitle AS RootTitle,
        h.level + 1 AS level,
        h.[Rank] + '-' + RIGHT('00' + CAST(RANK() OVER (PARTITION BY h.[Rank] ORDER BY r.title) AS VARCHAR(MAX)), 2) AS [Rank],
        CASE
            WHEN r.node_type_id = r.id THEN r.constant_value
            ELSE nt.constant_value
        END AS NodeType,
        r.[desc] AS [desc]
    FROM tblConstant r
    INNER JOIN CompleteHierarchy h ON r.parent_id = h.Id
    OUTER APPLY (
        SELECT constant_value
        FROM tblConstant
        WHERE id = r.node_type_id AND id <> r.id
    ) nt
    WHERE (@ApplicationId IS NULL OR r.application_id = @ApplicationId)
      AND EXISTS (
          SELECT 1 FROM AllPermissionedNodes apn
          WHERE apn.Id = r.id
             OR apn.Id IN (
                 SELECT c2.id FROM tblConstant c2
                 WHERE c2.parent_id = r.id
                    OR c2.id IN (
                        SELECT c3.id FROM tblConstant c3
                        WHERE c3.parent_id IN (SELECT c4.id FROM tblConstant c4 WHERE c4.parent_id = r.id)
                    )
             )
      )
)
SELECT
    h.Id,
    h.ParentId,
    h.CreateAt,
    h.LastModifiedAt,
    h.UserCreated,
    h.LastModifiedUser,
    h.ApplicationId,
    h.title,
    h.Priority,
    h.AllowDelete,
    h.AllowUpdate,
    h.Disabled,
    h.hidden,
    h.Version,
    h.ConstantValue,
    h.ValidEndDate,
    h.ValidStartDate,
    h.ValueType,
    h.NodeTypeId,
    h.Color,
    h.Icon,
    h.ChildMustBeShow,
    h.RootTitle,
    h.level,
    h.[Rank],
    h.NodeType,
    h.[desc]
FROM CompleteHierarchy h
WHERE EXISTS (
    SELECT 1 FROM AllPermissionedNodes apn
    WHERE apn.Id = h.Id
       OR h.Id IN (
           SELECT parent_id FROM tblConstant WHERE id IN (SELECT Id FROM AllPermissionedNodes) AND parent_id IS NOT NULL
           UNION
           SELECT parent_id FROM tblConstant WHERE id IN (
               SELECT parent_id FROM tblConstant WHERE id IN (SELECT Id FROM AllPermissionedNodes) AND parent_id IS NOT NULL
           ) AND parent_id IS NOT NULL
       )
);
GO
