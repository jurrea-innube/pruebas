from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CallInput(BaseModel):
    phone_number: str = Field(..., min_length=1, max_length=50, description="Phone number")
    name: str = Field(..., min_length=1, max_length=255, description="Debtor name")
    debt_amount: float = Field(..., ge=0, description="Debt amount")
    due_date: str = Field(..., min_length=1, max_length=100, description="Debt due date")
    room_name: str | None = Field(
        default=None, min_length=1, max_length=255, description="Optional room identifier override"
    )


class Transcript(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)


class CallSimulationResult(BaseModel):
    room_name: str = Field(..., min_length=1, max_length=255, description="Room identifier")
    transcript: Transcript = Field(default_factory=Transcript, description="Transcript item stream")
    status: str = Field(default="completed", max_length=50, description="Call status")
    call_tags: list[str] = Field(default_factory=list, description="Tags associated with the call")
    participant_name: str = Field(..., min_length=1, max_length=255, description="Participant identifier")
    call_duration_seconds: float = Field(..., ge=0, description="Call duration in seconds")
