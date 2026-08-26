from __future__ import annotations

import re
from datetime import date

from pydantic import BaseModel, model_validator

KINSHIP_VALUES = {"ребенок", "лицо, чьим законным представителем я являюсь"}


class BegemotikAgreementRequest(BaseModel):
    # Patient fields
    iin: str
    surname: str
    name: str
    last_name: str = ""
    gender: str
    birthdate: str
    phone: str

    # Legal representative (optional)
    has_kinship: bool = False
    surname_kinship: str = ""
    name_kinship: str = ""
    last_name_kinship: str = ""
    degree_of_kinship: str = ""

    # Medical info
    has_allergy: bool = False
    allergy_text: str = ""
    procedure: str

    # Signature & consents
    signature_base64: str
    consent_facsimile: bool = False
    consent_personal_data: bool = False

    @model_validator(mode="after")
    def validate_fields(self) -> "BegemotikAgreementRequest":
        self.iin = self.iin.strip()
        if not re.fullmatch(r"\d{12}", self.iin):
            raise ValueError("IIN must be exactly 12 digits")

        cyrillic_re = re.compile(r"^[А-Яа-яЁёӘәҒғҚқҢңӨөҰұҮүҺһІі\s\-]+$")

        self.surname = self.surname.strip()
        if not self.surname or not cyrillic_re.match(self.surname):
            raise ValueError("surname must be non-empty Cyrillic text")

        self.name = self.name.strip()
        if not self.name or not cyrillic_re.match(self.name):
            raise ValueError("name must be non-empty Cyrillic text")

        self.last_name = self.last_name.strip()
        if self.last_name and not cyrillic_re.match(self.last_name):
            raise ValueError("last_name must be Cyrillic text when provided")

        self.gender = self.gender.strip()
        if self.gender not in {"мужской", "женский"}:
            raise ValueError("gender must be 'мужской' or 'женский'")

        self.birthdate = self.birthdate.strip()
        if not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", self.birthdate):
            raise ValueError("birthdate must be in DD.MM.YYYY format")
        try:
            from datetime import datetime as _dt
            bd = _dt.strptime(self.birthdate, "%d.%m.%Y").date()
            if bd > date.today():
                raise ValueError("birthdate cannot be in the future")
        except ValueError as exc:
            if "cannot be" in str(exc) or "does not match" in str(exc):
                raise
            raise ValueError("birthdate is not a valid calendar date") from exc

        self.phone = self.phone.strip()
        if not re.fullmatch(r"77\d{9}", re.sub(r"\D", "", self.phone)):
            raise ValueError("Phone must be in +77XXXXXXXXX format")

        if self.has_kinship:
            self.surname_kinship = self.surname_kinship.strip()
            if not self.surname_kinship or not cyrillic_re.match(self.surname_kinship):
                raise ValueError("surname_kinship must be non-empty Cyrillic text")
            self.name_kinship = self.name_kinship.strip()
            if not self.name_kinship or not cyrillic_re.match(self.name_kinship):
                raise ValueError("name_kinship must be non-empty Cyrillic text")
            self.last_name_kinship = self.last_name_kinship.strip()
            if self.last_name_kinship and not cyrillic_re.match(self.last_name_kinship):
                raise ValueError("last_name_kinship must be Cyrillic text when provided")
            self.degree_of_kinship = self.degree_of_kinship.strip()
            if self.degree_of_kinship not in KINSHIP_VALUES:
                raise ValueError("degree_of_kinship must be 'ребенок' or 'лицо, чьим законным представителем я являюсь'")
        else:
            self.surname_kinship = ""
            self.name_kinship = ""
            self.last_name_kinship = ""
            self.degree_of_kinship = ""

        self.allergy_text = self.allergy_text.strip()

        self.procedure = self.procedure.strip()
        if not self.procedure:
            raise ValueError("procedure is required")

        if not self.signature_base64.strip():
            raise ValueError("signature_base64 is required")

        return self
