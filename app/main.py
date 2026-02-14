from __future__ import annotations

import asyncio
import logging
import random

from fastapi import FastAPI, HTTPException

from app.schemas import MockLiveKitRequest
from app.settings import settings
from app.transcription_service import generate_livekit_transcription_payload
from app.webhook_client import deliver_transcription

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("livekit-mock")

app = FastAPI(title="LiveKit Mock Transcription Service", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/mock/livekit/transcription")
async def mock_livekit_transcription(request: MockLiveKitRequest) -> dict:
    webhook_url = str(request.webhook_url) if request.webhook_url else settings.default_webhook_url
    if not webhook_url:
        raise HTTPException(
            status_code=400,
            detail=(
                "No webhook configured. Provide webhook_url in the request or set "
                "DEFAULT_WEBHOOK_URL in the environment."
            ),
        )

    payload = await generate_livekit_transcription_payload(request)
    sleep_seconds = random.randint(1, 10)
    await asyncio.sleep(sleep_seconds)

    delivery = await deliver_transcription(webhook_url, payload)
    if not delivery.delivered:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Webhook delivery failed",
                "status_code": delivery.status_code,
                "response_body": delivery.response_body,
            },
        )

    logger.info(
        "Mock transcription delivered. call_id=%s webhook=%s sleep=%ss",
        request.call_id,
        webhook_url,
        sleep_seconds,
    )

    return {
        "status": "delivered",
        "call_id": request.call_id,
        "sleep_seconds": sleep_seconds,
        "webhook_status_code": delivery.status_code,
        "payload": payload,
    }
