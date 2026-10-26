from uuid import UUID

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from core.config import get_settings

_bearer_scheme = HTTPBearer(auto_error=False)

settings = get_settings()


class CurrentUser:
    def __init__(
        self,
        user_id: UUID | None,
        roles: list[str],
        is_authenticated: bool,
        app_id: UUID | None = None,
    ):
        self.user_id = user_id
        self.roles = roles
        self.is_authenticated = is_authenticated
        self.app_id = app_id


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    token = credentials.credentials if credentials is not None else None
    if not token:
        token = request.cookies.get("jwt_token")
    if not token:
        return CurrentUser(user_id=None, roles=[], is_authenticated=False)

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"verify_signature": True, "verify_aud": True},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    sub = payload.get("sub")
    roles = payload.get("roles") or payload.get("role") or []
    if isinstance(roles, str):
        roles = [roles]

    user_id: UUID | None = None
    if sub:
        try:
            user_id = UUID(sub)
        except ValueError:
            user_id = None

    app_id: UUID | None = None
    app_id_raw = payload.get("app_id") or payload.get("applicationId") or payload.get("application_id")
    if app_id_raw:
        try:
            app_id = UUID(str(app_id_raw))
        except ValueError:
            app_id = None

    return CurrentUser(user_id=user_id, roles=roles, is_authenticated=True, app_id=app_id)


def require_user(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if not current_user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return current_user


def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if not current_user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    if "admin" not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user


def require_tenant(
    application_id: str = Query(...),
    current_user: CurrentUser = Depends(require_user),
) -> tuple[UUID, CurrentUser]:
    parsed_id: UUID | None = None
    try:
        parsed_id = UUID(application_id)
    except (ValueError, TypeError):
        if "admin" in current_user.roles:
            parsed_id = current_user.app_id or UUID(int=0)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid application_id format. Expected UUID.",
            )

    if "admin" not in current_user.roles and current_user.app_id and parsed_id != current_user.app_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: application_id does not match authenticated tenant",
        )
    return parsed_id, current_user


def resolve_application_id(
    application_id: UUID | None = Query(None),
    current_user: CurrentUser = Depends(require_user),
) -> UUID:
    resolved = application_id or current_user.app_id
    if resolved is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="application_id is required",
        )
    if "admin" not in current_user.roles and resolved != current_user.app_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: application_id does not match authenticated tenant",
        )
    return resolved


def get_uow(request: Request):
    return request.state.uow

