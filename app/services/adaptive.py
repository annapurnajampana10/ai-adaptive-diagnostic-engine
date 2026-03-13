from __future__ import annotations

import random
from typing import Any


def clamp_ability(x: float) -> float:
    return max(0.1, min(1.0, round(x, 1)))


def update_ability(current: float, correct: bool) -> float:
    delta = 0.1 if correct else -0.1
    return clamp_ability(current + delta)


def difficulty_target(ability: float) -> float:
    return clamp_ability(ability)


def pick_best_question(candidates: list[dict[str, Any]], target: float) -> dict[str, Any] | None:
    if not candidates:
        return None
    scored = sorted(
        candidates,
        key=lambda q: (abs(float(q.get("difficulty", 0.5)) - target), random.random()),
    )
    return scored[0]


DIFFICULTY_LEVELS: tuple[str, ...] = ("easy", "medium", "hard")


def next_difficulty_level(current: str, score: float) -> str:
    """
    Determine the next difficulty level based on the score.

    Rules:
      - If score > 0.7 → move to harder difficulty
      - If score < 0.4 → move to easier difficulty
      - Otherwise → keep same difficulty.
    """
    current = (current or "medium").lower()
    if current not in DIFFICULTY_LEVELS:
        current = "medium"

    idx = DIFFICULTY_LEVELS.index(current)
    if score > 0.7 and idx < len(DIFFICULTY_LEVELS) - 1:
        idx += 1
    elif score < 0.4 and idx > 0:
        idx -= 1
    return DIFFICULTY_LEVELS[idx]


def difficulty_level_to_target(level: str) -> float:
    """
    Map a named difficulty level to a numeric difficulty target in [0.1, 1.0].
    """
    mapping = {
        "easy": 0.3,
        "medium": 0.5,
        "hard": 0.8,
    }
    return float(mapping.get((level or "medium").lower(), 0.5))

