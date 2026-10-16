"""
Background Worker Service
=========================
Consumes async jobs from Redis queue (e.g. batch summarization of case notes),
queries the AI service, and persists the generated insights to PostgreSQL.
"""

import json
import logging
import os
import time
import httpx
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, CaseNote

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BackgroundWorker")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app_user:app_password@postgres:5432/app_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def process_summarization(case_id: int):
    """Fetch case, invoke AI model, and save summary."""
    session = SessionLocal()
    try:
        case = session.query(CaseNote).filter(CaseNote.id == case_id).first()
        if not case:
            logger.warning(f"Case {case_id} not found in database.")
            return

        logger.info(f"Generating summary for Case {case_id} ({case.client_pseudonym})...")
        prompt = f"Please write a concise 2-sentence clinical/administrative summary for the following case note: {case.content}"

        with httpx.Client(timeout=60.0) as client:
            res = client.post(
                f"{AI_SERVICE_URL}/v1/chat/completions",
                json={
                    "model": "llama-3.1-8b-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            if res.status_code == 200:
                summary_text = res.json()["choices"][0]["message"]["content"]
                case.summary = summary_text.strip()
                case.status = "summarized"
                session.commit()
                logger.info(f"Successfully updated summary for Case {case_id}")
            else:
                logger.error(f"AI service returned error: {res.status_code} {res.text}")
    except Exception as exc:
        logger.error(f"Error processing task for case {case_id}: {exc}")
    finally:
        session.close()


def main():
    """Main worker loop listening on Redis task_queue."""
    logger.info("Connecting to Redis queue...")
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

    while True:
        try:
            # Blocking pop with timeout of 5 seconds
            task_item = r.blpop("task_queue", timeout=5)
            if task_item:
                _, payload_str = task_item
                payload = json.loads(payload_str)
                task_name = payload.get("task")
                if task_name == "summarize":
                    case_id = payload.get("case_id")
                    process_summarization(case_id)
        except redis.ConnectionError:
            logger.warning("Redis connection lost. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected worker exception: {e}")
            time.sleep(2)


if __name__ == "__main__":
    main()
