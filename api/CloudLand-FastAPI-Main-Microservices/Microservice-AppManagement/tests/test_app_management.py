import os
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("SENTRY_DSN", "")

import asyncio

import pytest
from jose import jwt
from fastapi.testclient import TestClient
from sqlalchemy import text

from core.config import get_settings
from Models.constant import Constant
from Structure.session import get_db_manager, reset_db_manager

pytestmark = pytest.mark.usefixtures("clean_db")

ROOT_ID = uuid4()
NODE_TYPE_ID = uuid4()
USER_ID = uuid4()
APP_ID = uuid4()
ROLE_ID = uuid4()
GROUP_ID = uuid4()

settings = get_settings()


@pytest.fixture(scope="session", autouse=True)
def clean_db():
    pass


def make_token(roles: list[str] | None = None) -> str:
    payload = {
        "sub": str(USER_ID),
        "app_id": str(APP_ID),
        "roles": roles or ["admin"],
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        return loop.run_until_complete(coro)


def seed() -> None:
    reset_db_manager()
    dm = get_db_manager(settings.database_url)

    async def _seed():
        async with dm.get_uow() as uow:
            await dm.create_tables()
            await uow.session.execute(text("DELETE FROM tblCalendar"))
            await uow.session.execute(text("DELETE FROM tblUserConstantPermission"))
            await uow.session.execute(text("DELETE FROM tblEntityFileAttachment"))
            await uow.session.execute(text("DELETE FROM tblConstant"))
            await uow.commit()
            await uow.constants.add(
                Constant(
                    id=ROOT_ID,
                    title="Root",
                    user_created=USER_ID,
                    last_modified_user=USER_ID,
                    application_id=APP_ID,
                )
            )
            await uow.constants.add(
                Constant(
                    id=NODE_TYPE_ID,
                    title="NodeType",
                    parent_id=ROOT_ID,
                    user_created=USER_ID,
                    last_modified_user=USER_ID,
                    application_id=APP_ID,
                    allow_delete=False,
                    allow_update=False,
                    disabled=True,
                    hidden=True,
                )
            )
            await uow.commit()

    try:
        _run_async(_seed())
    finally:
        _run_async(dm.close())
        reset_db_manager()


@pytest.fixture(scope="module")
def client():
    seed()
    from main import app

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_store_and_retrieve_json_data(client):
    headers = {"Authorization": f"Bearer {make_token()}"}
    child = NODE_TYPE_ID
    body = '{"FullName":"پوشه تست","Icon":"folder","IconColor":"#123456","IsExpand":true,"IconSize":12}'
    r = client.put(
        f"/api/v1/constant/StoreJsonData/{child}?node_type=folder&application_id={APP_ID}",
        headers=headers,
        content=body,
    )
    assert r.status_code == 200 and r.json() is True

    r = client.get(
        f"/api/v1/constant/RetrieveJsonData/{child}?node_type=folder&application_id={APP_ID}",
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["FullName"] == "پوشه تست"

    r = client.put(
        f"/api/v1/constant/StoreJsonData/{child}?node_type=unknown_type&application_id={APP_ID}",
        headers=headers,
        content='{"a": 1}',
    )
    assert r.status_code == 400

    r = client.put(
        f"/api/v1/constant/StoreJsonData/{child}?node_type=database&application_id={APP_ID}",
        headers=headers,
        content='{"not_valid": true}',
    )
    assert r.status_code == 400


def test_calendar_generate_and_paging(client):
    admin = {"Authorization": f"Bearer {make_token(['admin'])}"}
    r = client.post(f"/api/v1/calendar/Generate/1404/{ROOT_ID}?application_id={APP_ID}", headers=admin)
    assert r.status_code == 200 and r.json() == 365

    r = client.get(f"/api/v1/calendar/Paging/1404/1/10?application_id={APP_ID}", headers=admin)
    data = r.json()
    assert data["TotalCount"] == 365 and data["PageSize"] == 10
    assert data["Items"][0]["Date"] == "1404/01/01"
    assert data["Items"][0]["IsHoliday"] is True
    assert "عید نوروز" in data["Items"][0]["Occasion"]

    r = client.post(
        f"/api/v1/calendar/?application_id={APP_ID}",
        headers=admin,
        json={"date": "1405/05/10", "occasion": "تست", "isHoliday": True},
    )
    assert r.status_code == 200 and r.json()["Date"] == "1405/05/10"
    entry_id = r.json()["Id"]

    r = client.post(
        f"/api/v1/calendar/?application_id={APP_ID}",
        headers=admin,
        json={"date": "1405/05/10", "occasion": "تست 2"},
    )
    assert r.status_code == 400

    r = client.put(
        f"/api/v1/calendar/?application_id={APP_ID}",
        headers=admin,
        json={"id": entry_id, "date": "1405/05/11", "occasion": "به‌روزشده"},
    )
    assert r.status_code == 200 and r.json()["title"] == "به‌روزشده"

    r = client.delete(f"/api/v1/calendar/{entry_id}?application_id={APP_ID}", headers=admin)
    assert r.status_code == 204


def test_calendar_generate_far_future_years(client):
    admin = {"Authorization": f"Bearer {make_token(['admin'])}"}
    for year in (1498, 1499):
        r = client.post(f"/api/v1/calendar/Generate/{year}/{ROOT_ID}?application_id={APP_ID}", headers=admin)
        assert r.status_code == 200
        assert r.json() in (365, 366)
    r = client.get(f"/api/v1/calendar/Paging/1498/1/5?application_id={APP_ID}", headers=admin)
    assert r.status_code == 200 and r.json()["TotalCount"] > 0


def test_update_constant_permission(client):
    headers = {"Authorization": f"Bearer {make_token()}"}
    base = "/api/v1/ConstantPermission"

    r = client.post(
        f"{base}/UpdateConstantPermission?role_id={ROLE_ID}&application_id={APP_ID}",
        headers=headers,
        json=[str(NODE_TYPE_ID)],
    )
    assert r.status_code == 200 and len(r.json()) == 1
    assert r.json()[0]["ConstantId"] == str(NODE_TYPE_ID)

    r = client.get(
        f"{base}/GetConstantWithPermissionForRole/{ROOT_ID}/{ROLE_ID}?application_id={APP_ID}",
        headers=headers,
    )
    assert r.status_code == 200
    result = r.json()
    assert len(result) >= 1
    assert str(NODE_TYPE_ID) in {i["Id"] for i in result}

    r = client.post(
        f"{base}/UpdateConstantPermission?role_id={ROLE_ID}&application_id={APP_ID}",
        headers=headers,
        json=[],
    )
    assert r.status_code == 200 and r.json() == []

    r = client.get(
        f"{base}/GetConstantWithPermissionForRole/{ROOT_ID}/{ROLE_ID}?application_id={APP_ID}",
        headers=headers,
    )
    assert r.status_code == 200 and r.json() == []


async def _seed_nodes(dm, node_id, child_id):
    async with dm.get_uow() as uow:
        await uow.constants.add(
            Constant(
                id=node_id,
                title="ParityNode",
                parent_id=ROOT_ID,
                user_created=USER_ID,
                last_modified_user=USER_ID,
                application_id=APP_ID,
            )
        )
        await uow.constants.add(
            Constant(
                id=child_id,
                title="ParityChild",
                parent_id=node_id,
                user_created=USER_ID,
                last_modified_user=USER_ID,
                application_id=APP_ID,
            )
        )
        await uow.commit()


def test_constant_route_parity(client):
    headers = {"Authorization": f"Bearer {make_token()}"}

    r = client.get(f"/api/v1/constant/ById/{uuid4()}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 200 and r.json() is None

    r = client.post(
        f"/api/v1/constant/?application_id={APP_ID}",
        headers=headers,
        json={"title": "X", "parentId": str(ROOT_ID)},
    )
    assert r.status_code == 400

    node_id = uuid4()
    child_id = uuid4()
    reset_db_manager()
    dm = get_db_manager(settings.database_url)

    try:
        _run_async(_seed_nodes(dm, node_id, child_id))
    finally:
        _run_async(dm.close())
        reset_db_manager()

    r = client.request(
        "GET",
        f"/api/v1/constant/ByIds?application_id={APP_ID}",
        json=[str(child_id), str(child_id)],
        headers=headers,
    )
    assert r.status_code == 200 and len(r.json()) == 1

    r = client.request("GET", f"/api/v1/constant/ByIds?application_id={APP_ID}", json=[], headers=headers)
    assert r.status_code == 400

    r = client.put(
        f"/api/v1/constant/?application_id={APP_ID}",
        headers=headers,
        json={"id": str(child_id), "title": "Renamed"},
    )
    assert r.status_code == 200 and r.json()["title"] == "Renamed"

    r = client.delete(f"/api/v1/constant/{uuid4()}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 204

    r = client.delete(f"/api/v1/constant/{ROOT_ID}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 400

    r = client.delete(f"/api/v1/constant/{node_id}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 204

    r = client.delete(f"/api/v1/constant/{child_id}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 204

    r = client.delete(f"/api/v1/constant/DeleteAllChild/{ROOT_ID}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 400


def test_delete_all_child_constants(client):
    headers = {"Authorization": f"Bearer {make_token()}"}
    node_id = uuid4()
    child_id = uuid4()
    grandchild_id = uuid4()
    reset_db_manager()
    dm = get_db_manager(settings.database_url)

    async def _seed():
        async with dm.get_uow() as uow:
            await uow.constants.add(
                Constant(
                    id=node_id,
                    title="ParentNode",
                    parent_id=ROOT_ID,
                    user_created=USER_ID,
                    last_modified_user=USER_ID,
                    application_id=APP_ID,
                )
            )
            await uow.constants.add(
                Constant(
                    id=child_id,
                    title="ChildNode",
                    parent_id=node_id,
                    user_created=USER_ID,
                    last_modified_user=USER_ID,
                    application_id=APP_ID,
                )
            )
            await uow.constants.add(
                Constant(
                    id=grandchild_id,
                    title="GrandchildNode",
                    parent_id=child_id,
                    user_created=USER_ID,
                    last_modified_user=USER_ID,
                    application_id=APP_ID,
                )
            )
            await uow.commit()

    try:
        _run_async(_seed())
    finally:
        _run_async(dm.close())
        reset_db_manager()

    r = client.delete(
        f"/api/v1/constant/DeleteAllChild/{node_id}?application_id={APP_ID}", headers=headers
    )
    assert r.status_code == 204

    r = client.get(f"/api/v1/constant/ById/{node_id}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 200 and r.json()["title"] == "ParentNode"

    r = client.get(f"/api/v1/constant/ById/{child_id}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 200 and r.json() is None

    r = client.get(f"/api/v1/constant/ById/{grandchild_id}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 200 and r.json() is None

    r = client.delete(f"/api/v1/constant/{node_id}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 204

    r = client.get(
        f"/api/v1/constant/GetConstantNodeType/{uuid4()}/{NODE_TYPE_ID}?application_id={APP_ID}",
        headers=headers,
    )
    assert r.status_code == 200


def test_reindex_views_and_calendar(client):
    headers = {"Authorization": f"Bearer {make_token()}"}

    r = client.get("/api/v1/Reindex/views", headers=headers)
    assert r.status_code == 200
    assert r.json() == ["Constant", "ConstantRecursive", "Calendar"]

    r = client.post(f"/api/v1/Reindex/reindex/Unknown?application_id={APP_ID}", headers=headers)
    assert r.status_code == 400
    assert "not supported" in r.json()["Message"]

    from services.elastic_client import get_es_client

    es_configured = get_es_client() is not None

    r = client.post(f"/api/v1/Reindex/reindex/Calendar?application_id={APP_ID}", headers=headers)
    if es_configured:
        assert r.status_code == 200
    else:
        assert r.status_code == 400
        assert "Elasticsearch is not configured" in r.json()["Message"]

    r = client.post(f"/api/v1/Reindex/reindex-all?application_id={APP_ID}", headers=headers)
    if es_configured:
        assert r.status_code == 200
    else:
        assert r.status_code == 400
        assert "Elasticsearch is not configured" in r.json()["Message"]


def test_tenant_isolation(client):
    other_app_id = uuid4()
    app_a = {"Authorization": f"Bearer {make_token()}"}
    app_b_token = jwt.encode(
        {
            "sub": str(USER_ID),
            "app_id": str(other_app_id),
            "roles": ["admin"],
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        },
        settings.jwt_secret_key,
        algorithm="HS256",
    )
    app_b = {"Authorization": f"Bearer {app_b_token}"}

    r = client.get(f"/api/v1/constant/ById/{ROOT_ID}?application_id={other_app_id}", headers=app_b)
    assert r.status_code == 200 and r.json() is None

    r = client.post(
        f"/api/v1/calendar/?application_id={other_app_id}",
        headers=app_b,
        json={"date": "1410/01/01", "occasion": "تست اپ ب"},
    )
    assert r.status_code == 200
    other_id = r.json()["Id"]

    r = client.get(f"/api/v1/calendar/ById/{other_id}?application_id={other_app_id}", headers=app_b)
    assert r.status_code == 200 and r.json()["Occasion"] == "تست اپ ب"

    r = client.get(f"/api/v1/calendar/ById/{other_id}?application_id={APP_ID}", headers=app_a)
    assert r.status_code == 404

    r = client.get(f"/api/v1/calendar/Paging/1410/1/10?application_id={APP_ID}", headers=app_a)
    assert r.json()["TotalCount"] == 0

    r = client.get(f"/api/v1/calendar/Paging/1410/1/10?application_id={other_app_id}", headers=app_b)
    assert r.json()["TotalCount"] == 1

    r = client.delete(f"/api/v1/calendar/{other_id}?application_id={APP_ID}", headers=app_a)
    assert r.status_code == 404

    r = client.delete(f"/api/v1/calendar/{other_id}?application_id={other_app_id}", headers=app_b)
    assert r.status_code == 204


def test_tenant_input_isolation(client):
    other_app_id = uuid4()
    app_a = {"Authorization": f"Bearer {make_token()}"}
    app_b_token = jwt.encode(
        {
            "sub": str(USER_ID),
            "app_id": str(other_app_id),
            "roles": ["admin"],
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        },
        settings.jwt_secret_key,
        algorithm="HS256",
    )
    app_b = {"Authorization": f"Bearer {app_b_token}"}

    r = client.post(
        f"/api/v1/constant/?application_id={other_app_id}",
        headers=app_b,
        json={"title": "نود خارجی", "parent_id": str(ROOT_ID), "node_type_id": str(NODE_TYPE_ID)},
    )
    assert r.status_code == 400

    r = client.post(
        f"/api/v1/constant/?application_id={APP_ID}",
        headers=app_a,
        json={"title": "نود خودی", "parent_id": str(ROOT_ID), "node_type_id": str(NODE_TYPE_ID)},
    )
    assert r.status_code == 200
    own_id = r.json()["Id"]

    r = client.put(
        f"/api/v1/constant/?application_id={other_app_id}",
        headers=app_b,
        json={"id": own_id, "parent_id": str(ROOT_ID)},
    )
    assert r.status_code == 404

    r = client.post(
        f"/api/v1/ConstantPermission/UpdateConstantPermission?role_id={ROLE_ID}&application_id={other_app_id}",
        headers=app_b,
        json=[str(NODE_TYPE_ID)],
    )
    assert r.status_code == 200 and r.json() == []

    r = client.post(
        f"/api/v1/calendar/Generate/1410/{ROOT_ID}?application_id={other_app_id}",
        headers=app_b,
    )
    assert r.status_code == 404

    r = client.post(
        f"/api/v1/calendar/?application_id={other_app_id}",
        headers=app_b,
        json={"date": "1410/02/02", "occasion": "خارجی", "parent_id": str(ROOT_ID)},
    )
    assert r.status_code == 404

    r = client.delete(f"/api/v1/constant/{own_id}?application_id={APP_ID}", headers=app_a)
    assert r.status_code == 204


def test_application_id_in_query_params(client):
    headers = {"Authorization": f"Bearer {make_token()}"}

    r = client.get(f"/api/v1/constant/?application_id={APP_ID}", headers=headers)
    assert r.status_code == 200
    roots = r.json()
    assert len(roots) > 0
    assert roots[0]["ApplicationId"] == str(APP_ID)

    r = client.get(f"/api/v1/constant/ById/{ROOT_ID}?application_id={APP_ID}", headers=headers)
    assert r.status_code == 200
    assert r.json()["ApplicationId"] == str(APP_ID)

    wrong_app = uuid4()
    r = client.get(f"/api/v1/constant/ById/{ROOT_ID}?application_id={wrong_app}", headers=headers)
    assert r.status_code == 200 and r.json() is None
