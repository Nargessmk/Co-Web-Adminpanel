"""
User management schemas — Pydantic models for user CRUD request/response payloads.

These map to the FusionAuth user objects used by the C# service's
UserManagementController and UserManagementService. The C# service
delegates all user operations to FusionAuth's REST API, so these schemas
mirror FusionAuth's user/registration JSON shapes.

Field naming follows FusionAuth's API conventions (camelCase) for wire-format
compatibility.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# FusionAuth user object (simplified — we don't need every field)
# ---------------------------------------------------------------------------

class FusionAuthUserResponse(BaseModel):
    """Simplified representation of a FusionAuth User object.

    The C# service returns the full FusionAuth SDK User object; here we
    expose only the fields the frontend actually uses.
    """
    id: str = Field(..., description="FusionAuth user ID (UUID string)")
    username: str | None = Field(default=None)
    email: str = Field(...)
    firstName: str | None = Field(default=None)
    lastName: str | None = Field(default=None)
    active: bool = Field(default=True)
    verified: bool = Field(default=False)
    insertInstant: int | None = Field(default=None, description="Creation timestamp (epoch ms)")
    lastUpdateInstant: int | None = Field(default=None, description="Last update timestamp (epoch ms)")
    registrations: list[dict] | None = Field(default=None, description="Application registrations")


class FusionAuthRegistrationResponse(BaseModel):
    """A single application registration attached to a user."""
    applicationId: str = Field(...)
    roles: list[str] = Field(default_factory=list)
    insertInstant: int | None = None
    lastUpdateInstant: int | None = None


# ---------------------------------------------------------------------------
# User CRUD requests
# ---------------------------------------------------------------------------

class UserCreateRequest(BaseModel):
    """Create a new user in FusionAuth.

    Mirrors the fields the C# UserManagementService sends to
    POST /api/user/registration.
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, description="Plaintext password")
    firstName: str | None = None
    lastName: str | None = None
    applicationId: str = Field(..., description="FusionAuth application to register against")
    roles: list[str] | None = Field(default=None, description="Initial roles")

    @field_validator('firstName')
    @classmethod
    def validate_first_name(cls, v):
        if v is None:
            return v
        if any(c.isdigit() for c in v):
            raise ValueError('firstName must not contain numbers')
        if len(v.strip()) < 2:
            raise ValueError('firstName must be at least 2 characters')
        return v


class UserUpdateRequest(BaseModel):
    """Update an existing user's profile fields.

    Mirrors the partial update the C# service applies via
    PATCH /api/user/{userId}.
    """
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    firstName: str | None = None
    lastName: str | None = None
    mobilePhone: str | None = None
    imageUrl: str | None = None
    active: bool | None = None
    data: dict | None = None

    @field_validator('mobilePhone')
    @classmethod
    def validate_mobile_phone(cls, v):
        if v is None:
            return v
        import re
        if not re.match(r'^\d{11}$', v):
            raise ValueError('mobilePhone must be exactly 11 digits')
        if not v.startswith('09'):
            raise ValueError('mobilePhone must start with 09')
        return v

    @field_validator('firstName')
    @classmethod
    def validate_first_name(cls, v):
        if v is None:
            return v
        if any(c.isdigit() for c in v):
            raise ValueError('firstName must not contain numbers')
        if len(v.strip()) < 2:
            raise ValueError('firstName must be at least 2 characters')
        return v


class UserSearchRequest(BaseModel):
    """Search / list users with optional filters.

    Mirrors the query parameters the C# UserManagementController exposes.
    """
    query: str | None = Field(default=None, description="Free-text search (email, username)")
    applicationId: str | None = Field(default=None, description="Filter by application registration")
    roles: list[str] | None = Field(default=None, description="Filter by assigned roles")
    active: bool | None = Field(default=None, description="Filter by active status")
    pageIndex: int = Field(default=0, ge=0, description="Page index (0-based)")
    pageSize: int = Field(default=25, ge=1, le=100, description="Items per page")


# ---------------------------------------------------------------------------
# Password management (user-level)
# ---------------------------------------------------------------------------

class UserChangePasswordRequest(BaseModel):
    """User initiates a password change (authenticated).

    Mirrors C#: Cloudland.APM.Models.Auth.PasswordRequest
    """
    id: str = Field(..., description="FusionAuth user ID")
    currentPassword: str = Field(..., description="Current password for verification")
    password: str = Field(..., min_length=8, description="New password")


class UserSelfChangePasswordRequest(BaseModel):
    """User initiates a password change for their own account."""
    applicationId: str = Field(..., description="FusionAuth application ID (must match token)")
    currentPassword: str = Field(..., description="Current password for verification")
    password: str = Field(..., min_length=8, description="New password")


class UserForgotPasswordRequest(BaseModel):
    """User requests a password reset email."""
    applicationId: str = Field(..., description="FusionAuth application ID")
    email: EmailStr = Field(..., description="Registered email address")


class UserResetPasswordRequest(BaseModel):
    """Admin resets a user's password."""
    id: str = Field(..., description="FusionAuth user ID")
    email: EmailStr | None = None
    username: str | None = None
    password: str = Field(..., min_length=8, description="New password")


# ---------------------------------------------------------------------------
# Role & group management
# ---------------------------------------------------------------------------

class RoleAssignmentRequest(BaseModel):
    """Assign roles to a user within an application."""
    userId: str = Field(..., description="FusionAuth user ID")
    applicationId: str = Field(..., description="FusionAuth application ID")
    roles: list[str] = Field(default_factory=list, description="Role names to assign")


class RoleRemovalRequest(BaseModel):
    """Remove specific roles from a user."""
    userId: str = Field(..., description="FusionAuth user ID")
    applicationId: str = Field(..., description="FusionAuth application ID")
    roles: list[str] = Field(default_factory=list, description="Role names to remove")


class GroupMembershipRequest(BaseModel):
    """Add or remove a user from FusionAuth groups."""
    userId: str = Field(..., description="FusionAuth user ID")
    groupIds: list[str] = Field(..., min_length=1, description="Group IDs to set")


# ---------------------------------------------------------------------------
# Response wrappers
# ---------------------------------------------------------------------------

class UserListResponse(BaseModel):
    """Paginated list of users."""
    users: list[FusionAuthUserResponse] = Field(default_factory=list)
    total: int = Field(default=0, description="Total matching users")
    pageIndex: int = Field(default=0)
    pageSize: int = Field(default=25)


class UserDetailResponse(BaseModel):
    """Full user detail including registrations and roles."""
    user: FusionAuthUserResponse
    registrations: list[FusionAuthRegistrationResponse] = Field(default_factory=list)
    roles: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Map of applicationId -> list of role names",
    )
    groupIds: list[str] = Field(default_factory=list)


class MessageResponse(BaseModel):
    """Generic success/error message response."""
    message: str
    success: bool = True


class UserProfileImageResponse(BaseModel):
    """Result of a profile image upload."""
    success: bool
    imageUrl: str | None = None
    error: str | None = None
