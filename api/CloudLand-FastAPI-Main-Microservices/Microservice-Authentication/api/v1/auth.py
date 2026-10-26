"""
Authentication endpoints — register, login, refresh, logout, password management.

Mirrors C# AuthController with matching authorization attributes:
- Class default: [Authorize] (all endpoints require JWT)
- [AllowAnonymous]: login, 2FA login, change-password, forgot-password, verify-security-questions
- [Authorize(Roles = "admin")]: list users
"""

from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, Response, status

from api.dependencies import AdminUser, get_current_user
from core.config import Settings, get_settings
from core.exceptions import FusionAuthAPIError, FusionAuthNotFoundError
from core.security import InvalidTokenError, TokenPayload, generate_csrf_token
from Schema.Authentication.auth import (
    AdminResetPasswordRequest,
    ChangePasswordWithTokenRequest,
    ForgotPasswordRequest,
    LoginRequest,
    ResolveApplicationRequest,
    SecurityQuestionsRequest,
    TwoFactorDisableRequest,
    TwoFactorLoginRequest,
    TwoFactorSetupRequest,
)
from services.auth_service import AuthService, get_auth_service
from services.two_factor import TwoFactorService, get_two_factor_service

# Public router (no auth required)
router = APIRouter()

# Protected router — auth is enforced by individual dependencies (AdminUser, get_current_user)
protected_router = APIRouter()


def _get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def _set_refresh_cookie(response: Response, refresh_token: str, settings: Settings) -> None:
    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.refresh_token_expire_days * 86400,
    )
    # CSRF cookie: readable by JavaScript for double-submit pattern
    response.set_cookie(
        key=settings.csrf_cookie_name,
        value=generate_csrf_token(settings.csrf_token_length),
        httponly=False,
        secure=True,
        samesite="strict",
        max_age=settings.refresh_token_expire_days * 86400,
    )


def _clear_refresh_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(key="refreshToken", httponly=True, secure=True, samesite="strict")
    response.delete_cookie(key=settings.csrf_cookie_name, httponly=False, secure=True, samesite="strict")


# ------------------------------------------------------------------
# AllowAnonymous endpoints
# ------------------------------------------------------------------

@router.post("/login", summary="Authenticate user", status_code=status.HTTP_200_OK)
async def login(
    model: LoginRequest,
    request: Request,
    response: Response,
    auth: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> dict:
    ip = _get_client_ip(request)
    try:
        result = await auth.login(model, ip_address=ip)
    except FusionAuthAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc

    status_code = result.get("statusCode", 202)

    if status_code == 203:
        raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail=result)

    if status_code == 242:
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail=result)

    _set_refresh_cookie(response, result["refreshToken"], settings)

    return {
        "statusCode": 202,
        "userName": result["userName"],
        "token": result["accessToken"],
        "roles": result["roles"],
        "userId": result["userId"],
        "applicationId": result["applicationId"],
    }


@router.post("/resolve-application", summary="Resolve application ID from username and password")
async def resolve_application(
    model: ResolveApplicationRequest,
    auth: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        result = await auth.resolve_application(model)
        return {
            "statusCode": 200,
            "applicationId": result["applicationId"],
            "userName": result["userName"],
            "userId": result["userId"],
        }
    except FusionAuthAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc


@router.post("/login/two-factor", summary="Complete two-factor authentication")
async def login_two_factor(
    model: TwoFactorLoginRequest,
    request: Request,
    response: Response,
    auth: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> dict:
    ip = _get_client_ip(request)
    try:
        result = await auth.login_with_two_factor(model, ip_address=ip)
    except FusionAuthAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc

    _set_refresh_cookie(response, result["refreshToken"], settings)

    return {
        "statusCode": 202,
        "userName": result["userName"],
        "token": result["accessToken"],
        "roles": result["roles"],
        "userId": result["userId"],
        "applicationId": result["applicationId"],
    }


@router.post("/register", summary="Register new user", status_code=status.HTTP_201_CREATED)
async def register(
    model: ForgotPasswordRequest,
    auth: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        change_password_id = await auth.forgot_password(model)
        return {"message": "Password reset email sent", "changePasswordId": change_password_id}
    except FusionAuthAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc


@router.post("/forgot-password", summary="Send forgot password email")
async def forgot_password(
    model: ForgotPasswordRequest,
    auth: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        change_password_id = await auth.forgot_password(model)
        return {"message": "Password reset email sent", "changePasswordId": change_password_id}
    except FusionAuthAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc


@router.post("/change-password", summary="Change password with confirmation token")
async def change_password(
    model: ChangePasswordWithTokenRequest,
    auth: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        result = await auth.change_password_with_token(model)
        return {"message": "Password changed successfully", "state": result}
    except FusionAuthAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc


@router.post("/change-password/{change_password_id}", summary="Change password using forgot-password token")
async def change_password_for_login(
    change_password_id: str,
    password: str,
    email: str,
    auth: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        result = await auth.change_password_for_login(change_password_id, password, email)
        return {"message": "Password changed successfully", "state": result}
    except FusionAuthAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc


@router.post("/verify-security-questions", summary="Verify security questions for password reset")
async def verify_security_questions(
    model: SecurityQuestionsRequest,
    auth: AuthService = Depends(get_auth_service),
) -> dict:
    try:
        change_password_id = await auth.verify_security_questions(model)
        return {"changePasswordId": change_password_id}
    except FusionAuthAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code or status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc


@protected_router.post("/reset-password", summary="Admin reset password (auto-generates if not supplied)")
async def reset_password(
    model: AdminResetPasswordRequest,
    admin: AdminUser,
    auth: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Admin resets user password. If newPassword is not supplied,
    an 8-char alphanumeric password is auto-generated (matches C# behavior).
    """
    try:
        result = await auth.reset_password(str(model.Id), model.newPassword)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "message": "Password reset successfully",
            "newPassword": result.get("newPassword", ""),
        }
    except FusionAuthAPIError as exc:
        raise HTTPException(
            status_code=exc.status_code or 400, detail=exc.message,
        ) from exc


# ------------------------------------------------------------------
# [Authorize] endpoints (require valid JWT)
# ------------------------------------------------------------------

@protected_router.post("/refresh", summary="Refresh access token")
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    auth: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> dict:
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found in cookie")

    try:
        result = await auth.refresh_token(refresh_token)
    except FusionAuthAPIError as exc:
        raise HTTPException(status_code=exc.status_code or status.HTTP_401_UNAUTHORIZED, detail=exc.message) from exc

    _set_refresh_cookie(response, result["refreshToken"], settings)
    return {"AccessToken": result["accessToken"]}


@protected_router.post("/logout", summary="Log out user")
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    auth: AuthService = Depends(get_auth_service),
    settings: Settings = Depends(get_settings),
) -> dict:
    _clear_refresh_cookie(response, settings)
    return await auth.logout(refresh_token)


@protected_router.get("/me/{user_id}", summary="Get user info by ID")
async def get_me(
    user_id: str,
    auth: AuthService = Depends(get_auth_service),
    current_user: TokenPayload = Depends(get_current_user),
) -> dict:
    user = await auth.get_me(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ------------------------------------------------------------------
# [Authorize(Roles = "admin")] endpoints
# ------------------------------------------------------------------

@protected_router.get("/list-of-users", summary="List all users (admin only)")
async def list_of_users(
    admin: AdminUser,
    auth: AuthService = Depends(get_auth_service),
) -> list:
    try:
        from services.user_service import get_user_service
        svc = get_user_service()
        return await svc.get_users()
    except FusionAuthAPIError as exc:
        raise HTTPException(status_code=exc.status_code or 400, detail=exc.message) from exc


@protected_router.get("/list-of-users/{number_of_results:int}", summary="List users with limit (admin only)")
async def list_of_users_limit(
    number_of_results: int,
    admin: AdminUser,
    excluded_application_id: str | None = Query(default=None, description="FusionAuth applicationId to exclude from results"),
    auth: AuthService = Depends(get_auth_service),
) -> list:
    try:
        from services.user_service import get_user_service
        svc = get_user_service()
        query = "*"
        if excluded_application_id:
            query += f" AND NOT registrations.applicationId:{excluded_application_id}"
        result = await svc._client.search_users_by_query({
            "queryString": query,
            "startRow": 0,
            "numberOfResults": number_of_results,
        })
        return sorted(result.get("users", []), key=lambda u: u.get("username", ""))
    except FusionAuthAPIError as exc:
        raise HTTPException(status_code=exc.status_code or 400, detail=exc.message) from exc


# ------------------------------------------------------------------
# [Authorize(Roles = "admin, user")] endpoints — 2FA
# ------------------------------------------------------------------

@protected_router.get("/two-factor/secret", summary="Get 2FA secret for setup")
async def get_two_factor_secret(
    current_user: TokenPayload = Depends(get_current_user),
    svc: TwoFactorService = Depends(get_two_factor_service),
) -> dict:
    try:
        return await svc.get_secret()
    except FusionAuthAPIError as exc:
        raise HTTPException(status_code=exc.status_code or 400, detail=exc.message) from exc


@protected_router.post("/two-factor/enable", summary="Enable 2FA")
async def enable_two_factor(
    model: TwoFactorSetupRequest,
    current_user: TokenPayload = Depends(get_current_user),
    svc: TwoFactorService = Depends(get_two_factor_service),
) -> dict:
    try:
        result = await svc.enable(model)
        return {"message": "2FA enabled", "response": result}
    except FusionAuthAPIError as exc:
        raise HTTPException(status_code=exc.status_code or 400, detail=exc.message) from exc


@protected_router.post("/two-factor/disable", summary="Disable 2FA")
async def disable_two_factor(
    model: TwoFactorDisableRequest,
    current_user: TokenPayload = Depends(get_current_user),
    svc: TwoFactorService = Depends(get_two_factor_service),
) -> dict:
    try:
        await svc.disable(model)
        return {"message": "2FA disabled successfully"}
    except FusionAuthAPIError as exc:
        raise HTTPException(status_code=exc.status_code or 400, detail=exc.message) from exc


@protected_router.get("/two-factor/status", summary="Get 2FA status")
async def get_two_factor_status(
    current_user: TokenPayload = Depends(get_current_user),
    svc: TwoFactorService = Depends(get_two_factor_service),
) -> dict:
    return await svc.get_status(current_user.sub, current_user.app_id)


# Export both routers
__all__ = ["router", "protected_router"]
