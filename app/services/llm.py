from __future__ import annotations

from typing import Any, Tuple
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def _weak_topics_from_stats(topic_stats: dict[str, dict[str, int]], top_k: int = 3) -> list[str]:
    scored: list[tuple[str, float]] = []

    for topic, st in topic_stats.items():
        attempted = max(1, int(st.get("attempted", 0)))
        correct = int(st.get("correct", 0))

        accuracy = correct / attempted
        scored.append((topic, accuracy))

    scored.sort(key=lambda x: x[1])

    return [t for t, _ in scored[:top_k]] if scored else []


def heuristic_study_plan(topic_stats: dict[str, dict[str, int]]) -> list[str]:

    weak = _weak_topics_from_stats(topic_stats)

    if not weak:
        return [
            "Review the questions you missed and understand the correct reasoning.",
            "Practice medium difficulty questions across all topics.",
            "Take another timed mini diagnostic test to measure improvement.",
        ]

    return [
        f"Focus on weak topics: {', '.join(weak)}. Review core concepts and formulas.",
        f"Practice 20 targeted questions on {weak[0]} and review every mistake.",
        "Finish with a mixed mini-test and monitor topic-wise accuracy.",
    ]


async def llm_study_plan(payload: dict[str, Any]) -> list[str]:
    """
    Generate a 3-step personalized study plan.
    Uses OpenAI if API key exists, otherwise uses heuristic plan.
    """

    topic_stats = payload.get("topic_stats") or {}

    if not settings.openai_api_key:
        return heuristic_study_plan(topic_stats)

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        prompt = (
            "You are an expert tutor. Based on the student's diagnostic test results, "
            "generate a concise 3-step personalized study plan.\n\n"
            f"Performance data:\n{payload}"
        )

        resp = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "Return ONLY a JSON array with exactly 3 short study steps."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        content = (resp.choices[0].message.content or "").strip()

        import json

        plan = json.loads(content)

        if isinstance(plan, list) and len(plan) == 3:
            return plan

    except Exception:
        pass

    return heuristic_study_plan(topic_stats)


async def evaluate_answer(
    question_text: str,
    user_answer: str,
    correct_answer: str | None = None,
) -> Tuple[float, str]:

    """
    Evaluate student answer.

    Returns:
        score (0.0–1.0)
        feedback text
    """

    try:
        # If correct answer is available, compare directly
        if correct_answer:
            correct = correct_answer.strip().lower()
            answer = user_answer.strip().lower()

            if answer == correct:
                return 1.0, "Correct answer."
            else:
                return 0.0, "Incorrect answer."

        # If correct answer not provided
        return 0.5, "Answer received, but no reference answer available."

    except Exception as e:
        print("Evaluation error:", e)

        # Fallback heuristic
        if correct_answer:
            correct = correct_answer.strip().lower()
            answer = user_answer.strip().lower()

            if answer == correct:
                return 1.0, "Correct answer."
            else:
                return 0.0, "Incorrect answer."

        return 0.5, "Could not evaluate answer."

    # Heuristic evaluation when OpenAI API not configured
    if not settings.openai_api_key:

        answer = (user_answer or "").strip().lower()

        if not answer:
            return 0.0, "You did not provide an answer."

        if correct_answer:

            correct = correct_answer.strip().lower()

            if answer == correct:
                return 1.0, "Correct answer."

            if correct in answer:
                return 0.8, "Mostly correct but explanation could be clearer."

            return 0.0, "Incorrect answer. Review the concept and try again."

        return 0.5, "Answer recorded but reference answer not available."

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        system_message = (
            "You are an expert tutor grading a diagnostic test answer.\n"
            "Return JSON only: {\"score\": number_between_0_and_1, \"feedback\": \"short explanation\"}"
        )

        user_prompt = f"""
Question:
{question_text}

Correct Answer:
{correct_answer}

Student Answer:
{user_answer}
"""

        resp = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        content = (resp.choices[0].message.content or "").strip()

        import json

        data = json.loads(content)

        score = float(data.get("score", 0.0))
        score = max(0.0, min(1.0, score))

        feedback = str(data.get("feedback") or "").strip()

        if not feedback:
            feedback = "Your answer has been evaluated."

        return score, feedback

    except Exception as e:

        logger.exception("LLM evaluation failed: %s", e)

        answer = (user_answer or "").strip()

        if not answer:
            return 0.0, "You did not provide an answer."

        return (
            0.5,
            "AI evaluation temporarily failed, so a default score was assigned.",
        )