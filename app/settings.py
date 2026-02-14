from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    default_webhook_url: str | None = os.getenv("DEFAULT_WEBHOOK_URL")
    webhook_timeout_seconds: float = float(os.getenv("WEBHOOK_TIMEOUT_SECONDS", "20"))


settings = Settings()
