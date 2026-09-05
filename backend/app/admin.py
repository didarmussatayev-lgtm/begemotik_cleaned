from __future__ import annotations

import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from . import db, drive
from .config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
security = HTTPBasic()

_MEDIA_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    if not settings.admin_username or not settings.admin_password:
        # Fail closed: if these aren't configured, nobody gets in rather than
        # everybody getting in.
        logger.error("admin_username/admin_password not configured")
        raise HTTPException(status_code=503, detail="Admin access is not configured")

    user_ok = secrets.compare_digest(credentials.username, settings.admin_username)
    pass_ok = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.get("/agreements")
def list_agreements(
    _: str = Depends(require_admin),
    company: str = Query("", description="Exact match on company name"),
    iin: str = Query("", description="Substring match on IIN"),
    phone: str = Query("", description="Substring match on phone number"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    return db.list_agreements(company=company, iin=iin, phone=phone, page=page, page_size=page_size)


@router.get("/agreements/{agreement_id}/download")
def download_agreement(
    agreement_id: str,
    file_type: str = Query("pdf", pattern="^(pdf|docx)$"),
    _: str = Depends(require_admin),
):
    """Streams the file's bytes straight from Drive using the server's own
    OAuth credentials — works no matter which Google account the admin is
    logged into in their browser."""
    record = db.get_agreement(agreement_id)
    if not record:
        raise HTTPException(status_code=404, detail="Agreement not found")

    file_id = record["drive_pdf_file_id"] if file_type == "pdf" else record["drive_docx_file_id"]
    if not file_id:
        raise HTTPException(status_code=404, detail=f"No {file_type} stored for this agreement")

    try:
        content = drive.get_file_bytes(file_id, settings.oauth_credentials_info)
    except Exception as exc:
        logger.exception("Failed to download %s for agreement %s", file_type, agreement_id)
        raise HTTPException(status_code=502, detail=f"Drive download failed: {exc}") from exc

    filename = f"{record['iin']}_{record['full_name']}.{file_type}"
    return Response(
        content=content,
        media_type=_MEDIA_TYPES[file_type],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/agreements/{agreement_id}")
def delete_agreement(
    agreement_id: str,
    _: str = Depends(require_admin),
):
    record = db.get_agreement(agreement_id)
    if not record:
        raise HTTPException(status_code=404, detail="Agreement not found")

    # Delete both Drive files first. Only drop the DB row if that succeeds —
    # otherwise a failed Drive delete would silently orphan the file with no
    # record left to retry from.
    errors: list[str] = []
    for file_type, file_id in (
        ("docx", record["drive_docx_file_id"]),
        ("pdf", record["drive_pdf_file_id"]),
    ):
        if not file_id:
            continue
        try:
            drive.delete_file(file_id, settings.oauth_credentials_info)
        except Exception as exc:
            logger.exception("Failed to delete Drive %s file for agreement %s", file_type, agreement_id)
            errors.append(f"{file_type}: {exc}")

    if errors:
        raise HTTPException(
            status_code=502,
            detail=f"Could not delete from Drive, DB record kept: {'; '.join(errors)}",
        )

    deleted = db.delete_agreement(agreement_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agreement not found")
    return {"status": "deleted", "agreement_id": agreement_id}
