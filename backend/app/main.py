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

from .config import settings
from .docgen import convert_to_pdf, generate_begemotik_docx
from .drive import build_patient_filename_base, upload_documents
from .models import BegemotikAgreementRequest

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

BEGEMOTIK_TEMPLATE_NAME = "begemotik_template.docx"

app = FastAPI(title="Electronic Consent API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/agreements")
async def create_agreement(body: BegemotikAgreementRequest):
    """
    Accept form data, generate DOCX+PDF, upload both to Google Drive,
    and return the PDF to the client as a downloadable file.
    """
    agreement_id = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    patient_full_name = " ".join(filter(None, [body.surname, body.name, body.last_name]))
    logger.info("Processing agreement %s for %s", agreement_id, patient_full_name)

    tmp_dir = Path(tempfile.mkdtemp(prefix="agreement_"))
    try:
        template_dir = Path(__file__).parent / "templates"
        template_path = template_dir / BEGEMOTIK_TEMPLATE_NAME

        if not template_path.exists():
            logger.error("Template not found: %s", template_path)
            raise HTTPException(
                status_code=500,
                detail=f"Document template '{BEGEMOTIK_TEMPLATE_NAME}' not found. Please contact support.",
            )

        # Build allergy context values
        if body.has_allergy and body.allergy_text:
            allergy_value = f"Есть аллергия на: {body.allergy_text}"
            no_allergy_value = ""
        else:
            allergy_value = ""
            no_allergy_value = "Нет аллергии"

        patient_file_base = build_patient_filename_base(body.iin, patient_full_name)
        output_basename = f"{patient_file_base}_begemotik_consent"

        # 1. Generate the DOCX from the template
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
            logger.exception("DOCX generation failed")
            raise HTTPException(status_code=500, detail=f"Document generation failed: {exc}") from exc

        # 2. Convert the DOCX to PDF (only after step 1 succeeded)
        try:
            pdf_path = convert_to_pdf(docx_path, tmp_dir)
        except Exception as exc:
            logger.exception("PDF conversion failed")
            raise HTTPException(status_code=500, detail=f"PDF conversion failed: {exc}") from exc

        # 3. Upload both files to Google Drive (best-effort — never blocks the download)
        drive_error: str | None = None
        if settings.google_drive_folder_id:
            if settings.oauth_credentials_info:
                try:
                    upload_documents(
                        file_paths=[docx_path, pdf_path],
                        folder_id=settings.google_drive_folder_id,
                        iin=body.iin,
                        full_name=patient_full_name,
                        oauth_credentials_info=settings.oauth_credentials_info,
                    )
                except Exception as exc:
                    drive_error = str(exc)
                    logger.error("Drive upload failed for %s: %s", patient_file_base, exc)
            else:
                logger.warning("Google Drive OAuth credentials not set — skipping Drive upload")
        else:
            logger.warning("GOOGLE_DRIVE_FOLDER_ID not set — skipping Drive upload")

        headers: dict[str, str] = {}
        if drive_error:
            headers["X-Drive-Error"] = drive_error[:200]

        # 4. Return only the PDF for immediate download on the client's phone
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename="med_centr_begemotik.pdf",
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
    """Return a BackgroundTask that removes the temp directory after the response is sent."""
    from starlette.background import BackgroundTask

    def _cleanup():
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.debug("Cleaned up temp dir: %s", tmp_dir)

    return BackgroundTask(_cleanup)
