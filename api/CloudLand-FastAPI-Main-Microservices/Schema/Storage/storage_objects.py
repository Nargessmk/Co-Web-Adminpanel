from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class MakeBucketRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bucket_name: Optional[str] = Field(default=None, alias="bucketName")
    location: Optional[str] = Field(default=None)


class ListObjectsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bucket_name: Optional[str] = Field(default=None, alias="BucketName")
    recursive: bool = Field(default=False, alias="Recursive")
    versioning: bool = Field(default=False, alias="Versioning")
    prefix: Optional[str] = Field(default=None, alias="Prefix")
    list_object_v1: bool = Field(default=False, alias="ListObjectV1")


class SetVersionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bucket_name: Optional[str] = Field(default=None, alias="BucketName")
    enabled: bool = Field(default=True, alias="Enabled")


class BucketEncryptionRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bucket_name: Optional[str] = Field(default=None, alias="BucketName")


class SetBucketTagsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bucket_name: Optional[str] = Field(default=None, alias="BucketName")
    tags: Optional[Dict[str, str]] = Field(default=None)
    is_object: bool = Field(default=False, alias="IsObject")


class SetBucketLifecycleRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bucket_name: Optional[str] = Field(default=None, alias="BucketName")
    expire_date: datetime = Field(..., alias="ExpireDate")
    is_delete_marker: bool = Field(default=False, alias="IsDeleteMaker")


class RemoveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bucket_name: Optional[str] = Field(default=None, alias="BucketName")
    object_name: Optional[str] = Field(default=None, alias="ObjectName")


class SetBucketNotificationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bucket_name: Optional[str] = Field(default=None, alias="BucketName")
