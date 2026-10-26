"""Team members: public list + admin CRUD (with optional image upload)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response

from .. import db, storage
from ..errors import ApiError
from ..helpers import extract_file, optional_bool, read_body, to_int
from ..responses import failure, success
from ..resume_pdf import ResumePdfError, build_resume_pdf, resume_filename
from ..security import AdminContext, require_admin

logger = logging.getLogger("cloudland.team_members")

router = APIRouter(prefix="/api/team-members", tags=["Team members"])

LIST_COLUMNS = (
    "id, full_name, full_name_en, role, role_en, linkedin_url, github_url, "
    "website_url, resume_en, resume_fa, resume_template, image_url, avatar_icon, "
    "sort_order, is_active, created_at, updated_at"
)


def _avatar_icon(value) -> str | None:
    """Normalise the chosen icon name.

    A Material Icons ligature is a single lowercase word, so anything else is
    rejected and stored as NULL — the About page then falls back to the icon it
    assigns by position. Blank means "no choice", which is how the admin clears
    the selection, so it is stored as NULL rather than an empty string.

    The length guard matters: `avatar_icon` is VARCHAR(64), and an over-long
    value would otherwise abort the INSERT/UPDATE with a database error
    instead of being quietly ignored.
    """
    name = str(value or "").strip().lower()
    if not name or len(name) > 64:
        return None
    return name if name.replace("_", "").isalnum() else None


def localized(member: dict, field: str, lang: str) -> str:
    """The ``field`` value that belongs on a résumé in ``lang``.

    The English résumé uses the ``*_en`` spelling of the name and the job title
    and the Persian one uses the original, so an English PDF never shows a
    Persian name or role. Rows created before those columns existed fall back to
    the original rather than rendering an empty heading.
    """
    if lang == "en":
        return str(member.get(f"{field}_en") or member.get(field) or "").strip()
    return str(member.get(field) or "").strip()

# Résumé layout templates the admin can choose from. 'classic' is the
# GitHub-style single column and the default for every existing member.
RESUME_TEMPLATES = ("classic", "modern", "compact")


def _resume_template(value) -> str:
    """Normalise the template name, falling back to the default."""
    name = str(value or "").strip().lower()
    return name if name in RESUME_TEMPLATES else "classic"


async def _store_image(body: dict, files: dict, admin: AdminContext) -> None:
    """Upload the optional ``image`` field and put its URL into the payload."""
    upload = await extract_file(files, "image")
    if upload is None:
        return
    stored = await storage.upload_file(
        buffer=upload.buffer,
        originalname=upload.originalname,
        mimetype=upload.mimetype,
        folder="team-members",
        token=admin.token,
    )
    body["image_url"] = storage.stored_value(stored)


@router.get("")
async def get_active():
    try:
        rows = await db.fetch(
            "SELECT id, full_name, full_name_en, role, role_en, linkedin_url, "
            "github_url, website_url, resume_en, resume_fa, resume_template, "
            "image_url, avatar_icon, sort_order FROM team_members "
            "WHERE is_active = TRUE ORDER BY sort_order ASC, created_at DESC"
        )
        return success(data=[dict(row) for row in rows])
    except Exception:  # noqa: BLE001
        logger.exception("Get active team members error")
        return failure("Failed to fetch team members", 500)


@router.get("/{member_id}/resume.pdf")
async def download_resume(member_id: int, lang: str = "fa"):
    """Render a member's résumé as a PDF, on demand, in Persian or English.

    The text already lives in the database, so the file is generated per request
    instead of being stored: an edited résumé is downloadable immediately and no
    second copy can fall out of sync. Rendering is CPU-bound, so it runs in a
    worker thread to keep the event loop free.
    """
    lang = (lang or "fa").strip().lower()
    if lang not in ("fa", "en"):
        return failure("lang must be either 'fa' or 'en'", 400)

    row = await db.fetchrow(
        "SELECT id, full_name, full_name_en, role, role_en, linkedin_url, "
        "github_url, website_url, resume_en, resume_fa, resume_template "
        "FROM team_members WHERE id = $1 AND is_active = TRUE",
        member_id,
    )
    if row is None:
        return failure("Team member not found", 404)

    member = dict(row)
    try:
        pdf = await run_in_threadpool(
            build_resume_pdf, member, lang
        )
    except ResumePdfError as error:
        # An empty résumé is a content problem, not a server fault.
        logger.info("Resume PDF unavailable: %s", error)
        return failure(str(error), 404)
    except Exception:  # noqa: BLE001
        logger.exception("Resume PDF generation error")
        return failure("Failed to generate resume PDF", 500)

    filename = resume_filename(member, lang)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            # `filename` keeps old clients happy, `filename*` carries the name.
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            ),
            "Content-Length": str(len(pdf)),
            "Cache-Control": "public, max-age=300",
        },
    )


@router.get("/admin/all")
async def admin_get_all(_admin: AdminContext = Depends(require_admin)):
    try:
        rows = await db.fetch(
            f"SELECT {LIST_COLUMNS} FROM team_members ORDER BY sort_order ASC, created_at DESC"
        )
        return success(data=[dict(row) for row in rows])
    except Exception:  # noqa: BLE001
        logger.exception("Admin get team members error")
        return failure("Failed to fetch team members", 500)


@router.get("/admin/{member_id}")
async def admin_get_by_id(
    member_id: int,
    _admin: AdminContext = Depends(require_admin),
):
    try:
        row = await db.fetchrow("SELECT * FROM team_members WHERE id = $1", member_id)
        if row is None:
            return failure("Team member not found", 404)
        return success(data=row)
    except Exception:  # noqa: BLE001
        logger.exception("Admin get team member error")
        return failure("Failed to fetch team member", 500)


@router.post("/admin")
async def create_member(
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, files = await read_body(request)
        await _store_image(body, files, admin)

        full_name, role = body.get("full_name"), body.get("role")
        full_name_en = str(body.get("full_name_en") or "").strip()
        role_en = str(body.get("role_en") or "").strip()
        if not full_name or not role:
            return failure("full_name and role are required", 400)
        # The English résumé is headed by the Latin name and the English title,
        # so both are required.
        if not full_name_en:
            return failure("full_name_en is required", 400)
        if not role_en:
            return failure("role_en is required", 400)

        active = optional_bool(body.get("is_active"))

        row = await db.fetchrow(
            "INSERT INTO team_members (full_name, full_name_en, role, role_en, "
            "linkedin_url, github_url, website_url, resume_en, resume_fa, "
            "resume_template, image_url, avatar_icon, sort_order, is_active) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14) "
            "RETURNING *",
            full_name,
            full_name_en,
            role,
            role_en,
            body.get("linkedin_url") or None,
            body.get("github_url") or None,
            body.get("website_url") or None,
            body.get("resume_en") or None,
            body.get("resume_fa") or None,
            _resume_template(body.get("resume_template")),
            storage.to_object_key(body.get("image_url")),
            _avatar_icon(body.get("avatar_icon")),
            to_int(body.get("sort_order"), 0) or 0,
            True if active is None else active,
        )
        return success(data=row, status_code=201)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception as error:  # noqa: BLE001
        logger.exception("Create team member error")
        return failure(str(error) or "Create failed", 500)


@router.put("/admin/{member_id}")
async def update_member(
    member_id: int,
    request: Request,
    admin: AdminContext = Depends(require_admin),
):
    try:
        body, files = await read_body(request)
        await _store_image(body, files, admin)

        existing = await db.fetchrow(
            "SELECT image_url FROM team_members WHERE id = $1", member_id
        )
        if existing is None:
            return failure("Team member not found", 404)

        row = await db.fetchrow(
            "UPDATE team_members SET\n"
            "  full_name = COALESCE($1, full_name),\n"
            "  full_name_en = COALESCE($2, full_name_en),\n"
            "  role = COALESCE($3, role),\n"
            "  role_en = COALESCE($4, role_en),\n"
            "  linkedin_url = $5,\n"
            "  github_url = $6,\n"
            "  website_url = $7,\n"
            "  resume_en = $8,\n"
            "  resume_fa = $9,\n"
            "  resume_template = $10,\n"
            "  image_url = COALESCE($11, image_url),\n"
            # Assigned unconditionally, not COALESCE'd: the admin form always
            # sends the field, and COALESCE would make "no icon chosen" (NULL)
            # indistinguishable from "field omitted", leaving a stale icon that
            # the admin had already cleared.
            "  avatar_icon = $12,\n"
            "  sort_order = COALESCE($13, sort_order),\n"
            "  is_active = COALESCE($14, is_active),\n"
            "  updated_at = CURRENT_TIMESTAMP\n"
            "WHERE id = $15\n"
            "RETURNING *",
            body.get("full_name"),
            str(body.get("full_name_en") or "").strip() or None,
            body.get("role"),
            str(body.get("role_en") or "").strip() or None,
            body.get("linkedin_url"),
            body.get("github_url"),
            body.get("website_url"),
            body.get("resume_en"),
            body.get("resume_fa"),
            _resume_template(body.get("resume_template")),
            storage.to_object_key(body.get("image_url")),
            _avatar_icon(body.get("avatar_icon")),
            to_int(body.get("sort_order")),
            optional_bool(body.get("is_active")),
            member_id,
        )
        return success(data=row)
    except ApiError as error:
        return failure(error.message, error.status_code)
    except Exception as error:  # noqa: BLE001
        logger.exception("Update team member error")
        return failure(str(error) or "Update failed", 500)


@router.delete("/admin/{member_id}/image")
async def delete_member_image(
    member_id: int,
    admin: AdminContext = Depends(require_admin),
):
    try:
        existing = await db.fetchrow(
            "SELECT id, image_url FROM team_members WHERE id = $1", member_id
        )
        if existing is None:
            return failure("Team member not found", 404)

        current_image = existing["image_url"]
        if not current_image:
            return failure("Team member has no image", 404)

        await db.execute(
            "UPDATE team_members SET image_url = NULL, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = $1",
            member_id,
        )
        await storage.remove_stored_file(current_image, admin.token, admin.app_id)

        return success(message="Team member image deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete team member image error")
        return failure("Failed to delete team member image", 500)


@router.delete("/admin/{member_id}")
async def remove_member(
    member_id: int,
    admin: AdminContext = Depends(require_admin),
):
    try:
        existing = await db.fetchrow(
            "SELECT image_url FROM team_members WHERE id = $1", member_id
        )
        if existing is None:
            return failure("Team member not found", 404)

        image_url = existing["image_url"]
        if image_url:
            await storage.remove_stored_file(image_url, admin.token, admin.app_id)

        await db.execute("DELETE FROM team_members WHERE id = $1", member_id)
        return success(message="Team member deleted")
    except Exception:  # noqa: BLE001
        logger.exception("Delete team member error")
        return failure("Failed to delete team member", 500)
