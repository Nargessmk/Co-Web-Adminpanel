from typing import Optional
from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field


class FileUploaderRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bucket_name: Optional[str] = Field(default=None, alias="BucketName")
    folder_name: Optional[str] = Field(default=None, alias="FolderName")
    file_name: Optional[str] = Field(default=None, alias="FileName")
    ignore_default_path: bool = Field(default=False, alias="IgnoreDefaultPath")

    @classmethod
    def as_form(
        cls,
        bucket_name: Optional[str] = Form(None, alias="BucketName"),
        folder_name: Optional[str] = Form(None, alias="FolderName"),
        file_name: Optional[str] = Form(None, alias="FileName"),
        ignore_default_path: bool = Form(False, alias="IgnoreDefaultPath"),
    ) -> "FileUploaderRequest":
        return cls(
            bucket_name=bucket_name,
            folder_name=folder_name,
            file_name=file_name,
            ignore_default_path=ignore_default_path,
        )
