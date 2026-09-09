from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
import urllib.parse

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response
from pydantic import BaseModel

from . import db, drive
from .config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

_MEDIA_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

SESSION_COOKIE_NAME = "admin_session"
SESSION_MAX_AGE_SECONDS = 8 * 60 * 60  # 8 hours

# Prefer a dedicated secret from env (settings.session_secret) if you add one;
# falls back to deriving from admin credentials so this works without any
# extra configuration.
_SESSION_SECRET = (
    getattr(settings, "session_secret", None)
    or f"{settings.admin_username}:{settings.admin_password}"
).encode()


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_session_token(username: str) -> str:
    payload = json.dumps({"u": username, "exp": time.time() + SESSION_MAX_AGE_SECONDS}).encode()
    signature = hmac.new(_SESSION_SECRET, payload, hashlib.sha256).digest()
    return f"{_b64encode(payload)}.{_b64encode(signature)}"


def verify_session_token(token: str) -> bool:
    try:
        payload_b64, sig_b64 = token.split(".", 1)
        payload = _b64decode(payload_b64)
        signature = _b64decode(sig_b64)
        expected_sig = hmac.new(_SESSION_SECRET, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(signature, expected_sig):
            return False
        data = json.loads(payload)
        return float(data.get("exp", 0)) > time.time()
    except Exception:
        return False


def require_admin_session(admin_session: str | None = Cookie(default=None)) -> str:
    if not settings.admin_username or not settings.admin_password:
        logger.error("admin_username/admin_password not configured")
        raise HTTPException(status_code=503, detail="Admin access is not configured")
    if not admin_session or not verify_session_token(admin_session):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return "admin"


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginRequest, response: Response):
    if not settings.admin_username or not settings.admin_password:
        raise HTTPException(status_code=503, detail="Admin access is not configured")

    user_ok = secrets.compare_digest(body.username, settings.admin_username)
    pass_ok = secrets.compare_digest(body.password, settings.admin_password)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_session_token(body.username)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {"status": "ok"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"status": "ok"}


@router.get("/me")
def me(_: str = Depends(require_admin_session)):
    return {"status": "ok"}


@router.get("/agreements")
def list_agreements(
    _: str = Depends(require_admin_session),
    company: str = Query("", description="Exact match on company name"),
    iin: str = Query("", description="Substring match on IIN"),
    phone: str = Query("", description="Substring match on phone number"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    return db.list_agreements(company=company, iin=iin, phone=phone, page=page, page_size=page_size)


def _content_disposition(filename: str) -> str:
    ascii_fallback = "".join(c if ord(c) < 128 else "_" for c in filename) or "file"
    quoted_utf8 = urllib.parse.quote(filename)
    return f'attachment; filename="{ascii_fallback}"; filename*=UTF-8\'\'{quoted_utf8}'


@router.get("/agreements/{agreement_id}/download")
def download_agreement(
    agreement_id: str,
    file_type: str = Query("pdf", pattern="^(pdf|docx)$"),
    _: str = Depends(require_admin_session),
):
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
        headers={"Content-Disposition": _content_disposition(filename)},
    )


@router.delete("/agreements/{agreement_id}")
def delete_agreement(
    agreement_id: str,
    _: str = Depends(require_admin_session),
):
    record = db.get_agreement(agreement_id)
    if not record:
        raise HTTPException(status_code=404, detail="Agreement not found")

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
