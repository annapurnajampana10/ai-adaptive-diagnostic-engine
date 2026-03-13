from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class SessionPublic(BaseModel):
    id: str
    ability: float = Field(ge=0.1, le=1.0)
    answered_count: int
    created_at: datetime
    updated_at: datetime
    study_plan: list[str] | None = None
    difficulty_level: str | None = None


class NextQuestionResponse(BaseModel):
    session: SessionPublic
    question: dict | None


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    selected_answer: str


class SubmitAnswerResponse(BaseModel):
    correct: bool
    new_ability: float = Field(ge=0.1, le=1.0)
    session: SessionPublic
    next_question: dict | None
    study_plan: list[str] | None = None
    feedback: str | None = None
    score: float | None = None
