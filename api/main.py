from fastapi import FastAPI, HTTPException
import redis
import uuid
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)
    r.ping()
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    raise

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

@app.post("/jobs")
def create_job():
    try:
        job_id = str(uuid.uuid4())
        r.lpush("job", job_id)
        r.hset(f"job:{job_id}", "status", "queued")
        logger.info(f"Job created: {job_id}")
        return {"job_id": job_id}
    except redis.RedisError as e:
        logger.error(f"Redis error while creating job: {e}")
        raise HTTPException(status_code=500, detail="Failed to create job")
    except Exception as e:
        logger.error(f"Unexpected error while creating job: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        if not is_valid_uuid(job_id):
            logger.warning(f"Invalid job_id format: {job_id}")
            raise HTTPException(status_code=400, detail="Invalid job ID format")
        status = r.hget(f"job:{job_id}", "status")
        if not status:
            logger.warning(f"Job not found: {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")
        logger.info(f"Retrieved status for job {job_id}: {status.decode()}")
        return {"job_id": job_id, "status": status.decode()}
    except redis.RedisError as e:
        logger.error(f"Redis error while retrieving job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error while retrieving job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
