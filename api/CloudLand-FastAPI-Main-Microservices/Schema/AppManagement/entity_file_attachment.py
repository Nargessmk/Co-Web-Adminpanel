from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel as PydanticBaseModel, ConfigDict, Field


class EntityFileAttachmentDTO(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID = Field(..., alias="Id")
    record_id: Optional[UUID] = Field(None, alias="RecordId")
    file_url: Optional[str] = Field(None, alias="FileUrl")
    file_extension: Optional[str] = Field(None, alias="FileExtension")
    original_file_name: Optional[str] = Field(None, alias="OriginalFileName")
    file_size_in_bytes: int = Field(0, alias="FileSizeInBytes")
    
    title: Optional[str] = Field(None, alias="Title")
    desc: Optional[str] = Field(None, alias="Desc")
    create_at: Optional[datetime] = Field(None, alias="CreateAt")
    last_modified_at: Optional[datetime] = Field(None, alias="LastModifiedAt")
    user_created: Optional[UUID] = Field(None, alias="UserCreated")
    last_modified_user: Optional[UUID] = Field(None, alias="LastModifiedUser")
    application_id: Optional[UUID] = Field(None, alias="ApplicationId")
    allow_delete: bool = Field(True, alias="AllowDelete")
    allow_update: bool = Field(True, alias="AllowUpdate")
    disabled: bool = Field(False, alias="Disabled")
    hidden: bool = Field(False, alias="Hidden")
    version: int = Field(1, alias="Version")


class EntityFileAttachmentCreateDTO(PydanticBaseModel):
    model_config = ConfigDict(populate_by_name=True)

    record_id: Optional[UUID] = Field(None, alias="RecordId")
    file_url: Optional[str] = Field(None, alias="FileUrl")
    file_extension: Optional[str] = Field(None, alias="FileExtension")
    original_file_name: Optional[str] = Field(None, alias="OriginalFileName")
    file_size_in_bytes: int = Field(0, alias="FileSizeInBytes")
    title: Optional[str] = Field(None, alias="Title")
    desc: Optional[str] = Field(None, alias="Desc")


class EntityFileAttachmentUpdateDTO(PydanticBaseModel):
    model_config = ConfigDict(populate_by_name=True)

    record_id: Optional[UUID] = Field(None, alias="RecordId")
    file_url: Optional[str] = Field(None, alias="FileUrl")
    file_extension: Optional[str] = Field(None, alias="FileExtension")
    original_file_name: Optional[str] = Field(None, alias="OriginalFileName")
    file_size_in_bytes: Optional[int] = Field(None, alias="FileSizeInBytes")
    title: Optional[str] = Field(None, alias="Title")
    desc: Optional[str] = Field(None, alias="Desc")
    disabled: Optional[bool] = Field(None, alias="Disabled")
    hidden: Optional[bool] = Field(None, alias="Hidden")
