from fastapi import FastAPI, HTTPException
import redis
import uuid
import os
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# -------------------------
# CONFIG
# -------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# -------------------------
# GLOBAL REDIS CLIENT (LAZY SAFE)
# -------------------------
r = None


def get_redis():
    """
    Lazy Redis initializer.
    Ensures:
    - No import-time failure (pytest-safe)
    - Retry logic for Docker startup race conditions
    """
    global r

    if r:
        return r

    retries = 5
    while retries > 0:
        try:
            client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True
            )
            client.ping()
            r = client
            logger.info("Connected to Redis")
            return r

        except redis.ConnectionError:
            retries -= 1
            logger.warning("Redis not ready, retrying...")
            time.sleep(2)

    raise Exception("Could not connect to Redis")


# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------
# VALIDATION
# -------------------------
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except Exception:
        return False


# -------------------------
# CREATE JOB
# -------------------------
@app.post("/jobs")
def create_job():
    try:
        db = get_redis()

        job_id = str(uuid.uuid4())

        db.lpush("jobs", job_id)
        db.hset(f"job:{job_id}", mapping={"status": "queued"})

        logger.info(f"Job created: {job_id}")
        return {"job_id": job_id}

    except redis.RedisError:
        logger.error("Redis error during job creation")
        raise HTTPException(status_code=500, detail="Redis error")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# -------------------------
# GET JOB
# -------------------------
@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        db = get_redis()

        if not is_valid_uuid(job_id):
            raise HTTPException(status_code=400, detail="Invalid job ID format")

        status = db.hget(f"job:{job_id}", "status")

        if not status:
            raise HTTPException(status_code=404, detail="Job not found")

        return {"job_id": job_id, "status": status}

    except redis.RedisError:
        logger.error("Redis error during job retrieval")
        raise HTTPException(status_code=500, detail="Redis error")

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
