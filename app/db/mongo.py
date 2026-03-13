from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        _db = get_client()[settings.mongodb_db]
    return _db


async def init_db() -> None:
    db = get_db()
    # Indexes for faster matching and avoiding repeats
    await db.questions.create_index([("difficulty", 1)])
    await db.questions.create_index([("topic", 1)])
    await db.user_sessions.create_index([("created_at", -1)])
