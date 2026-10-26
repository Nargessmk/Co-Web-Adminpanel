import sys
import os
import uuid
import pytest
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from api.dependencies import CurrentUser, require_user, require_tenant


def _get_test_application_id() -> uuid.UUID:
    app_id = os.environ.get("TEST_APPLICATION_ID")
    if app_id:
        return uuid.UUID(app_id)
    return uuid.uuid4()


@pytest.fixture
def test_user():
    app_id = _get_test_application_id()
    return CurrentUser(
        user_id=uuid.uuid4(),
        roles=["admin"],
        is_authenticated=True,
        app_id=app_id,
    )


@pytest.fixture
def mock_require_user(test_user):
    def _override():
        return test_user
    return _override


@pytest.fixture
def mock_require_tenant(test_user):
    def _override():
        return (test_user.app_id, test_user)
    return _override


@pytest.fixture(autouse=True)
def override_dependencies(test_user, mock_require_user, mock_require_tenant):
    app.dependency_overrides[require_user] = mock_require_user
    app.dependency_overrides[require_tenant] = mock_require_tenant
    yield
    app.dependency_overrides.pop(require_user, None)
    app.dependency_overrides.pop(require_tenant, None)


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_unauthorized_buckets(test_user):
    app.dependency_overrides.pop(require_tenant, None)
    app.dependency_overrides.pop(require_user, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/buckets/list-buckets", params={"application_id": str(test_user.app_id)})
    assert response.status_code == 401
