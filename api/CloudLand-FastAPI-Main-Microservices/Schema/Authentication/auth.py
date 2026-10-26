"""
Authentication schemas — Pydantic models for auth-related request/response payloads.

These map directly to the C# models in Cloudland.APM.Models/Auth/ and
Cloudland.APM.Models/JWT/, preserving field names and types for API
compatibility with the existing C# backend.

Field naming follows the C# convention (camelCase) to maintain wire-format
compatibility with the C# API Gateway and frontend clients.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Login / Registration
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    """Login payload sent by the client.

    Mirrors C#: Cloudland.APM.Models.Auth.LoginModel
    """
    applicationId: str = Field(..., description="FusionAuth application ID (tenant)")
    userName: str = Field(..., description="Username or email")
    password: str = Field(..., description="Plaintext password (HTTPS required)")


class ResolveApplicationRequest(BaseModel):
    """Resolve which application a user belongs to based on credentials.

    When a username exists in multiple applications with different passwords,
    this endpoint identifies the correct application by trying each one.
    """
    userName: str = Field(..., description="Username or email")
    password: str = Field(..., description="Plaintext password")


class RegisterRequest(BaseModel):
    """User registration payload.

    Mirrors C#: FusionAuth registration request fields used by the C# service.
    """
    applicationId: str = Field(..., description="FusionAuth application ID to register against")
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Desired username")
    password: str = Field(..., description="Plaintext password")
    firstName: str | None = Field(default=None)
    lastName: str | None = Field(default=None)
    roles: list[str] | None = Field(default=None, description="Roles to assign on registration")


# ---------------------------------------------------------------------------
# Token exchange
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    """Response after successful login or token refresh.

    Mirrors C#: Cloudland.APM.Models.JWT.TokenRequest (partial — we don't
    send the full FusionAuth User object back, just the tokens and basic info).
    """
    accessToken: str = Field(..., description="Short-lived JWT access token")
    refreshToken: str = Field(..., description="Long-lived refresh token")
    tokenType: str = Field(default="Bearer", description="Token type prefix")
    expiresIn: int = Field(..., description="Access token lifetime in seconds")
    userId: str = Field(..., description="FusionAuth user ID")
    applicationId: str = Field(..., description="FusionAuth application ID")


class RefreshTokenRequest(BaseModel):
    """Refresh token exchange request.

    Mirrors C#: Cloudland.APM.Models.JWT.TokenRequest (partial).
    """
    refreshToken: str = Field(..., description="The refresh token to exchange")


class LogoutRequest(BaseModel):
    """Logout request — invalidates the refresh token."""
    refreshToken: str | None = Field(default=None, description="Refresh token to revoke")


# ---------------------------------------------------------------------------
# Password management
# ---------------------------------------------------------------------------

class ChangePasswordRequest(BaseModel):
    """Authenticated password change (user knows current password).

    Mirrors C#: Cloudland.APM.Models.Auth.PasswordRequest
    """
    id: str = Field(..., description="FusionAuth user ID")
    currentPassword: str = Field(..., description="Current password for verification")
    password: str = Field(..., description="New password")


class ChangePasswordWithTokenRequest(BaseModel):
    """Password change via confirmation token (forced password change flow).

    Mirrors C#: Cloudland.APM.Models.Auth.PasswordRequestRequired
    """
    id: str = Field(..., description="FusionAuth user ID")
    changePasswordId: str = Field(..., description="Confirmation token from FusionAuth")
    currentPassword: str = Field(..., description="Current password")
    password: str = Field(..., description="New password")


class AdminResetPasswordRequest(BaseModel):
    """Admin-initiated password reset (generates a random new password).

    Mirrors C#: Cloudland.APM.Models.Auth.ResetPasswordRequest
    """
    Id: UUID = Field(..., description="FusionAuth user ID")
    Email: str | None = Field(default=None, description="User email (used for notification)")
    UserName: str | None = Field(default=None, description="Username")
    newPassword: str | None = Field(default=None, description="Explicit new password (optional)")


class ForgotPasswordRequest(BaseModel):
    """User-initiated forgot password — sends a reset email via FusionAuth.

    Mirrors C#: the forgot-password endpoint payload in the C# service.
    """
    applicationId: str = Field(..., description="FusionAuth application ID")
    email: str = Field(..., description="Registered email address")


class ResetPasswordConfirmRequest(BaseModel):
    """Confirm password reset with the token from the email."""
    changePasswordId: str = Field(..., description="Token from the reset email")
    password: str = Field(..., description="New password")


# ---------------------------------------------------------------------------
# Security questions
# ---------------------------------------------------------------------------

class SecurityQuestionAnswer(BaseModel):
    """Single security question + answer pair.

    Mirrors C#: Cloudland.APM.DTO.SecurityQuestionsDTO
    """
    QuestionId: int = Field(..., description="Security question identifier")
    Answer: str = Field(..., description="User's answer")


class SecurityQuestionsRequest(BaseModel):
    """Set or verify security questions for a user.

    Mirrors C#: Cloudland.APM.DTO.UserSecurityQuestionsDTO
    """
    Email: str = Field(..., description="User email")
    Questions: list[SecurityQuestionAnswer] = Field(..., description="List of Q&A pairs")


# ---------------------------------------------------------------------------
# Two-factor authentication
# ---------------------------------------------------------------------------

class TwoFactorSetupRequest(BaseModel):
    """Client-side 2FA setup confirmation — verifies the initial TOTP code.

    Mirrors C#: Cloudland.APM.DTO.TwoFactorRequestFromClientDTO
    """
    UserId: UUID = Field(..., description="FusionAuth user ID")
    secret: str | None = Field(default=None, description="TOTP secret (raw)")
    secretBase32Encoded: str | None = Field(default=None, description="TOTP secret (Base32)")
    code: str | None = Field(default=None, description="6-digit TOTP code to verify")


class TwoFactorLoginRequest(BaseModel):
    """Second-step 2FA verification during login.

    Mirrors C#: Cloudland.APM.DTO.TwoFactorLoginDTO
    """
    applicationId: UUID = Field(..., description="FusionAuth application ID")
    userId: UUID = Field(..., description="FusionAuth user ID")
    twoFactorId: str | None = Field(default=None, description="2FA challenge ID from login response")
    code: str | None = Field(default=None, description="6-digit TOTP code")
    ipAddress: str | None = Field(default=None, description="Client IP address")


class TwoFactorSecretResponse(BaseModel):
    """Returned after initiating 2FA setup — contains the secret for the authenticator app.

    Mirrors C#: Cloudland.APM.DTO.TwoFactorSecretDetailDTO
    """
    secret: str | None = Field(default=None, description="Raw TOTP secret")
    secretBase32Encoded: str | None = Field(default=None, description="Base32-encoded secret for QR code")


class TwoFactorDisableRequest(BaseModel):
    """Disable 2FA for a user.

    Mirrors C#: Cloudland.APM.DTO.TwoFactorDisableRequestDTO
    """
    UserId: UUID = Field(..., description="FusionAuth user ID")
    Code: str = Field(default="", description="Current TOTP code to verify identity")


# ---------------------------------------------------------------------------
# User remove from application
# ---------------------------------------------------------------------------

class UserRemoveApplicationRequest(BaseModel):
    """Detach a user from a FusionAuth application.

    Mirrors C#: Cloudland.APM.Models.Auth.UserRemoveApplicationRequest
    """
    Id: UUID = Field(..., description="FusionAuth user ID")
    ApplicationId: UUID = Field(..., description="FusionAuth application ID")
    Email: str | None = Field(default=None)
    UserName: str | None = Field(default=None)


# ---------------------------------------------------------------------------
# Role management
# ---------------------------------------------------------------------------

class UserRolesRequest(BaseModel):
    """Assign or update roles for a user within an application.

    Mirrors C#: Cloudland.APM.Models.Auth.UserRoles
    """
    UserId: UUID = Field(..., description="FusionAuth user ID")
    ApplicationId: UUID = Field(..., description="FusionAuth application ID")
    Roles: list[str] | None = Field(default=None, description="Role names to assign")


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------

class UserCreationResult(BaseModel):
    """Result of a user creation attempt.

    Mirrors C#: Cloudland.APM.Models.ResultModel.UserCreationResult
    """
    User: dict | None = Field(default=None, description="Created FusionAuth user object")
    Errors: list[dict[str, str]] | None = Field(default=None, description="Validation errors")


class RoleInfo(BaseModel):
    """FusionAuth role metadata.

    Mirrors C#: Cloudland.APM.DTO.FusionSpecialObjects.RoleInfo
    """
    Name: str = Field(..., description="Role name")
    Id: UUID | None = Field(default=None, description="Role ID")


class RoleResult(BaseModel):
    """Role with its assigned users.

    Mirrors C#: Cloudland.APM.Models.ResultModel.RoleResult
    """
    ApplicationName: str = Field(default="", description="Application display name")
    Role: RoleInfo | None = Field(default=None)
    Users: list[dict] | None = Field(default=None, description="Users assigned to this role")


class UserRolesAndGroups(BaseModel):
    """Aggregated roles and groups for a user across all applications.

    Mirrors C#: Cloudland.APM.DTO.FusionSpecialObjects.UserRolesAndGroups
    """
    ApplicationRoles: dict[str, list[RoleInfo]] = Field(
        default_factory=dict,
        description="Map of applicationId -> list of roles",
    )
    GroupIds: list[UUID] = Field(default_factory=list, description="FusionAuth group IDs")
