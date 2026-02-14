from __future__ import annotations

import httpx

from app.schemas import WebhookDeliveryResult
from app.settings import settings


async def deliver_transcription(webhook_url: str, payload: dict) -> WebhookDeliveryResult:
    async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
        response = await client.post(webhook_url, json=payload)

    return WebhookDeliveryResult(
        delivered=200 <= response.status_code < 300,
        status_code=response.status_code,
        response_body=response.text,
    )
