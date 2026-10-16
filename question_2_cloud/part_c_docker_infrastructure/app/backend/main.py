"""
FastAPI Backend Application
===========================
Provides REST endpoints for:
- Health checking (/health)
- Confidential Case Note Management (/api/cases)
- Async Background Processing submission (/api/cases/{id}/summarize)
- Real-time LLM Query Proxy to Llama 3.1 (/api/ask)
"""

import json
import logging
import os
from typing import List, Optional
import httpx
import redis
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models import Base, CaseNote

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BackendAPI")

# Environment configurations
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app_user:app_password@postgres:5432/app_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")

# Database setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis client for worker queue
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Could not connect to Redis immediately: {e}")
    redis_client = None

app = FastAPI(
    title="AI Case Management API",
    description="Backend service managing sensitive case notes and orchestrating Llama 3.1 AI queries.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database tables on service launch."""
    logger.info("Initializing database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error initializing DB schema: {e}")


def get_db():
    """Yield database session with safe closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic Schemas
class CaseNoteCreate(BaseModel):
    client_pseudonym: str = Field(..., example="Client-8492")
    category: str = Field(..., example="Housing Support")
    content: str = Field(..., example="Client completed vocational training program.")


class CaseNoteResponse(BaseModel):
    id: int
    client_pseudonym: str
    category: str
    content: str
    summary: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    prompt: str = Field(..., example="Summarize recent developments for housing assistance cases.")


class QueryResponse(BaseModel):
    prompt: str
    response: str
    model: str


# Endpoints
@app.get("/health", tags=["Monitoring"])
def health_check(db: Session = Depends(get_db)):
    """Check connectivity to DB and Redis."""
    db_status = "ok"
    redis_status = "ok"

    try:
        db.execute("SELECT 1")
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    if redis_client:
        try:
            redis_client.ping()
        except Exception as e:
            redis_status = f"unhealthy: {str(e)}"
    else:
        redis_status = "disconnected"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "redis": redis_status,
    }


@app.post("/api/cases", response_model=CaseNoteResponse, status_code=status.HTTP_201_CREATED, tags=["Cases"])
def create_case(case_in: CaseNoteCreate, db: Session = Depends(get_db)):
    """Record a new confidential case note."""
    new_case = CaseNote(
        client_pseudonym=case_in.client_pseudonym,
        category=case_in.category,
        content=case_in.content,
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    # Queue background task for automated AI summary
    if redis_client:
        try:
            redis_client.rpush("task_queue", json.dumps({"task": "summarize", "case_id": new_case.id}))
            logger.info(f"Queued background summarization for case {new_case.id}")
        except Exception as e:
            logger.warning(f"Failed to enqueue task: {e}")

    return new_case


@app.get("/api/cases", response_model=List[CaseNoteResponse], tags=["Cases"])
def list_cases(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List case notes with pagination."""
    return db.query(CaseNote).offset(skip).limit(limit).all()


@app.post("/api/ask", response_model=QueryResponse, tags=["AI Inference"])
async def ask_ai(request: QueryRequest):
    """Forward user inquiry to the Llama 3.1 AI microservice."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            ai_res = await client.post(
                f"{AI_SERVICE_URL}/v1/chat/completions",
                json={
                    "model": "llama-3.1-8b-instruct",
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI assistant supporting case managers."},
                        {"role": "user", "content": request.prompt},
                    ],
                },
            )
            if ai_res.status_code != 200:
                raise HTTPException(status_code=502, detail="Error from AI inference service")

            ai_data = ai_res.json()
            answer = ai_data["choices"][0]["message"]["content"]
            return QueryResponse(
                prompt=request.prompt,
                response=answer,
                model="llama-3.1-8b-instruct",
            )
    except httpx.RequestError as exc:
        logger.error(f"Failed to connect to AI engine at {AI_SERVICE_URL}: {exc}")
        raise HTTPException(
            status_code=503,
            detail="AI inference engine temporarily unavailable. Please retry in a few moments.",
        )
