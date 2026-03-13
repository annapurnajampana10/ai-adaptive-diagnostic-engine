from __future__ import annotations

from typing import Any
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

from app.db.mongo import get_db
from app.schemas.common import utc_now
from app.schemas.session import (
    NextQuestionResponse,
    SessionPublic,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)

from app.services.adaptive import (
    difficulty_level_to_target,
    difficulty_target,
    next_difficulty_level,
    pick_best_question,
    update_ability,
)

from app.services.llm import llm_study_plan, evaluate_answer

router = APIRouter()


def _oid(s: str) -> ObjectId:
    try:
        return ObjectId(s)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid id") from e


def _public_question(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(doc["_id"]),
        "question": doc["question"],
        "options": doc["options"],
        "difficulty": float(doc["difficulty"]),
        "topic": doc["topic"],
        "tags": doc.get("tags", []),
    }


def _public_session(doc: dict[str, Any]) -> SessionPublic:
    return SessionPublic(
        id=str(doc["_id"]),
        ability=float(doc["ability"]),
        answered_count=int(doc.get("answered_count", 0)),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        study_plan=doc.get("study_plan"),
        difficulty_level=str(doc.get("difficulty_level"))
        if doc.get("difficulty_level")
        else None,
    )


async def _create_session() -> dict[str, Any]:
    db = get_db()

    now = utc_now()

    session_doc = {
        "ability": 0.5,
        "difficulty_level": "medium",
        "answered_count": 0,
        "asked_question_ids": [],
        "answers": [],
        "topic_stats": {},
        "study_plan": None,
        "created_at": now,
        "updated_at": now,
    }

    res = await db.user_sessions.insert_one(session_doc)

    session_doc["_id"] = res.inserted_id

    return session_doc


async def _find_next_question(session_doc: dict[str, Any]) -> dict[str, Any] | None:

    db = get_db()

    level = session_doc.get("difficulty_level")

    if level:
        target = difficulty_level_to_target(str(level))
    else:
        target = difficulty_target(float(session_doc["ability"]))

    asked = session_doc.get("asked_question_ids", [])

    base_filter: dict[str, Any] = {}

    if asked:
        base_filter["_id"] = {
            "$nin": [ObjectId(x) if isinstance(x, str) else x for x in asked]
        }

    window = 0.2
    min_d = max(0.1, round(target - window, 1))
    max_d = min(1.0, round(target + window, 1))

    cursor = db.questions.find(
        {**base_filter, "difficulty": {"$gte": min_d, "$lte": max_d}}, limit=50
    )

    candidates = await cursor.to_list(length=50)

    if not candidates:
        cursor2 = db.questions.find(base_filter, limit=50)
        candidates = await cursor2.to_list(length=50)

    return pick_best_question(candidates, target)


@router.get("/next-question", response_model=NextQuestionResponse)
async def next_question(session_id: str | None = Query(default=None)):

    db = get_db()

    if session_id:
        session_doc = await db.user_sessions.find_one({"_id": _oid(session_id)})

        if not session_doc:
            raise HTTPException(status_code=404, detail="Session not found")

    else:
        session_doc = await _create_session()

    q = await _find_next_question(session_doc)

    return NextQuestionResponse(
        session=_public_session(session_doc),
        question=_public_question(q) if q else None,
    )


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(payload: SubmitAnswerRequest):

    db = get_db()

    session_doc = await db.user_sessions.find_one({"_id": _oid(payload.session_id)})

    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")

    qdoc = await db.questions.find_one({"_id": _oid(payload.question_id)})

    if not qdoc:
        raise HTTPException(status_code=404, detail="Question not found")

    # AI answer evaluation
    score, feedback = await evaluate_answer(
        question_text=str(qdoc.get("question", "")),
        user_answer=str(payload.selected_answer),
        correct_answer=str(qdoc.get("correct_answer", "")),
    )

    correct = str(payload.selected_answer).strip() == str(qdoc["correct_answer"]).strip()

    new_ability = update_ability(float(session_doc["ability"]), correct)

    current_level = str(session_doc.get("difficulty_level", "medium"))

    next_level = next_difficulty_level(current_level, score)

    topic = qdoc.get("topic", "unknown")

    topic_stats = session_doc.get("topic_stats") or {}

    st = topic_stats.get(topic) or {"attempted": 0, "correct": 0}

    st["attempted"] += 1

    if correct:
        st["correct"] += 1

    topic_stats[topic] = st

    asked_ids = session_doc.get("asked_question_ids") or []

    if str(qdoc["_id"]) not in {str(x) for x in asked_ids}:
        asked_ids.append(qdoc["_id"])

    answers = session_doc.get("answers") or []

    answers.append(
        {
            "question_id": qdoc["_id"],
            "selected_answer": payload.selected_answer,
            "correct": correct,
            "score": score,
            "feedback": feedback,
            "topic": topic,
            "difficulty": float(qdoc["difficulty"]),
            "ts": utc_now(),
        }
    )

    answered_count = int(session_doc.get("answered_count", 0)) + 1

    update_doc = {
        "$set": {
            "ability": new_ability,
            "answered_count": answered_count,
            "asked_question_ids": asked_ids,
            "answers": answers,
            "topic_stats": topic_stats,
            "difficulty_level": next_level,
            "updated_at": utc_now(),
        }
    }

    await db.user_sessions.update_one({"_id": session_doc["_id"]}, update_doc)

    session_doc = await db.user_sessions.find_one({"_id": session_doc["_id"]})

    if not session_doc:
        raise HTTPException(status_code=500, detail="Session update failed")

    study_plan = session_doc.get("study_plan")

    # 🔥 Generate study plan after 10 answers
    if answered_count >= 10 and not study_plan:

        perf_payload = {
            "ability": float(session_doc["ability"]),
            "answered_count": answered_count,
            "topic_stats": topic_stats,
            "recent_answers": [
                {
                    "topic": a["topic"],
                    "difficulty": a["difficulty"],
                    "correct": a["correct"],
                }
                for a in answers[-10:]
            ],
        }

        study_plan = await llm_study_plan(perf_payload)

        await db.user_sessions.update_one(
            {"_id": session_doc["_id"]},
            {"$set": {"study_plan": study_plan, "updated_at": utc_now()}},
        )

        session_doc["study_plan"] = study_plan

    next_q = await _find_next_question(session_doc)

    return SubmitAnswerResponse(
        correct=correct,
        new_ability=new_ability,
        session=_public_session(session_doc),
        next_question=_public_question(next_q) if next_q else None,
        study_plan=study_plan,
        feedback=feedback,
        score=score,
    )