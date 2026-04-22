import redis
import time
import os
import logging
from typing import Optional, Tuple, cast

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)  # type: ignore
    r.ping()
    logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    exit(1)

def process_job(job_id):
    try:
        logger.info(f"Processing job {job_id}")
        time.sleep(2)
        r.hset(f"job:{job_id}", "status", "completed")
        logger.info(f"Job {job_id} completed successfully")
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        try:
            r.hset(f"job:{job_id}", "status", "failed")
        except Exception as inner_e:
            logger.error(f"Failed to update job status: {inner_e}")

while True:
    try:
        job: Optional[Tuple[str, str]] = cast(Optional[Tuple[str, str]], r.brpop(["job"], timeout=5))
        if job is not None:
            _, job_id = job
            process_job(job_id)
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        time.sleep(1)