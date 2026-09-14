from __future__ import annotations

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General
    app_env: str = "development"
    log_level: str = "INFO"

    # CORS — comma-separated list of origins, e.g. "https://user.github.io,http://localhost:5500"
    cors_origins: str = "*"

    # --- Cloudflare R2 (S3-compatible object storage) ---
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""

    # Optional: key prefix inside the bucket, analogous to the old Drive folder.
    r2_folder_prefix: str = ""

    # Optional: public base URL for direct links (e.g. an r2.dev subdomain or a
    # custom domain mapped to the bucket). Leave empty if the bucket is private —
    # in that case only the admin dashboard's proxied download will work.
    r2_public_base_url: str = ""

    # --- Admin dashboard (list/download/delete signed agreements) ---
    admin_username: str = ""
    admin_password: str = ""

    # Secret used to sign admin session cookies. Set this explicitly in
    # production — if left empty, admin.py falls back to deriving one from
    # admin_username/admin_password, which is fine but less ideal.
    session_secret: str = ""

    # Postgres connection string, e.g. postgres://user:password@host:5432/dbname
    # (append ?sslmode=require if your provider needs it for external connections)
    database_url: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def r2_credentials_info(self) -> dict | None:
        """Return R2 credentials dict if all required vars are set, else None."""
        if (
            self.r2_account_id.strip()
            and self.r2_access_key_id.strip()
            and self.r2_secret_access_key.strip()
            and self.r2_bucket_name.strip()
        ):
            return {
                "account_id": self.r2_account_id.strip(),
                "access_key_id": self.r2_access_key_id.strip(),
                "secret_access_key": self.r2_secret_access_key.strip(),
                "bucket_name": self.r2_bucket_name.strip(),
            }
        return None


settings = Settings()
