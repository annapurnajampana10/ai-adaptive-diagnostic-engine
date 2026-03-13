from __future__ import annotations

import asyncio
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


QUESTIONS: list[dict[str, Any]] = [
    {
        "question": "If x + 3 = 10, what is x?",
        "options": ["5", "6", "7", "8"],
        "correct_answer": "7",
        "difficulty": 0.2,
        "topic": "algebra",
        "tags": ["linear-equations"],
    },
    {
        "question": "Solve: 2x = 18",
        "options": ["7", "8", "9", "10"],
        "correct_answer": "9",
        "difficulty": 0.2,
        "topic": "algebra",
        "tags": ["linear-equations"],
    },
    {
        "question": "What is the slope of the line y = 3x + 2?",
        "options": ["2", "3", "-3", "1/3"],
        "correct_answer": "3",
        "difficulty": 0.4,
        "topic": "algebra",
        "tags": ["functions"],
    },
    {
        "question": "If f(x) = x^2, what is f(4)?",
        "options": ["8", "12", "16", "20"],
        "correct_answer": "16",
        "difficulty": 0.3,
        "topic": "algebra",
        "tags": ["functions"],
    },
    {
        "question": "What is 25% of 80?",
        "options": ["10", "20", "25", "30"],
        "correct_answer": "20",
        "difficulty": 0.2,
        "topic": "arithmetic",
        "tags": ["percentages"],
    },
    {
        "question": "Compute: 7 * 8",
        "options": ["54", "56", "58", "64"],
        "correct_answer": "56",
        "difficulty": 0.1,
        "topic": "arithmetic",
        "tags": ["multiplication"],
    },
    {
        "question": "Compute: 144 / 12",
        "options": ["10", "11", "12", "13"],
        "correct_answer": "12",
        "difficulty": 0.2,
        "topic": "arithmetic",
        "tags": ["division"],
    },
    {
        "question": "Simplify: 3/4 + 1/8",
        "options": ["7/8", "5/8", "3/8", "1/2"],
        "correct_answer": "7/8",
        "difficulty": 0.5,
        "topic": "arithmetic",
        "tags": ["fractions"],
    },
    {
        "question": "Which number is prime?",
        "options": ["21", "27", "29", "33"],
        "correct_answer": "29",
        "difficulty": 0.4,
        "topic": "number-theory",
        "tags": ["primes"],
    },
    {
        "question": "What is the remainder when 47 is divided by 6?",
        "options": ["1", "2", "3", "5"],
        "correct_answer": "5",
        "difficulty": 0.4,
        "topic": "number-theory",
        "tags": ["modular-arithmetic"],
    },
    {
        "question": "If a triangle has sides 3, 4, 5, what type is it?",
        "options": ["Equilateral", "Isosceles", "Right", "Obtuse"],
        "correct_answer": "Right",
        "difficulty": 0.4,
        "topic": "geometry",
        "tags": ["triangles"],
    },
    {
        "question": "What is the area of a circle with radius 3? (Use π ≈ 3.14)",
        "options": ["18.84", "28.26", "31.40", "9.42"],
        "correct_answer": "28.26",
        "difficulty": 0.6,
        "topic": "geometry",
        "tags": ["circles"],
    },
    {
        "question": "What is the sum of interior angles of a triangle?",
        "options": ["90°", "180°", "270°", "360°"],
        "correct_answer": "180°",
        "difficulty": 0.2,
        "topic": "geometry",
        "tags": ["angles"],
    },
    {
        "question": "A bag has 3 red and 2 blue balls. Probability of drawing red?",
        "options": ["2/5", "3/5", "1/2", "2/3"],
        "correct_answer": "3/5",
        "difficulty": 0.5,
        "topic": "probability",
        "tags": ["basic-probability"],
    },
    {
        "question": "If you flip a fair coin twice, probability of exactly one head?",
        "options": ["1/4", "1/2", "3/4", "1"],
        "correct_answer": "1/2",
        "difficulty": 0.6,
        "topic": "probability",
        "tags": ["binomial"],
    },
    {
        "question": "Mean of 2, 4, 6, 8 is:",
        "options": ["4", "5", "6", "7"],
        "correct_answer": "5",
        "difficulty": 0.3,
        "topic": "statistics",
        "tags": ["mean"],
    },
    {
        "question": "Median of 1, 3, 3, 6, 7, 8, 9 is:",
        "options": ["3", "6", "7", "8"],
        "correct_answer": "6",
        "difficulty": 0.5,
        "topic": "statistics",
        "tags": ["median"],
    },
    {
        "question": "Choose the word closest in meaning to 'abundant':",
        "options": ["scarce", "plentiful", "tiny", "rude"],
        "correct_answer": "plentiful",
        "difficulty": 0.3,
        "topic": "vocabulary",
        "tags": ["synonyms"],
    },
    {
        "question": "Choose the word opposite in meaning to 'opaque':",
        "options": ["transparent", "strong", "soft", "loud"],
        "correct_answer": "transparent",
        "difficulty": 0.4,
        "topic": "vocabulary",
        "tags": ["antonyms"],
    },
    {
        "question": "If all A are B and all B are C, then all A are C. This is an example of:",
        "options": ["addition", "transitive reasoning", "circular logic", "guessing"],
        "correct_answer": "transitive reasoning",
        "difficulty": 0.7,
        "topic": "logic",
        "tags": ["syllogisms"],
    },
    {
        "question": "If statement: 'If it rains, the ground is wet.' Contrapositive is:",
        "options": [
            "If the ground is wet, it rains.",
            "If it doesn't rain, the ground isn't wet.",
            "If the ground isn't wet, it didn't rain.",
            "If it rains, the ground isn't wet.",
        ],
        "correct_answer": "If the ground isn't wet, it didn't rain.",
        "difficulty": 0.8,
        "topic": "logic",
        "tags": ["conditionals"],
    },
]


async def main() -> None:
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]

    ops = 0
    for q in QUESTIONS:
        await db.questions.update_one(
            {"question": q["question"]},
            {"$set": q},
            upsert=True,
        )
        ops += 1

    print(f"Seeded/updated {ops} questions into '{settings.mongodb_db}.questions'")
    client.close()


if __name__ == "__main__":
    asyncio.run(main())

