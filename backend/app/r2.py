from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path

logger = logging.getLogger(__name__)

_R2_AVAILABLE = False
try:
    import boto3
    from botocore.client import Config as BotoConfig
    from botocore.exceptions import ClientError
    _R2_AVAILABLE = True
except ImportError:
    logger.warning("boto3 not installed; R2 upload disabled")


def _safe_filename(value: str) -> str:
    """Normalize a string for safe and readable filenames."""
    normalized = unicodedata.normalize("NFKC", value).strip()
    normalized = re.sub(r"[\x00-\x1f\x7f]+", "", normalized)
    normalized = re.sub(r'[\\/:*?"<>|]+', " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    normalized = re.sub(r"[^\w .()\-]", "", normalized, flags=re.UNICODE)
    normalized = normalized.replace(" ", "_")
    return (normalized or "patient")[:80]


def build_patient_filename_base(iin: str, full_name: str) -> str:
    safe_iin = _safe_filename(iin)
    safe_name = _safe_filename(full_name)
    return f"{safe_iin}_{safe_name}"


def _build_client(r2_credentials_info: dict):
    """
    Build and return an S3-compatible client pointed at Cloudflare R2.

    r2_credentials_info expects:
        account_id, access_key_id, secret_access_key
    """
    if not _R2_AVAILABLE:
        raise RuntimeError("boto3 is not installed")
    if not r2_credentials_info:
        raise RuntimeError(
            "No R2 credentials found. Set R2_ACCOUNT_ID / R2_ACCESS_KEY_ID / "
            "R2_SECRET_ACCESS_KEY / R2_BUCKET_NAME."
        )
    account_id = r2_credentials_info["account_id"]
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=r2_credentials_info["access_key_id"],
        aws_secret_access_key=r2_credentials_info["secret_access_key"],
        config=BotoConfig(signature_version="s3v4"),
        region_name="auto",
    )


def upload_documents(
    file_paths: list[Path],
    folder_id: str,
    iin: str,
    full_name: str,
    r2_credentials_info: dict,
) -> dict:
    """
    Upload generated documents to R2.
    Returns a dict of {filename: object_key}. object_key is what you should
    store in the DB in place of the old Google Drive file id.

    folder_id is treated as an optional key prefix ("folder/") inside the bucket.
    """
    client = _build_client(r2_credentials_info)
    bucket = r2_credentials_info["bucket_name"]
    patient_base = build_patient_filename_base(iin, full_name)
    prefix = f"{folder_id.strip('/')}/" if folder_id else ""

    uploaded: dict[str, str] = {}
    for file_path in file_paths:
        suffix = _safe_filename(file_path.stem.split("_")[-1]) or "document"
        extension = file_path.suffix.lower()
        file_name = f"{patient_base}_{suffix}{extension}"
        key = f"{prefix}{file_name}"
        try:
            client.upload_file(str(file_path), bucket, key)
        except ClientError:
            logger.exception("Failed to upload %s to R2 as %s", file_path, key)
            raise
        logger.info("Uploaded file to R2 as %s", key)
        uploaded[file_name] = key
    return uploaded


def get_file_bytes(object_key: str, r2_credentials_info: dict) -> bytes:
    """Download an object's raw bytes from R2 by key. Used by the admin
    dashboard's download button so it works regardless of who is logged
    in — the server fetches with its own R2 credentials."""
    if not object_key:
        raise RuntimeError("No R2 object key provided")

    client = _build_client(r2_credentials_info)
    bucket = r2_credentials_info["bucket_name"]
    try:
        response = client.get_object(Bucket=bucket, Key=object_key)
        return response["Body"].read()
    except ClientError:
        logger.exception("Failed to download %s from R2", object_key)
        raise


def delete_file(object_key: str, r2_credentials_info: dict) -> None:
    """Permanently delete an object from R2 by key. Raises on failure so the
    caller can decide whether it's safe to also drop the DB record."""
    if not object_key:
        return
    client = _build_client(r2_credentials_info)
    bucket = r2_credentials_info["bucket_name"]
    try:
        client.delete_object(Bucket=bucket, Key=object_key)
    except ClientError:
        logger.exception("Failed to delete %s from R2", object_key)
        raise
    logger.info("Deleted R2 object %s", object_key)
