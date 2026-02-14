from __future__ import annotations

import csv
import io
import re
import unicodedata

from app.schemas import CallInputRow

REQUIRED_FIELDS = {"name", "room_id", "monto_deuda", "fecha_limite", "telefono"}

HEADER_ALIASES = {
    "name": "name",
    "nombre": "name",
    "persona": "name",
    "room_id": "room_id",
    "roomid": "room_id",
    "room": "room_id",
    "sala": "room_id",
    "monto_deuda": "monto_deuda",
    "montodeuda": "monto_deuda",
    "monto": "monto_deuda",
    "deuda": "monto_deuda",
    "fecha_limite": "fecha_limite",
    "fechalimite": "fecha_limite",
    "fecha_vencimiento": "fecha_limite",
    "vencimiento": "fecha_limite",
    "telefono": "telefono",
    "telefono_contacto": "telefono",
    "phone": "telefono",
    "celular": "telefono",
}


def parse_csv_rows(content: bytes) -> list[CallInputRow]:
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

    rows: list[CallInputRow] = []
    for index, raw_row in enumerate(reader, start=2):
        canonical_row: dict[str, str] = {}
        for original_key, value in raw_row.items():
            key = canonical_map.get(original_key, "")
            if key:
                canonical_row[key] = (value or "").strip()

        if not any(canonical_row.values()):
            continue

        try:
            row = CallInputRow(
                name=canonical_row["name"],
                room_id=canonical_row["room_id"],
                monto_deuda=_parse_amount(canonical_row["monto_deuda"]),
                fecha_limite=canonical_row["fecha_limite"],
                telefono=canonical_row["telefono"],
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
        raise ValueError("monto_deuda is empty")

    sanitized = re.sub(r"[^0-9,.-]", "", raw)
    if sanitized.count(",") > 0 and sanitized.count(".") > 0:
        sanitized = sanitized.replace(",", "")
    elif sanitized.count(",") > 0:
        sanitized = sanitized.replace(",", ".")

    amount = float(sanitized)
    if amount < 0:
        raise ValueError("monto_deuda must be non-negative")
    return round(amount, 2)
