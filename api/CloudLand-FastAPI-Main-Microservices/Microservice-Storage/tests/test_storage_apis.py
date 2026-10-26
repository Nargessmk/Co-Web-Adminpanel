import os
import sys
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
async def test_health_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_bucket_management_apis():
    bucket_name = f"test-bucket-{uuid.uuid4().hex[:6]}"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. list-buckets
        res = await ac.get("/api/v1/buckets/list-buckets")
        assert res.status_code in [200, 503]

        # 2. make-bucket
        res = await ac.post("/api/v1/buckets/make-bucket", json={"bucket_name": bucket_name})
        assert res.status_code in [200, 400, 503]

        # 3. is-exist-bucket
        res = await ac.get(f"/api/v1/buckets/is-exist-bucket/{bucket_name}")
        assert res.status_code in [200, 503]

        # 4. set-version
        res = await ac.post("/api/v1/buckets/set-version", json={"bucket_name": bucket_name, "enabled": True})
        assert res.status_code in [200, 404, 501, 503]

        # 5. get-version
        res = await ac.get(f"/api/v1/buckets/get-version/{bucket_name}")
        assert res.status_code in [200, 404, 501, 503]

        # 6. set-bucket-encryption
        res = await ac.post("/api/v1/buckets/set-bucket-encryption", json={"bucket_name": bucket_name})
        assert res.status_code in [200, 404, 501, 503]

        # 7. PutBucketEncryption (Legacy 501)
        res = await ac.put(f"/api/v1/buckets/PutBucketEncryption/{bucket_name}")
        assert res.status_code == 501

        # 8. GetBucketEncryption (Legacy 501)
        res = await ac.get(f"/api/v1/buckets/GetBucketEncryption/{bucket_name}")
        assert res.status_code == 501

        # 9. DeleteBucketEncryption (Legacy 501)
        res = await ac.delete(f"/api/v1/buckets/DeleteBucketEncryption/{bucket_name}")
        assert res.status_code == 501

        # 10. get-bucket-encryption
        res = await ac.get(f"/api/v1/buckets/get-bucket-encryption/{bucket_name}")
        assert res.status_code in [200, 404, 501, 503]

        # 11. remove-bucket-encryption
        res = await ac.delete(f"/api/v1/buckets/remove-bucket-encryption?bucketName={bucket_name}")
        assert res.status_code in [200, 404, 501, 503]

        # 12. set-bucket-tags
        res = await ac.post("/api/v1/buckets/set-bucket-tags", json={"bucket_name": bucket_name, "tags": {"env": "test"}})
        assert res.status_code in [200, 404, 503]

        # 13. get-bucket-tags
        res = await ac.get(f"/api/v1/buckets/get-bucket-tags/{bucket_name}")
        assert res.status_code in [200, 404, 503]

        # 14. remove-bucket-tags
        res = await ac.delete(f"/api/v1/buckets/remove-bucket-tags/{bucket_name}")
        assert res.status_code in [200, 404, 503]

        # 15. set-bucket-lifecycle
        res = await ac.post("/api/v1/buckets/set-bucket-lifecycle", json={"bucket_name": bucket_name, "expire_date": "2026-12-31T00:00:00Z"})
        assert res.status_code in [200, 404, 501, 503]

        # 16. PutBucketLifecycleConfiguration (Legacy 501)
        res = await ac.put(f"/api/v1/buckets/PutBucketLifecycleConfiguration/{bucket_name}")
        assert res.status_code == 501

        # 17. GetBucketLifecycleConfiguration (Legacy 501)
        res = await ac.get(f"/api/v1/buckets/GetBucketLifecycleConfiguration/{bucket_name}")
        assert res.status_code == 501

        # 18. DeleteBucketLifecycle (Legacy 501)
        res = await ac.delete(f"/api/v1/buckets/DeleteBucketLifecycle/{bucket_name}")
        assert res.status_code == 501

        # 19. get-bucket-lifecycle
        res = await ac.get(f"/api/v1/buckets/get-bucket-lifecycle?bucketName={bucket_name}")
        assert res.status_code in [200, 404, 501, 503]

        # 20. remove-bucket-lifecycle
        res = await ac.delete(f"/api/v1/buckets/remove-bucket-lifecycle/{bucket_name}")
        assert res.status_code in [200, 404, 501, 503]

        # 21. PutBucketNotificationConfiguration (Legacy 501)
        res = await ac.put(f"/api/v1/buckets/PutBucketNotificationConfiguration/{bucket_name}")
        assert res.status_code == 501

        # 22. listen-bucket-notifications
        res = await ac.get(f"/api/v1/buckets/listen-bucket-notifications/{bucket_name}")
        assert res.status_code in [200, 404, 501, 503]

        # 23. remove-bucket
        res = await ac.request("DELETE", "/api/v1/buckets/remove-bucket", json={"bucket_name": bucket_name})
        assert res.status_code in [200, 404, 503]


@pytest.mark.asyncio
async def test_bucket_objects_apis():
    bucket_name = "test-bucket"
    object_name = "test_file.txt"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. list-objects
        res = await ac.post("/api/v1/buckets-objects/list-objects", json={"bucket_name": bucket_name})
        assert res.status_code in [200, 404, 503]

        # 2. file-uploader
        files = {"file": ("test.txt", b"Hello World content", "text/plain")}
        data = {"BucketName": bucket_name, "FolderName": "uploads"}
        res = await ac.post("/api/v1/buckets-objects/file-uploader", files=files, data=data)
        assert res.status_code in [200, 503]

        # 3. presigned-url
        res = await ac.get(f"/api/v1/buckets-objects/presigned-url/{bucket_name}/{object_name}")
        assert res.status_code in [200, 400, 404, 503]

        # 4. download
        res = await ac.get(f"/api/v1/buckets-objects/download/{bucket_name}/{object_name}")
        assert res.status_code in [200, 404, 503]

        # 5. download-by-path
        res = await ac.get(f"/api/v1/buckets-objects/download-by-path/{bucket_name}/{object_name}")
        assert res.status_code in [200, 404, 503]

        # 6. delete
        res = await ac.delete(f"/api/v1/buckets-objects/delete/{bucket_name}/{object_name}")
        assert res.status_code in [200, 404, 503]

        # 7. delete-object query
        res = await ac.delete(f"/api/v1/buckets-objects/delete-object?bucketName={bucket_name}&objectName={object_name}")
        assert res.status_code in [200, 404, 503]


@pytest.mark.asyncio
async def test_nas_apis():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. file-uploader
        files = {"file": ("test_nas.txt", b"NAS test content", "text/plain")}
        data = {"FolderName": "test_folder"}
        res = await ac.post("/api/v1/nas/file-uploader", files=files, data=data)
        assert res.status_code in [200, 400, 503]

        # 2. course-term-cover-upload
        files_cover = {"file": ("cover.jpg", b"fake image bytes", "image/jpeg")}
        res = await ac.post("/api/v1/nas/course-term-cover-upload/file_123", files=files_cover)
        assert res.status_code in [200, 400, 503]
