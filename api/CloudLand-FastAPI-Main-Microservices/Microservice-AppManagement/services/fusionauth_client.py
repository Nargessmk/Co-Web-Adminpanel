import logging
from typing import Any
from uuid import UUID

from core.config import get_settings
from core.exceptions import NotFoundError

logger = logging.getLogger(__name__)

try:
    import httpx
except ImportError:
    httpx = None


async def _get_fusion_client() -> Any | None:
    settings = get_settings()
    if httpx is None or not settings.fusionauth_auth_url or not settings.fusionauth_api_key:
        return None
    return httpx.AsyncClient(
        base_url=settings.fusionauth_auth_url,
        headers={"Authorization": settings.fusionauth_api_key},
        timeout=httpx.Timeout(15.0, connect=5.0),
    )


async def resolve_user_roles_and_groups(
    user_id: UUID, application_id: UUID
) -> tuple[list[str], list[str], list[str]]:
    client = await _get_fusion_client()
    if client is None:
        return [], [], []
    try:
        user_resp = await client.get(f"/api/user/{user_id}")
        if user_resp.status_code == 404:
            raise NotFoundError(f"User {user_id} not found.")
        if user_resp.status_code >= 400:
            raise RuntimeError("Can not retrieve user information.")
        user = (user_resp.json() or {}).get("user") or {}
        registrations = user.get("registrations") or []
        memberships = user.get("memberships") or []

        app_resp = await client.get(f"/api/application/{application_id}")
        if app_resp.status_code == 404:
            raise NotFoundError(f"Application {application_id} not found.")
        if app_resp.status_code >= 400:
            raise RuntimeError("Application not found.")
        application = (app_resp.json() or {}).get("application") or {}
        app_roles = application.get("roles") or []

        target = next(
            (reg for reg in registrations if reg.get("applicationId") == str(application_id)),
            None,
        )
        if target is None:
            return [], [], []

        role_names = target.get("roles") or []
        role_ids = [str(role["id"]) for role in app_roles if role.get("name") in role_names and role.get("id")]
        group_ids = [str(member["groupId"]) for member in memberships if member.get("groupId")]
        return role_ids, group_ids, role_names
    except (httpx.TimeoutException, httpx.NetworkError) as exc:
        logger.warning("FusionAuth connection timed out / network issue (VPN latency): %s", exc)
        return [], [], []
    except Exception as exc:
        logger.error("Error communicating with FusionAuth: %s", exc, exc_info=True)
        return [], [], []
    finally:
        await client.aclose()
