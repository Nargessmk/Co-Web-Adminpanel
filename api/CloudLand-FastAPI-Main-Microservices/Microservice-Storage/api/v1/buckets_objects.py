import io
import logging
import os
import uuid
from typing import Any, Dict, List, Optional
from uuid import UUID
from urllib.parse import quote, unquote
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from Schema.Storage import FileUploadResponse, ListObjectsRequest
from api.dependencies import CurrentUser, require_tenant, require_user
from core.config import get_settings
from core.s3 import get_s3_client
from api.v1.buckets import _handle_s3_exception

router = APIRouter(prefix="/api/v1/buckets-objects", tags=["Bucket Objects"])
settings = get_settings()
logger = logging.getLogger("storage.buckets_objects")


def generate_object_name(folder_name: str, file_name: str) -> str:
    extension = os.path.splitext(file_name)[1]
    clean_folder_name = folder_name.strip("/") if folder_name and folder_name.strip() else "uploads"
    guid_name = uuid.uuid4().hex
    object_name = f"{clean_folder_name}/{guid_name}{extension}"
    return object_name.replace("//", "/")


async def ensure_bucket_exists(s3_client, bucket_name: str):
    try:
        await s3_client.head_bucket(Bucket=bucket_name)
    except Exception:
        try:
            await s3_client.create_bucket(Bucket=bucket_name)
        except Exception as e:
            logger.warning("Could not create bucket '%s': %s", bucket_name, str(e))


async def generate_presigned_url(s3_client, bucket_name: str, object_name: str, expiry_seconds: int = 86400) -> Optional[str]:
    try:
        url = await s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiry_seconds,
        )
        return url
    except Exception as e:
        logger.warning(f"Failed to generate presigned URL: {str(e)}")
        return None


@router.post("/list-objects", response_model=List[Dict[str, Any]])
async def list_objects(
    request: ListObjectsRequest,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    if not request.bucket_name:
        raise HTTPException(status_code=400, detail="Bucket name is required")
    bucket = request.bucket_name.lower()
    try:
        await s3_client.head_bucket(Bucket=bucket)
    except Exception as e:
        _handle_s3_exception(e, f"Error checking bucket {bucket}")

    kwargs: Dict[str, Any] = {"Bucket": bucket}
    if request.prefix:
        kwargs["Prefix"] = request.prefix

    try:
        if request.versioning:
            res = await s3_client.list_object_versions(**kwargs)
            versions = res.get("Versions", [])
            return [
                {
                    "Key": v.get("Key"),
                    "VersionId": v.get("VersionId"),
                    "Size": v.get("Size"),
                    "LastModified": v.get("LastModified"),
                    "ETag": v.get("ETag"),
                }
                for v in versions
            ]
        else:
            res = await s3_client.list_objects_v2(**kwargs)
            contents = res.get("Contents", [])
            return [
                {
                    "Key": c.get("Key"),
                    "Size": c.get("Size"),
                    "LastModified": c.get("LastModified"),
                    "ETag": c.get("ETag"),
                }
                for c in contents
            ]
    except Exception as e:
        _handle_s3_exception(e, f"Error listing objects in {bucket}")


@router.get("/download-by-path/{storage_path:path}")
async def download_by_path(
    storage_path: str,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    if not storage_path or "/" not in storage_path:
        raise HTTPException(status_code=400, detail="Invalid storage path format. Expected: bucketName/objectPath")

    parts = storage_path.split("/", 1)
    bucket_name = parts[0].lower()
    object_name = parts[1]

    try:
        stat = await s3_client.head_object(Bucket=bucket_name, Key=object_name)
        content_type = stat.get("ContentType", "application/octet-stream")
        metadata = stat.get("Metadata", {})
        original_filename = unquote(metadata.get("original-filename", os.path.basename(object_name)))

        response = await s3_client.get_object(Bucket=bucket_name, Key=object_name)
        body = response["Body"]

        return StreamingResponse(
            body,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{original_filename}"'
            },
        )
    except Exception as e:
        _handle_s3_exception(e, f"Error downloading path {storage_path}")


@router.post("/file-uploader", response_model=FileUploadResponse)
async def file_uploader(
    request: Request,
    file: Optional[UploadFile] = File(None),
    folder_name: Optional[str] = Form(None, alias="FolderName"),
    record_id: Optional[str] = Form(None, alias="RecordId"),
    user_id: Optional[str] = Form(None, alias="UserId"),
    application_id: Optional[str] = Form(None, alias="ApplicationId"),
    title: Optional[str] = Form(None, alias="Title"),
    desc: Optional[str] = Form(None, alias="Desc"),
    current_user: CurrentUser = Depends(require_user),
    s3_client=Depends(get_s3_client),
):
    form_data = await request.form()

    effective_file = file
    if not effective_file:
        raw_file = form_data.get("file") or form_data.get("File")
        if isinstance(raw_file, UploadFile):
            effective_file = raw_file

    if not effective_file or not effective_file.filename:
        return FileUploadResponse(success=False, error_message="No file provided or file is empty")

    file = effective_file

    req_folder_name = (
        folder_name
        or form_data.get("folder_name")
        or form_data.get("FolderName")
        or form_data.get("folderName")
    )
    if not req_folder_name:
        return FileUploadResponse(success=False, error_message="FolderName is required")

    req_record_id = (
        record_id
        or form_data.get("record_id")
        or form_data.get("recordId")
        or form_data.get("RecordId")
    )
    req_user_id = (
        user_id
        or form_data.get("user_id")
        or form_data.get("userId")
        or form_data.get("UserId")
        or form_data.get("user_created")
        or form_data.get("userCreated")
        or form_data.get("UserCreated")
    )
    req_app_id = (
        application_id
        or form_data.get("application_id")
        or form_data.get("applicationId")
        or form_data.get("ApplicationId")
        or form_data.get("app_id")
        or form_data.get("appId")
        or form_data.get("AppId")
    )
    req_title = (
        title
        or form_data.get("title")
        or form_data.get("Title")
    )
    req_desc = (
        desc
        or form_data.get("desc")
        or form_data.get("Desc")
        or form_data.get("description")
        or form_data.get("Description")
    )

    eff_app_id = req_app_id or (str(current_user.app_id) if current_user and current_user.app_id else None)
    if eff_app_id is not None:
        try:
            eff_app_uuid = UUID(eff_app_id)
        except (ValueError, TypeError):
            eff_app_uuid = None
        if eff_app_uuid and eff_app_uuid != current_user.app_id:
            if "admin" not in current_user.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: application_id does not match authenticated tenant",
                )

    bucket = settings.s3_bucket.lower()
    await ensure_bucket_exists(s3_client, bucket)

    folder_str = req_folder_name.strip() if isinstance(req_folder_name, str) else req_folder_name
    object_name = generate_object_name(folder_str, file.filename)

    file_size = file.size or 0
    file_extension = os.path.splitext(file.filename)[1] or ""
    content_type = file.content_type or "application/octet-stream"

    try:
        file.file.seek(0)
        await s3_client.upload_fileobj(
            Fileobj=file.file,
            Bucket=bucket,
            Key=object_name,
            ExtraArgs={
                "ContentType": content_type,
                "Metadata": {"original-filename": quote(file.filename, safe="")},
            },
        )

        presigned_url = await generate_presigned_url(s3_client, bucket, object_name, expiry_seconds=86400)

        endpoint_clean = settings.s3_endpoint.rstrip("/")
        direct_url = f"{endpoint_clean}/{bucket}/{object_name}"
        api_download_url = f"/api/v1/buckets-objects/download/{bucket}/{object_name}"
        file_url = api_download_url

        etag = ""
        last_modified = None
        warning = None
        try:
            stat = await s3_client.head_object(Bucket=bucket, Key=object_name)
            etag = stat.get("ETag", "").strip('"')
            last_modified = stat.get("LastModified")
        except Exception:
            warning = "Could not retrieve full metadata"

        try:
            from services.message_bus import get_storage_message_bus
            msg_bus = get_storage_message_bus()

            str_record_id = str(req_record_id) if req_record_id else None
            str_title = str(req_title) if req_title else None
            str_desc = str(req_desc) if req_desc else None

            await msg_bus.publish_file_uploaded(
                record_id=str_record_id,
                file_url=file_url,
                file_extension=file_extension,
                original_file_name=file.filename,
                file_size_in_bytes=file_size,
                user_id=str(req_user_id) if req_user_id else None,
                application_id=eff_app_id,
                title=str_title or file.filename,
                desc=str_desc,
            )
        except Exception as rmq_exc:
            logger.warning("RabbitMQ event publish failed: %s", rmq_exc)

        return FileUploadResponse(
            success=True,
            message="File uploaded successfully",
            object_name=object_name,
            bucket_name=bucket,
            original_file_name=file.filename,
            file_size=file_size,
            content_type=content_type,
            etag=etag,
            last_modified=last_modified,
            direct_url=direct_url,
            presigned_url=presigned_url,
            download_url=api_download_url,
            storage_path=f"{bucket}/{object_name}",
            file_identifier=object_name,
            file_url=file_url,
            warning=warning,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        return FileUploadResponse(success=False, message="Upload failed", error_message=str(e))


@router.get("/download/{bucket_name}/{object_name:path}")
async def download_file(
    bucket_name: str,
    object_name: str,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    try:
        stat = await s3_client.head_object(Bucket=bucket, Key=object_name)
        content_type = stat.get("ContentType", "application/octet-stream")
        metadata = stat.get("Metadata", {})
        original_filename = unquote(metadata.get("original-filename", os.path.basename(object_name)))

        response = await s3_client.get_object(Bucket=bucket, Key=object_name)
        body = response["Body"]

        return StreamingResponse(
            body,
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{original_filename}"'
            },
        )
    except Exception as e:
        _handle_s3_exception(e, f"Error downloading file {object_name} from {bucket}")


@router.get("/presigned-url/{bucket_name}/{object_name:path}")
async def get_presigned_url(
    bucket_name: str,
    object_name: str,
    expiry_seconds: int = Query(3600, alias="expirySeconds"),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    url = await generate_presigned_url(s3_client, bucket, object_name, expiry_seconds)
    if not url:
        raise HTTPException(status_code=400, detail="Failed to generate URL")
    return {"url": url}


async def _delete_object(bucket: str, object_name: str, record_id: str | None, s3_client) -> dict:
    try:
        await s3_client.delete_object(Bucket=bucket, Key=object_name)
    except Exception as e:
        _handle_s3_exception(e, f"Failed to delete object {object_name} from S3")

    endpoint_clean = settings.s3_endpoint.rstrip("/")
    direct_url = f"{endpoint_clean}/{bucket}/{object_name}"
    api_download_url = f"/api/v1/buckets-objects/download/{bucket}/{object_name}"
    file_url = api_download_url

    try:
        from services.message_bus import get_storage_message_bus
        msg_bus = get_storage_message_bus()
        await msg_bus.publish_file_deleted(file_url=file_url, record_id=record_id)
    except Exception as rmq_exc:
        logger.warning("RabbitMQ delete publish event failed: %s", rmq_exc)

    return {"message": "File deleted successfully", "bucket": bucket, "object_name": object_name}


@router.delete("/delete/{bucket_name}/{object_name:path}")
async def delete_file(
    bucket_name: str,
    object_name: str,
    record_id: Optional[str] = Query(None, alias="recordId"),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    return await _delete_object(bucket, object_name, record_id, s3_client)


@router.delete("/delete-object")
async def delete_object_query(
    bucket_name: str = Query(..., alias="bucketName"),
    object_name: str = Query(..., alias="objectName"),
    record_id: Optional[str] = Query(None, alias="recordId"),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    return await _delete_object(bucket, object_name, record_id, s3_client)
