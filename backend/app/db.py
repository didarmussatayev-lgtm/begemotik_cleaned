from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

import psycopg2
import psycopg2.extras

from .config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS agreements (
    id                  SERIAL PRIMARY KEY,
    agreement_id        TEXT UNIQUE NOT NULL,
    company             TEXT,
    full_name           TEXT NOT NULL,
    iin                 TEXT NOT NULL,
    phone               TEXT,
    procedure           TEXT,
    template_key        TEXT,
    date_of_birth       TEXT,
    signed_at           TIMESTAMPTZ NOT NULL,
    drive_docx_file_id  TEXT,
    drive_pdf_file_id   TEXT,
    drive_docx_link     TEXT,
    drive_pdf_link      TEXT,
    drive_upload_error  TEXT,
    created_at          TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agreements_iin ON agreements(iin);
CREATE INDEX IF NOT EXISTS idx_agreements_phone ON agreements(phone);
CREATE INDEX IF NOT EXISTS idx_agreements_signed_at ON agreements(signed_at);
"""


def init_db() -> None:
    """Create the table/indexes if they don't exist yet. Call once on startup."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(_SCHEMA)


@contextmanager
def _connect() -> Iterator["psycopg2.extensions.connection"]:
    # Managed Postgres (Render/Railway/Supabase/etc.) almost always needs
    # sslmode=require on external connections — add "?sslmode=require" to
    # settings.database_url if your provider needs it and it's not already
    # in the connection string they gave you.
    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Add it to your environment (e.g. "
            "postgres://user:password@host:5432/dbname)."
        )
    conn = psycopg2.connect(settings.database_url, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_agreement(
    *,
    agreement_id: str,
    full_name: str,
    iin: str,
    phone: str = "",
    procedure: str = "",
    template_key: str = "",
    date_of_birth: str = "",
    company: str = "",
    drive_docx_file_id: str = "",
    drive_pdf_file_id: str = "",
    drive_docx_link: str = "",
    drive_pdf_link: str = "",
    drive_upload_error: str = "",
) -> None:
    """Insert one row per generated agreement. Call this right after DOCX/PDF
    generation (and, ideally, after the Drive upload so file ids are available —
    but don't let a Drive failure prevent the row from being written; the
    dashboard should still show the record, with drive links empty/an error
    noted, so nothing is silently lost)."""
    now = datetime.now(timezone.utc)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO agreements (
                    agreement_id, company, full_name, iin, phone, procedure, template_key,
                    date_of_birth, signed_at, drive_docx_file_id, drive_pdf_file_id,
                    drive_docx_link, drive_pdf_link, drive_upload_error, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (agreement_id) DO UPDATE SET
                    drive_docx_file_id = EXCLUDED.drive_docx_file_id,
                    drive_pdf_file_id = EXCLUDED.drive_pdf_file_id,
                    drive_docx_link = EXCLUDED.drive_docx_link,
                    drive_pdf_link = EXCLUDED.drive_pdf_link,
                    drive_upload_error = EXCLUDED.drive_upload_error
                """,
                (
                    agreement_id, company, full_name, iin, phone, procedure, template_key,
                    date_of_birth, now, drive_docx_file_id, drive_pdf_file_id,
                    drive_docx_link, drive_pdf_link, drive_upload_error, now,
                ),
            )


def list_agreements(
    *,
    company: str = "",
    iin: str = "",
    phone: str = "",
    page: int = 1,
    page_size: int = 10,
) -> dict[str, Any]:
    """Return {items, total, page, page_size} filtered + paginated, newest first."""
    where = []
    params: list[Any] = []
    if company:
        where.append("company = %s")
        params.append(company)
    if iin:
        where.append("iin ILIKE %s")
        params.append(f"%{iin}%")
    if phone:
        where.append("phone ILIKE %s")
        params.append(f"%{phone}%")

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    offset = max(page - 1, 0) * page_size

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS c FROM agreements {where_sql}", params)
            total = cur.fetchone()["c"]

            cur.execute(
                f"""
                SELECT * FROM agreements {where_sql}
                ORDER BY signed_at DESC
                LIMIT %s OFFSET %s
                """,
                [*params, page_size, offset],
            )
            rows = cur.fetchall()

    return {
        "items": [dict(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_agreement(agreement_id: str) -> dict[str, Any] | None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM agreements WHERE agreement_id = %s", (agreement_id,))
            row = cur.fetchone()
    return dict(row) if row else None


def delete_agreement(agreement_id: str) -> bool:
    """Delete the DB row. Returns True if a row was actually deleted.
    Deleting the underlying Drive files is the caller's responsibility —
    do that first (via the Drive API) and only call this after it succeeds,
    so a failed Drive delete doesn't silently orphan files."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM agreements WHERE agreement_id = %s", (agreement_id,))
            deleted = cur.rowcount > 0
    return deleted
