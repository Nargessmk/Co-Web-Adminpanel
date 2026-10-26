import logging
from typing import Any, Dict, List
from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from uuid import UUID

from Schema.Storage import (
    BucketEncryptionRequest,
    MakeBucketRequest,
    SetBucketLifecycleRequest,
    SetBucketTagsRequest,
    SetVersionRequest,
)
from api.dependencies import CurrentUser, require_tenant
from core.s3 import get_s3_client

logger = logging.getLogger("storage.buckets")

router = APIRouter(prefix="/api/v1/buckets", tags=["Buckets"])


def _clean_s3_response(response: dict) -> dict:
    if isinstance(response, dict):
        response.pop("ResponseMetadata", None)
    return response


def _handle_s3_exception(e: Exception, fallback_msg: str = "S3 operation error"):
    error_msg = str(e)
    if "must be made to API port" in error_msg or "InvalidArgument" in error_msg:
        raise HTTPException(
            status_code=400,
            detail="S3 API Requests must be made to API port (port 9000). Nginx on s3.ailand.ai is currently proxying to MinIO Web Console (port 9001).",
        )
    if isinstance(e, ClientError):
        error_code = e.response.get("Error", {}).get("Code", "")
        msg = e.response.get("Error", {}).get("Message", str(e))
        if error_code in [
            "404",
            "NoSuchBucket",
            "NoSuchKey",
            "NotFound",
            "NoSuchTagSet",
            "NoSuchBucketTagging",
            "NoSuchLifecycleConfiguration",
            "ServerSideEncryptionConfigurationNotFoundError",
        ]:
            raise HTTPException(status_code=404, detail=msg or "Resource not found")
        if error_code in ["NotImplemented", "501"]:
            raise HTTPException(status_code=501, detail="Feature not supported by S3 server")
        raise HTTPException(status_code=400, detail=msg)
    logger.error(f"{fallback_msg}: {error_msg}")
    raise HTTPException(status_code=503, detail=f"S3 Storage connection error: {error_msg}")


async def _check_bucket_exists(s3_client, bucket_name: str):
    try:
        await s3_client.head_bucket(Bucket=bucket_name.lower())
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code in ["404", "NoSuchBucket", "NotFound"]:
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found")
        _handle_s3_exception(e, f"Error checking bucket {bucket_name}")
    except Exception as e:
        _handle_s3_exception(e, f"Error checking bucket {bucket_name}")


@router.get("/list-buckets", response_model=List[Dict[str, Any]])
async def list_buckets(
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    try:
        response = await s3_client.list_buckets()
        buckets = response.get("Buckets", [])
        return [{"Name": b.get("Name"), "CreationDate": b.get("CreationDate")} for b in buckets]
    except Exception as e:
        _handle_s3_exception(e, "Error in list_buckets")


@router.post("/make-bucket", status_code=status.HTTP_200_OK)
async def make_bucket(
    request: MakeBucketRequest,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    if not request.bucket_name:
        raise HTTPException(status_code=400, detail="Bucket name is required")

    bucket_name = request.bucket_name.lower()

    try:
        await s3_client.head_bucket(Bucket=bucket_name)
        raise HTTPException(status_code=400, detail="Bucket already exists")
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code not in ["404", "NoSuchBucket", "NotFound"]:
            _handle_s3_exception(e, "Error checking bucket existence")
    except Exception as e:
        _handle_s3_exception(e, "Error checking bucket existence")

    try:
        create_kwargs: Dict[str, Any] = {"Bucket": bucket_name}
        if request.location:
            create_kwargs["CreateBucketConfiguration"] = {"LocationConstraint": request.location}
        await s3_client.create_bucket(**create_kwargs)
        return {"message": "Bucket created successfully"}
    except Exception as e:
        _handle_s3_exception(e, "Error making bucket")


@router.get("/is-exist-bucket/{bucket_name}")
async def is_exist_bucket(
    bucket_name: str,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    try:
        await s3_client.head_bucket(Bucket=bucket_name.lower())
        return True
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code in ["404", "NoSuchBucket", "NotFound"]:
            return False
        _handle_s3_exception(e, f"Error checking is_exist_bucket for {bucket_name}")
    except Exception as e:
        _handle_s3_exception(e, f"Error checking is_exist_bucket for {bucket_name}")


@router.delete("/remove-bucket")
async def remove_bucket(
    request: MakeBucketRequest,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    if not request.bucket_name:
        raise HTTPException(status_code=400, detail="Bucket name is required")

    bucket_name = request.bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket_name)

    try:
        await s3_client.delete_bucket(Bucket=bucket_name)
        return True
    except Exception as e:
        _handle_s3_exception(e, f"Error removing bucket {bucket_name}")


@router.post("/set-version")
async def set_version(
    request: SetVersionRequest,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    if not request.bucket_name:
        raise HTTPException(status_code=400, detail="Bucket name is required")
    bucket_name = request.bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket_name)

    status_str = "Enabled" if request.enabled else "Suspended"
    try:
        await s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={"Status": status_str},
        )
        return {"message": f"Versioning set to {status_str}"}
    except Exception as e:
        _handle_s3_exception(e, f"Error setting versioning for {bucket_name}")


@router.get("/get-version/{bucket_name}")
async def get_version(
    bucket_name: str,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    try:
        res = await s3_client.get_bucket_versioning(Bucket=bucket)
        return _clean_s3_response(res)
    except Exception as e:
        _handle_s3_exception(e, f"Error getting version for {bucket}")


@router.post("/set-bucket-encryption")
async def set_bucket_encryption(
    request: BucketEncryptionRequest,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    if not request.bucket_name:
        raise HTTPException(status_code=400, detail="Bucket name is required")
    bucket = request.bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    try:
        await s3_client.put_bucket_encryption(
            Bucket=bucket,
            ServerSideEncryptionConfiguration={
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            },
        )
        return {"message": "Encryption set"}
    except Exception as e:
        _handle_s3_exception(e, f"Error setting encryption for {bucket}")


@router.put("/PutBucketEncryption/{bucket_name}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def put_bucket_encryption(bucket_name: str, tenant: tuple[UUID, CurrentUser] = Depends(require_tenant)):
    application_id, current_user = tenant
    raise HTTPException(status_code=501, detail="Bucket Encryption not implemented in MinIO S3 Server")


@router.get("/GetBucketEncryption/{bucket_name}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_bucket_encryption_legacy(bucket_name: str, tenant: tuple[UUID, CurrentUser] = Depends(require_tenant)):
    application_id, current_user = tenant
    raise HTTPException(status_code=501, detail="Bucket Encryption not implemented in MinIO S3 Server")


@router.delete("/DeleteBucketEncryption/{bucket_name}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def delete_bucket_encryption_legacy(bucket_name: str, tenant: tuple[UUID, CurrentUser] = Depends(require_tenant)):
    application_id, current_user = tenant
    raise HTTPException(status_code=501, detail="Bucket Encryption removal not implemented in MinIO S3 Server")


@router.get("/get-bucket-encryption/{bucket_name}")
async def get_bucket_encryption(
    bucket_name: str,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    try:
        res = await s3_client.get_bucket_encryption(Bucket=bucket)
        return _clean_s3_response(res)
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code in ["ServerSideEncryptionConfigurationNotFoundError"]:
            return {}
        _handle_s3_exception(e, f"Error getting encryption for {bucket}")
    except Exception as e:
        _handle_s3_exception(e, f"Error getting encryption for {bucket}")


@router.delete("/remove-bucket-encryption")
async def remove_bucket_encryption(
    bucket_name: str = Query(..., alias="bucketName"),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    try:
        await s3_client.delete_bucket_encryption(Bucket=bucket)
        return {"message": "Encryption removed"}
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code in ["ServerSideEncryptionConfigurationNotFoundError"]:
            return {"message": "Encryption removed"}
        _handle_s3_exception(e, f"Error removing encryption for {bucket}")
    except Exception as e:
        _handle_s3_exception(e, f"Error removing encryption for {bucket}")


@router.post("/set-bucket-tags")
async def set_bucket_tags(
    request: SetBucketTagsRequest,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    if not request.bucket_name:
        raise HTTPException(status_code=400, detail="Bucket name is required")
    bucket = request.bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    tags_list = [{"Key": k, "Value": v} for k, v in (request.tags or {}).items()]
    try:
        await s3_client.put_bucket_tagging(
            Bucket=bucket,
            Tagging={"TagSet": tags_list},
        )
        return {"message": "Tags set successfully"}
    except Exception as e:
        _handle_s3_exception(e, f"Error setting tags for {bucket}")


@router.get("/get-bucket-tags/{bucket_name}")
async def get_bucket_tags(
    bucket_name: str,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    try:
        res = await s3_client.get_bucket_tagging(Bucket=bucket)
        return res.get("TagSet", [])
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code in ["NoSuchTagSet", "NoSuchBucketTagging"]:
            return []
        _handle_s3_exception(e, f"Error getting tags for {bucket}")
    except Exception as e:
        _handle_s3_exception(e, f"Error getting tags for {bucket}")


@router.delete("/remove-bucket-tags/{bucket_name}")
async def remove_bucket_tags(
    bucket_name: str,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    try:
        await s3_client.delete_bucket_tagging(Bucket=bucket)
        return {"message": "Tags removed"}
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code in ["NoSuchTagSet", "NoSuchBucketTagging"]:
            return {"message": "Tags removed"}
        _handle_s3_exception(e, f"Error removing tags for {bucket}")
    except Exception as e:
        _handle_s3_exception(e, f"Error removing tags for {bucket}")


@router.post("/set-bucket-lifecycle")
async def set_bucket_lifecycle(
    request: SetBucketLifecycleRequest,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    if not request.bucket_name:
        raise HTTPException(status_code=400, detail="Bucket name is required")
    bucket = request.bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    rule = {
        "Status": "Enabled",
        "Expiration": {"Date": request.expire_date.isoformat()},
        "ID": "Rule1",
        "Prefix": "",
    }
    try:
        await s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket,
            LifecycleConfiguration={"Rules": [rule]},
        )
        return {"message": "Lifecycle set successfully"}
    except Exception as e:
        _handle_s3_exception(e, f"Error setting lifecycle for {bucket}")


@router.put("/PutBucketLifecycleConfiguration/{bucket_name}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def put_bucket_lifecycle(bucket_name: str, tenant: tuple[UUID, CurrentUser] = Depends(require_tenant)):
    application_id, current_user = tenant
    raise HTTPException(status_code=501, detail="Lifecycle rules not supported in MinIO S3 Server")


@router.get("/GetBucketLifecycleConfiguration/{bucket_name}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def get_bucket_lifecycle_legacy(bucket_name: str, tenant: tuple[UUID, CurrentUser] = Depends(require_tenant)):
    application_id, current_user = tenant
    raise HTTPException(status_code=501, detail="Lifecycle rules not supported in MinIO S3 Server")


@router.delete("/DeleteBucketLifecycle/{bucket_name}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def delete_bucket_lifecycle_legacy(bucket_name: str, tenant: tuple[UUID, CurrentUser] = Depends(require_tenant)):
    application_id, current_user = tenant
    raise HTTPException(status_code=501, detail="Lifecycle rules not supported in MinIO S3 Server")


@router.get("/get-bucket-lifecycle")
async def get_bucket_lifecycle(
    bucket_name: str = Query(..., alias="bucketName"),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    try:
        res = await s3_client.get_bucket_lifecycle_configuration(Bucket=bucket)
        return _clean_s3_response(res)
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code in ["NoSuchLifecycleConfiguration"]:
            return {"Rules": []}
        _handle_s3_exception(e, f"Error getting lifecycle for {bucket}")
    except Exception as e:
        _handle_s3_exception(e, f"Error getting lifecycle for {bucket}")


@router.delete("/remove-bucket-lifecycle/{bucket_name}")
async def remove_bucket_lifecycle(
    bucket_name: str,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    try:
        await s3_client.delete_bucket_lifecycle(Bucket=bucket)
        return {"message": "Lifecycle removed"}
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code in ["NoSuchLifecycleConfiguration"]:
            return {"message": "Lifecycle removed"}
        _handle_s3_exception(e, f"Error removing lifecycle for {bucket}")
    except Exception as e:
        _handle_s3_exception(e, f"Error removing lifecycle for {bucket}")


@router.put("/PutBucketNotificationConfiguration/{bucket_name}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def put_bucket_notification(bucket_name: str, tenant: tuple[UUID, CurrentUser] = Depends(require_tenant)):
    application_id, current_user = tenant
    raise HTTPException(status_code=501, detail="Bucket notifications not supported in MinIO S3 Server")


@router.get("/listen-bucket-notifications/{bucket_name}")
async def listen_bucket_notifications(
    bucket_name: str,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    s3_client=Depends(get_s3_client),
):
    application_id, current_user = tenant
    bucket = bucket_name.lower()
    await _check_bucket_exists(s3_client, bucket)

    try:
        res = await s3_client.get_bucket_notification_configuration(Bucket=bucket)
        return _clean_s3_response(res)
    except Exception as e:
        _handle_s3_exception(e, f"Error getting notifications for {bucket}")
