from __future__ import annotations

import logging
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .admin import router as admin_router
from .config import settings
from . import db as agreements_db
from .docgen import convert_to_pdf, generate_begemotik_docx
from .drive import build_patient_filename_base, upload_documents
from .models import BegemotikAgreementRequest
from .reminders import handle_incoming_whatsapp, start_scheduler

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)
logger.info("=== DEPLOY MARKER v4: begemotik model/docgen aligned ===")

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


@app.on_event("startup")
async def on_startup():
    start_scheduler()
    agreements_db.init_db()


@app.post("/api/v1/whatsapp-webhook")
async def whatsapp_webhook(request: Request):
    payload = await request.json()
    await handle_incoming_whatsapp(payload)
    return {"status": "ok"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _split_uploaded_ids(uploaded_ids: dict[str, str]) -> tuple[str, str]:
    """upload_documents() returns {filename: file_id}. docx and pdf share the
    same stem, so tell them apart by extension."""
    docx_file_id = ""
    pdf_file_id = ""
    for name, file_id in uploaded_ids.items():
        lower = name.lower()
        if lower.endswith(".docx"):
            docx_file_id = file_id
        elif lower.endswith(".pdf"):
            pdf_file_id = file_id
    return docx_file_id, pdf_file_id


def _drive_view_link(file_id: str) -> str:
    return f"https://drive.google.com/file/d/{file_id}/view" if file_id else ""


def _parse_birthdate_iso(birthdate: str) -> str:
    try:
        return datetime.strptime(birthdate, "%d.%m.%Y").date().isoformat()
    except ValueError:
        return ""


@app.post("/api/v1/agreements")
async def create_agreement(body: BegemotikAgreementRequest):
    """
    Accept form data, generate DOCX+PDF, upload both to Google Drive,
    record the agreement in the local DB for the admin dashboard, and
    return the PDF to the client as a downloadable file.
    """
    full_name = " ".join(filter(None, [body.surname, body.name, body.last_name]))
    agreement_id = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    logger.info("Processing agreement %s for %s", agreement_id, full_name)

    tmp_dir = Path(tempfile.mkdtemp(prefix="agreement_"))
    try:
        template_path = Path(__file__).parent / "templates" / TEMPLATE_FILENAME
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

        # Upload DOCX+PDF to Google Drive (best-effort — don't fail on Drive error)
        drive_error: str | None = None
        docx_file_id = ""
        pdf_file_id = ""
        if settings.google_drive_folder_id:
            if settings.oauth_credentials_info:
                try:
                    uploaded_ids = upload_documents(
                        file_paths=[docx_path, pdf_path],
                        folder_id=settings.google_drive_folder_id,
                        iin=body.iin,
                        full_name=full_name,
                        oauth_credentials_info=settings.oauth_credentials_info,
                    )
                    docx_file_id, pdf_file_id = _split_uploaded_ids(uploaded_ids)
                except Exception as exc:
                    drive_error = str(exc)
                    logger.error("Drive upload failed for %s: %s", patient_file_base, exc)
            else:
                logger.warning("Google Drive OAuth credentials not set — skipping Drive upload")
        else:
            logger.warning("GOOGLE_DRIVE_FOLDER_ID not set — skipping Drive upload")

        # Record the agreement for the admin dashboard, even if Drive upload failed
        try:
            agreements_db.insert_agreement(
                agreement_id=agreement_id,
                full_name=full_name,
                iin=body.iin,
                phone=body.phone,
                procedure=body.procedure,
                template_key="begemotik",
                date_of_birth=_parse_birthdate_iso(body.birthdate),
                drive_docx_file_id=docx_file_id,
                drive_pdf_file_id=pdf_file_id,
                drive_docx_link=_drive_view_link(docx_file_id),
                drive_pdf_link=_drive_view_link(pdf_file_id),
                drive_upload_error=drive_error or "",
            )
        except Exception:
            logger.exception("Failed to write DB record for agreement %s", agreement_id)

        headers: dict[str, str] = {}
        if drive_error:
            headers["X-Drive-Error"] = drive_error[:200]

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
    """Return a BackgroundTask that removes the temp directory."""
    from starlette.background import BackgroundTask

    def _cleanup():
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.debug("Cleaned up temp dir: %s", tmp_dir)

    return BackgroundTask(_cleanup)
