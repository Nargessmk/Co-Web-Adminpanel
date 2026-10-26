"""
IP Geolocation service — mirrors C# IpExtensions.cs.

Uses ip-api.com to get location info for client IPs.
"""

from typing import Any

import httpx
from pydantic import BaseModel

from core.config import Settings, get_settings
from core.logging import get_logger

logger = get_logger("app.ip_api")

_BASE_URL = "http://ip-api.com"


class IPInfo(BaseModel):
    status: str = ""
    country: str = ""
    regionName: str = ""
    city: str = ""
    isp: str = ""
    query: str = ""


async def get_ip_info(ip_address: str | None, settings: Settings | None = None) -> IPInfo | None:
    """Fetch geolocation for an IP address. Returns None on failure."""
    settings = settings or get_settings()
    if not settings.ip_api_enabled or not ip_address:
        return None
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{_BASE_URL}/json/{ip_address}")
            if resp.status_code == 200:
                return IPInfo(**resp.json())
    except Exception:
        logger.debug("IP API lookup failed for %s", ip_address)
    return None
