from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class CallInputRow(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Debtor name")
    room_id: str = Field(..., min_length=1, max_length=255, description="Room identifier")
    monto_deuda: float = Field(..., ge=0, description="Debt amount")
    fecha_limite: str = Field(..., min_length=1, max_length=100, description="Payment due date")
    telefono: str = Field(..., min_length=1, max_length=50, description="Phone number")


class TranscriptSegment(BaseModel):
    speaker: str = Field(..., min_length=1, max_length=20, description="Speaker role")
    text: str = Field(..., min_length=1, description="Segment text")
    start_time_seconds: float = Field(..., ge=0, description="Segment start second")
    end_time_seconds: float = Field(..., ge=0, description="Segment end second")


class Transcript(BaseModel):
    language: str = Field(default="es", min_length=2, max_length=10)
    sentiment_profile: str = Field(..., min_length=1, max_length=100)
    segments: list[TranscriptSegment] = Field(default_factory=list)
    full_text: str = Field(..., min_length=1)


class CallSimulationResult(BaseModel):
    room_name: str = Field(..., min_length=1, max_length=255, description="Room identifier")
    call_tags: list[str] = Field(default_factory=list, description="Tags associated with the call")
    participant_name: str = Field(..., min_length=1, max_length=255, description="Participant identifier")
    transcript: Optional[Transcript] = Field(default=None, description="Full transcript data")
    status: Optional[str] = Field(default=None, max_length=50, description="Call status")
    call_duration_seconds: Optional[float] = Field(
        default=None, description="Call duration in seconds (converted to integer)"
    )
