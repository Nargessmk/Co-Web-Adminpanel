import os
import uuid
from typing import Optional
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Query, UploadFile, status
from uuid import UUID
from api.dependencies import CurrentUser, require_tenant
from core.config import get_settings
from core.sftp import upload_file_to_nas

router = APIRouter(prefix="/api/v1/nas", tags=["NAS"])
settings = get_settings()


@router.post("/file-uploader", status_code=status.HTTP_200_OK)
async def file_uploader(
    file: UploadFile = File(...),
    folder_name: Optional[str] = Form(None, alias="FolderName"),
    file_name: Optional[str] = Form(None, alias="FileName"),
    ignore_default_path: bool = Form(False, alias="IgnoreDefaultPath"),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    if not folder_name:
        raise HTTPException(status_code=400, detail="FolderName is required")

    default_path = "" if ignore_default_path else settings.sftp_default_path
    remote_dir = f"{default_path}{folder_name.lower()}"

    extension = os.path.splitext(file.filename or "")[1]
    final_filename = file_name if file_name else f"{uuid.uuid4()}{extension}"

    try:
        file.file.seek(0)
        target_path = await upload_file_to_nas(file.file, remote_dir, final_filename)
        return {"message": "File uploaded successfully to NAS", "path": target_path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"NAS Upload failed: {str(e)}")


@router.post("/course-term-cover-upload/{file_id}", status_code=status.HTTP_200_OK)
async def course_term_cover_upload(
    file_id: str,
    file: UploadFile = File(...),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
):
    application_id, current_user = tenant
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided in request")

    extension = os.path.splitext(file.filename or "")[1]
    final_filename = f"{file_id}{extension}"
    remote_dir = settings.sftp_default_cover_path

    try:
        file.file.seek(0)
        target_path = await upload_file_to_nas(file.file, remote_dir, final_filename)
        return {"message": "Cover uploaded successfully", "path": target_path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"NAS Cover Upload failed: {str(e)}")
