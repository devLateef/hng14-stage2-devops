import redis
import time
import os
import logging
import signal
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# CONFIG
# -------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# -------------------------
# SAFE REDIS CONNECT
# -------------------------
def connect_redis():
    retries = 5
    while retries > 0:
        try:
            client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True
            )
            client.ping()
            logger.info("Connected to Redis")
            return client
        except redis.ConnectionError:
            retries -= 1
            logger.warning("Redis not ready, retrying...")
            time.sleep(2)

    logger.error("Could not connect to Redis")
    sys.exit(1)


r = connect_redis()

# -------------------------
# GRACEFUL SHUTDOWN
# -------------------------
def shutdown(signum, frame):
    logger.info("Shutting down worker...")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

# -------------------------
# PROCESS JOB
# -------------------------
def process_job(job_id: str):
    try:
        logger.info(f"Processing job {job_id}")
        time.sleep(2)

        r.hset(f"job:{job_id}", "status", "completed")

        logger.info(f"Job {job_id} completed")

    except Exception as e:
        logger.error(f"Job failed {job_id}: {e}")
        r.hset(f"job:{job_id}", "status", "failed")


# -------------------------
# MAIN LOOP
# -------------------------
while True:
    try:
        job = r.brpop("jobs", timeout=5)  # IMPORTANT FIX HERE

        if job:
            _, job_id = job
            process_job(job_id)

    except Exception as e:
        logger.error(f"Worker loop error: {e}")
        time.sleep(1)