from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FileUploadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool = True
    message: Optional[str] = None

    # File information
    object_name: Optional[str] = Field(default=None, alias="ObjectName")
    bucket_name: Optional[str] = Field(default=None, alias="BucketName")
    original_file_name: Optional[str] = Field(default=None, alias="OriginalFileName")
    file_size: Optional[int] = Field(default=None, alias="FileSize")
    content_type: Optional[str] = Field(default=None, alias="ContentType")
    etag: Optional[str] = Field(default=None, alias="ETag")
    last_modified: Optional[datetime] = Field(default=None, alias="LastModified")

    # Storage metadata
    storage_path: Optional[str] = Field(default=None, alias="StoragePath")
    file_identifier: Optional[str] = Field(default=None, alias="FileIdentifier")

    # Access URLs
    direct_url: Optional[str] = Field(default=None, alias="DirectUrl")
    presigned_url: Optional[str] = Field(default=None, alias="PresignedUrl")
    download_url: Optional[str] = Field(default=None, alias="DownloadUrl")
    thumbnail_url: Optional[str] = Field(default=None, alias="ThumbnailUrl")
    preview_url: Optional[str] = Field(default=None, alias="PreviewUrl")
    file_url: Optional[str] = Field(default=None, alias="FileUrl")

    # Error / Warning
    error_message: Optional[str] = Field(default=None, alias="ErrorMessage")
    warning: Optional[str] = Field(default=None, alias="Warning")
