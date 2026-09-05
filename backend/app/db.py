from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from .config import settings

# Path to the SQLite file. Set agreements_db_path (env: AGREEMENTS_DB_PATH) to
# a persistent disk/volume in production — SQLite is a single file, so it
# will be wiped on restart if it lives on ephemeral storage (e.g. most PaaS
# containers reset local disk on each deploy).
DB_PATH = Path(settings.agreements_db_path)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS agreements (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    agreement_id        TEXT UNIQUE NOT NULL,
    company              TEXT,
    full_name           TEXT NOT NULL,
    iin                 TEXT NOT NULL,
    phone               TEXT,
    procedure           TEXT,
    template_key        TEXT,
    date_of_birth       TEXT,
    signed_at           TEXT NOT NULL,
    drive_docx_file_id  TEXT,
    drive_pdf_file_id   TEXT,
    drive_docx_link     TEXT,
    drive_pdf_link      TEXT,
    drive_upload_error  TEXT,
    created_at          TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agreements_iin ON agreements(iin);
CREATE INDEX IF NOT EXISTS idx_agreements_phone ON agreements(phone);
CREATE INDEX IF NOT EXISTS idx_agreements_signed_at ON agreements(signed_at);
"""


def init_db() -> None:
    """Create the DB file/table if they don't exist yet. Call once on startup."""
    with _connect() as conn:
        conn.executescript(_SCHEMA)


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
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
    now = datetime.utcnow().isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO agreements (
                agreement_id, company, full_name, iin, phone, procedure, template_key,
                date_of_birth, signed_at, drive_docx_file_id, drive_pdf_file_id,
                drive_docx_link, drive_pdf_link, drive_upload_error, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(agreement_id) DO UPDATE SET
                drive_docx_file_id = excluded.drive_docx_file_id,
                drive_pdf_file_id = excluded.drive_pdf_file_id,
                drive_docx_link = excluded.drive_docx_link,
                drive_pdf_link = excluded.drive_pdf_link,
                drive_upload_error = excluded.drive_upload_error
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
        where.append("company = ?")
        params.append(company)
    if iin:
        where.append("iin LIKE ?")
        params.append(f"%{iin}%")
    if phone:
        where.append("phone LIKE ?")
        params.append(f"%{phone}%")

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    offset = max(page - 1, 0) * page_size

    with _connect() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) AS c FROM agreements {where_sql}", params
        ).fetchone()["c"]

        rows = conn.execute(
            f"""
            SELECT * FROM agreements {where_sql}
            ORDER BY signed_at DESC
            LIMIT ? OFFSET ?
            """,
            [*params, page_size, offset],
        ).fetchall()

    return {
        "items": [dict(row) for row in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_agreement(agreement_id: str) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM agreements WHERE agreement_id = ?", (agreement_id,)
        ).fetchone()
    return dict(row) if row else None


def delete_agreement(agreement_id: str) -> bool:
    """Delete the DB row. Returns True if a row was actually deleted.
    Deleting the underlying Drive files is the caller's responsibility —
    do that first (via the Drive API) and only call this after it succeeds,
    so a failed Drive delete doesn't silently orphan files."""
    with _connect() as conn:
        cur = conn.execute("DELETE FROM agreements WHERE agreement_id = ?", (agreement_id,))
    return cur.rowcount > 0
