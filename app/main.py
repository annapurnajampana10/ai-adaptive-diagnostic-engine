from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.mongo import init_db
from app.routes.diagnostic import router as diagnostic_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="AI-Driven Adaptive Diagnostic Engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diagnostic_router)

@app.get("/")
async def root():
    return {"message": "AI-Driven Adaptive Diagnostic Engine is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

