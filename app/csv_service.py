from __future__ import annotations

import csv
import io
import re
import unicodedata

from app.schemas import CallInput

REQUIRED_FIELDS = {"phone_number", "name", "debt_amount", "due_date"}

HEADER_ALIASES = {
    "phone_number": "phone_number",
    "phone": "phone_number",
    "telefono": "phone_number",
    "telefono_contacto": "phone_number",
    "celular": "phone_number",
    "participant_name": "phone_number",
    "name": "name",
    "nombre": "name",
    "persona": "name",
    "debt_amount": "debt_amount",
    "debt": "debt_amount",
    "amount": "debt_amount",
    "monto_deuda": "debt_amount",
    "montodeuda": "debt_amount",
    "monto": "debt_amount",
    "deuda": "debt_amount",
    "due_date": "due_date",
    "duedate": "due_date",
    "due": "due_date",
    "fecha_limite": "due_date",
    "fechalimite": "due_date",
    "fecha_vencimiento": "due_date",
    "vencimiento": "due_date",
    "room_name": "room_name",
    "room_id": "room_name",
    "roomid": "room_name",
    "room": "room_name",
    "sala": "room_name",
}


def parse_csv_rows(content: bytes) -> list[CallInput]:
    decoded = content.decode("utf-8-sig").strip()
    if not decoded:
        raise ValueError("CSV file is empty.")

    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        raise ValueError("CSV file must include headers.")

    normalized_headers = {
        fieldname: _normalize_header(fieldname) for fieldname in reader.fieldnames
    }
    canonical_map = {
        original: HEADER_ALIASES.get(normalized, normalized)
        for original, normalized in normalized_headers.items()
    }

    available = set(canonical_map.values())
    missing = REQUIRED_FIELDS - available
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"Missing required CSV columns: {missing_columns}")

    rows: list[CallInput] = []
    for index, raw_row in enumerate(reader, start=2):
        canonical_row: dict[str, str] = {}
        for original_key, value in raw_row.items():
            key = canonical_map.get(original_key, "")
            if key:
                canonical_row[key] = (value or "").strip()

        if not any(canonical_row.values()):
            continue

        try:
            room_name_value = canonical_row.get("room_name") or None
            row = CallInput(
                phone_number=canonical_row["phone_number"],
                name=canonical_row["name"],
                debt_amount=_parse_amount(canonical_row["debt_amount"]),
                due_date=canonical_row["due_date"],
                room_name=room_name_value,
            )
        except Exception as exc:
            raise ValueError(f"Invalid row at line {index}: {exc}") from exc
        rows.append(row)

    if not rows:
        raise ValueError("CSV file does not contain valid data rows.")

    return rows


def _normalize_header(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    ascii_value = ascii_value.strip().lower()
    ascii_value = re.sub(r"[^a-z0-9]+", "_", ascii_value)
    return ascii_value.strip("_")


def _parse_amount(value: str) -> float:
    raw = value.strip()
    if not raw:
        raise ValueError("debt_amount is empty")

    sanitized = re.sub(r"[^0-9,.-]", "", raw)
    if sanitized.count(",") > 0 and sanitized.count(".") > 0:
        sanitized = sanitized.replace(",", "")
    elif sanitized.count(",") > 0:
        sanitized = sanitized.replace(",", ".")

    amount = float(sanitized)
    if amount < 0:
        raise ValueError("debt_amount must be non-negative")
    return round(amount, 2)
