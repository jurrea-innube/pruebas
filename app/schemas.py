from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import AnyHttpUrl, BaseModel, Field


def _default_room_name() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"mock-room-{stamp}"


class ParticipantInput(BaseModel):
    name: str = Field(min_length=1, description="Nombre visible en la transcripcion")
    identity: str | None = Field(
        default=None, description="Identidad tecnica del participante"
    )


class MockLiveKitRequest(BaseModel):
    call_id: str = Field(default_factory=lambda: f"call_{uuid4().hex[:10]}")
    room_name: str = Field(default_factory=_default_room_name, min_length=3)
    webhook_url: AnyHttpUrl | None = None
    language: str = Field(default="es", min_length=2, max_length=8)
    call_context: str = Field(
        default="Llamada de seguimiento comercial y soporte al cliente."
    )
    objectives: list[str] = Field(
        default_factory=lambda: [
            "Entender la necesidad principal del cliente",
            "Acordar un siguiente paso",
        ]
    )
    turns: int = Field(default=8, ge=4, le=30)
    user: ParticipantInput
    agent: ParticipantInput = Field(
        default_factory=lambda: ParticipantInput(
            name="Agente virtual", identity="agent_virtual"
        )
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class WebhookDeliveryResult(BaseModel):
    delivered: bool
    status_code: int
    response_body: str
