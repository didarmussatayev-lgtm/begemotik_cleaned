from __future__ import annotations

import logging
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .admin import router as admin_router
from .config import settings
from . import db as agreements_db
from .docgen import convert_to_pdf, generate_begemotik_docx
from .r2 import build_patient_filename_base, upload_documents
from .models import BegemotikAgreementRequest

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)
logger.info("=== DEPLOY MARKER v6: migrated storage from Google Drive to Cloudflare R2 ===")

TEMPLATE_FILENAME = "begemotik_template.docx"

app = FastAPI(title="Begemotik Consent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS", "GET", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(admin_router)

static_admin_dir = Path(__file__).parent / "static_admin"
if static_admin_dir.exists():
    app.mount("/admin", StaticFiles(directory=str(static_admin_dir), html=True), name="admin")

@app.get("/api/v1/debug/static-admin")
def debug_static_admin():
    return {
        "static_admin_dir": str(static_admin_dir),
        "exists": static_admin_dir.exists(),
        "contents": [f.name for f in static_admin_dir.iterdir()] if static_admin_dir.exists() else [],
    }
@app.on_event("startup")
async def on_startup():
    agreements_db.init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _split_uploaded_keys(uploaded_keys: dict[str, str]) -> tuple[str, str]:
    docx_key = ""
    pdf_key = ""
    for name, key in uploaded_keys.items():
        lower = name.lower()
        if lower.endswith(".docx"):
            docx_key = key
        elif lower.endswith(".pdf"):
            pdf_key = key
    return docx_key, pdf_key


def _r2_view_link(object_key: str) -> str:
    """Build a direct link only if a public base URL is configured
    (an r2.dev subdomain or a custom domain mapped to the bucket).
    Otherwise leave empty — the admin dashboard downloads via the
    server-side proxy (get_file_bytes) using the stored key instead."""
    if not object_key or not settings.r2_public_base_url:
        return ""
    return f"{settings.r2_public_base_url.rstrip('/')}/{object_key}"


def _parse_birthdate_iso(birthdate: str) -> str:
    try:
        return datetime.strptime(birthdate, "%d.%m.%Y").date().isoformat()
    except ValueError:
        return ""


@app.post("/api/v1/agreements")
async def create_agreement(body: BegemotikAgreementRequest):
    full_name = " ".join(filter(None, [body.surname, body.name, body.last_name]))
    agreement_id = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    logger.info("Processing agreement %s for %s", agreement_id, full_name)

    tmp_dir = Path(tempfile.mkdtemp(prefix="agreement_"))
    try:
        template_path = Path(__file__).parent / TEMPLATE_FILENAME
        if not template_path.exists():
            logger.error("Template not found at %s", template_path)
            raise HTTPException(
                status_code=500,
                detail="Document template not found. Please contact support.",
            )

        patient_file_base = build_patient_filename_base(body.iin, full_name)
        output_basename = f"{patient_file_base}_begemotik"

        allergy_value = body.allergy_text if body.has_allergy else ""
        no_allergy_value = "" if body.has_allergy else "аллергий не имею"

        try:
            docx_path = generate_begemotik_docx(
                template_path=template_path,
                iin=body.iin,
                surname=body.surname,
                name=body.name,
                last_name=body.last_name,
                gender=body.gender,
                birthdate=body.birthdate,
                phone=body.phone,
                has_kinship=body.has_kinship,
                surname_kinship=body.surname_kinship,
                name_kinship=body.name_kinship,
                last_name_kinship=body.last_name_kinship,
                degree_of_kinship=body.degree_of_kinship,
                allergy_value=allergy_value,
                no_allergy_value=no_allergy_value,
                procedure=body.procedure,
                signature_base64=body.signature_base64,
                agreement_id=agreement_id,
                output_basename=output_basename,
                output_dir=tmp_dir,
            )
        except Exception as exc:
            logger.exception("DOCX generation failed for agreement %s", agreement_id)
            raise HTTPException(status_code=500, detail=f"Document generation failed: {exc}") from exc

        try:
            pdf_path = convert_to_pdf(docx_path, tmp_dir)
        except Exception as exc:
            logger.exception("PDF conversion failed for agreement %s", agreement_id)
            raise HTTPException(status_code=500, detail=f"PDF conversion failed: {exc}") from exc

        storage_error: str | None = None
        docx_key = ""
        pdf_key = ""
        if settings.r2_credentials_info:
            try:
                uploaded_keys = upload_documents(
                    file_paths=[docx_path, pdf_path],
                    folder_id=settings.r2_folder_prefix,
                    iin=body.iin,
                    full_name=full_name,
                    r2_credentials_info=settings.r2_credentials_info,
                )
                docx_key, pdf_key = _split_uploaded_keys(uploaded_keys)
            except Exception as exc:
                storage_error = str(exc)
                logger.error("R2 upload failed for %s: %s", patient_file_base, exc)
        else:
            logger.warning("R2 credentials not fully set — skipping R2 upload")

        try:
            # Note: these DB columns are named drive_* for historical reasons —
            # they now hold R2 object keys / links instead of Google Drive
            # file ids / view links. Left as-is to avoid a schema migration.
            agreements_db.insert_agreement(
                agreement_id=agreement_id,
                full_name=full_name,
                iin=body.iin,
                phone=body.phone,
                procedure=body.procedure,
                template_key="begemotik",
                date_of_birth=_parse_birthdate_iso(body.birthdate),
                drive_docx_file_id=docx_key,
                drive_pdf_file_id=pdf_key,
                drive_docx_link=_r2_view_link(docx_key),
                drive_pdf_link=_r2_view_link(pdf_key),
                drive_upload_error=storage_error or "",
            )
        except Exception:
            logger.exception("Failed to write DB record for agreement %s", agreement_id)

        headers: dict[str, str] = {}
        if storage_error:
            # HTTP headers must be latin-1; error text can contain the
            # (Cyrillic) filename, so strip anything non-ASCII instead of
            # crashing the whole response.
            safe_error = storage_error.encode("ascii", "ignore").decode("ascii")[:200]
            if safe_error:
                headers["X-Storage-Error"] = safe_error

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename="Begemotik.pdf",
            headers=headers,
            background=_cleanup_background(tmp_dir),
        )

    except HTTPException:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.exception("Unexpected error for agreement %s", agreement_id)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


def _cleanup_background(tmp_dir: Path):
    from starlette.background import BackgroundTask

    def _cleanup():
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.debug("Cleaned up temp dir: %s", tmp_dir)

    return BackgroundTask(_cleanup)
