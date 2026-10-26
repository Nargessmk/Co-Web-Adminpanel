from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, delete, or_

from api.dependencies import CurrentUser, get_uow, require_tenant
from Models.entity_file_attachment import EntityFileAttachment
from Schema.AppManagement.entity_file_attachment import (
    EntityFileAttachmentCreateDTO,
    EntityFileAttachmentDTO,
    EntityFileAttachmentUpdateDTO,
)
from Structure.session import UnitOfWork

router = APIRouter()


@router.get("", response_model=List[EntityFileAttachmentDTO])
async def list_file_attachments(
    record_id: Optional[UUID] = Query(None, alias="recordId", description="Filter by attached record ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    uow: UnitOfWork = Depends(get_uow),
):
    application_id, current_user = tenant
    if record_id and record_id == application_id:
        stmt = select(EntityFileAttachment).where(
            or_(
                EntityFileAttachment.application_id == application_id,
                EntityFileAttachment.record_id == application_id,
            )
        )
    elif record_id:
        stmt = select(EntityFileAttachment).where(
            or_(
                EntityFileAttachment.application_id == application_id,
                EntityFileAttachment.application_id.is_(None),
            ),
            or_(
                EntityFileAttachment.record_id == record_id,
                EntityFileAttachment.application_id == record_id,
            ),
        )
    else:
        stmt = select(EntityFileAttachment).where(
            or_(
                EntityFileAttachment.application_id == application_id,
                EntityFileAttachment.record_id == application_id,
            )
        )

    stmt = stmt.order_by(EntityFileAttachment.last_modified_at.desc(), EntityFileAttachment.create_at.desc()).offset(skip).limit(limit)
    res = await uow.session.execute(stmt)
    attachments = res.scalars().all()
    return [EntityFileAttachmentDTO.model_validate(item) for item in attachments]


@router.get("/by-record/{record_id}", response_model=List[EntityFileAttachmentDTO])
async def get_file_attachments_by_record_id(
    record_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    uow: UnitOfWork = Depends(get_uow),
):
    application_id, current_user = tenant
    stmt = (
        select(EntityFileAttachment)
        .where(
            or_(
                EntityFileAttachment.application_id == application_id,
                EntityFileAttachment.record_id == application_id,
                EntityFileAttachment.application_id.is_(None),
            ),
            or_(
                EntityFileAttachment.record_id == record_id,
                EntityFileAttachment.application_id == record_id,
            ),
        )
        .order_by(EntityFileAttachment.last_modified_at.desc(), EntityFileAttachment.create_at.desc())
        .offset(skip)
        .limit(limit)
    )
    res = await uow.session.execute(stmt)
    attachments = res.scalars().all()
    return [EntityFileAttachmentDTO.model_validate(item) for item in attachments]


@router.get("/by-record/{record_id}/single", response_model=EntityFileAttachmentDTO)
async def get_single_file_attachment_by_record_id(
    record_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    uow: UnitOfWork = Depends(get_uow),
):
    application_id, current_user = tenant
    stmt = (
        select(EntityFileAttachment)
        .where(
            or_(
                EntityFileAttachment.application_id == application_id,
                EntityFileAttachment.record_id == application_id,
                EntityFileAttachment.application_id.is_(None),
            ),
            or_(
                EntityFileAttachment.record_id == record_id,
                EntityFileAttachment.application_id == record_id,
            ),
        )
        .order_by(EntityFileAttachment.last_modified_at.desc(), EntityFileAttachment.create_at.desc())
        .limit(1)
    )
    res = await uow.session.execute(stmt)
    attachment = res.scalar_one_or_none()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No file attachment found for record_id {record_id}",
        )
    return EntityFileAttachmentDTO.model_validate(attachment)


@router.put("/by-record/{record_id}", response_model=EntityFileAttachmentDTO)
async def upsert_file_attachment_by_record_id(
    record_id: UUID,
    dto: EntityFileAttachmentUpdateDTO,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    uow: UnitOfWork = Depends(get_uow),
):
    application_id, current_user = tenant
    stmt = (
        select(EntityFileAttachment)
        .where(
            or_(
                EntityFileAttachment.application_id == application_id,
                EntityFileAttachment.record_id == application_id,
                EntityFileAttachment.application_id.is_(None),
            ),
            or_(
                EntityFileAttachment.record_id == record_id,
                EntityFileAttachment.application_id == record_id,
            ),
        )
        .order_by(EntityFileAttachment.last_modified_at.desc(), EntityFileAttachment.create_at.desc())
    )
    res = await uow.session.execute(stmt)
    attachments = res.scalars().all()
    if not attachments:
        attachment = EntityFileAttachment(
            record_id=record_id or application_id,
            file_url=dto.file_url,
            file_extension=dto.file_extension,
            original_file_name=dto.original_file_name,
            file_size_in_bytes=dto.file_size_in_bytes or 0,
            title=dto.title or "لوگوی شرکت",
            desc=dto.desc or "default",
            user_created=current_user.user_id,
            last_modified_user=current_user.user_id,
            application_id=application_id or record_id,
        )
        created = await uow.entity_file_attachments.add(attachment)
        await uow.commit()
        return EntityFileAttachmentDTO.model_validate(created)

    primary = attachments[0]
    update_data = dto.model_dump(exclude_unset=True)
    now_utc = datetime.now(timezone.utc)
    for att in attachments:
        for field, val in update_data.items():
            if field == "file_url" and val is None and att.file_url is not None:
                continue
            setattr(att, field, val)
        att.last_modified_user = current_user.user_id
        att.last_modified_at = now_utc
        await uow.entity_file_attachments.update(att)

    await uow.commit()
    return EntityFileAttachmentDTO.model_validate(primary)


@router.delete("/by-record/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_attachments_by_record_id(
    record_id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    uow: UnitOfWork = Depends(get_uow),
):
    application_id, current_user = tenant
    stmt = delete(EntityFileAttachment).where(
        EntityFileAttachment.application_id == application_id,
        EntityFileAttachment.record_id == record_id,
    )
    await uow.session.execute(stmt)
    await uow.commit()


@router.get("/{id}", response_model=EntityFileAttachmentDTO)
async def get_file_attachment(
    id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    uow: UnitOfWork = Depends(get_uow),
):
    application_id, current_user = tenant
    attachment = await uow.entity_file_attachments.find(id)
    if not attachment or attachment.application_id != application_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File attachment not found")
    return EntityFileAttachmentDTO.model_validate(attachment)


@router.post("", response_model=EntityFileAttachmentDTO, status_code=status.HTTP_201_CREATED)
async def create_file_attachment(
    dto: EntityFileAttachmentCreateDTO,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    uow: UnitOfWork = Depends(get_uow),
):
    application_id, current_user = tenant
    attachment = EntityFileAttachment(
        record_id=dto.record_id,
        file_url=dto.file_url,
        file_extension=dto.file_extension,
        original_file_name=dto.original_file_name,
        file_size_in_bytes=dto.file_size_in_bytes,
        title=dto.title,
        desc=dto.desc,
        user_created=current_user.user_id,
        last_modified_user=current_user.user_id,
        application_id=application_id,
    )
    created = await uow.entity_file_attachments.add(attachment)
    await uow.commit()
    return EntityFileAttachmentDTO.model_validate(created)


@router.put("/{id}", response_model=EntityFileAttachmentDTO)
async def update_file_attachment(
    id: UUID,
    dto: EntityFileAttachmentUpdateDTO,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    uow: UnitOfWork = Depends(get_uow),
):
    application_id, current_user = tenant
    attachment = await uow.entity_file_attachments.find(id)
    if not attachment or attachment.application_id != application_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File attachment not found")

    update_data = dto.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(attachment, field, val)

    attachment.last_modified_user = current_user.user_id
    attachment.last_modified_at = datetime.now(timezone.utc)
    updated = await uow.entity_file_attachments.update(attachment)
    await uow.commit()
    return EntityFileAttachmentDTO.model_validate(updated)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_attachment(
    id: UUID,
    tenant: tuple[UUID, CurrentUser] = Depends(require_tenant),
    uow: UnitOfWork = Depends(get_uow),
):
    application_id, current_user = tenant
    attachment = await uow.entity_file_attachments.find(id)
    if not attachment or attachment.application_id != application_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File attachment not found")

    await uow.entity_file_attachments.delete(id)
    await uow.commit()
