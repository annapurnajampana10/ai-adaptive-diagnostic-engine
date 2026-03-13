from __future__ import annotations

from pydantic import BaseModel, Field


class QuestionCreate(BaseModel):
    question: str
    options: list[str] = Field(min_length=2)
    correct_answer: str
    difficulty: float = Field(ge=0.1, le=1.0)
    topic: str
    tags: list[str] = Field(default_factory=list)


class QuestionPublic(BaseModel):
    id: str
    question: str
    options: list[str]
    difficulty: float
    topic: str
    tags: list[str]

