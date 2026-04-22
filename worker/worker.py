import redis
import time
import os
import logging
from typing import Optional, Tuple, cast


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))


def get_redis():
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

    raise Exception("Could not connect to Redis")


r = get_redis()


def process_job(job_id):
    try:
        logger.info(f"Processing job {job_id}")
        time.sleep(2)

        r.hset(f"job:{job_id}", "status", "completed")

        logger.info(f"Job {job_id} completed")

    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")

        try:
            r.hset(f"job:{job_id}", "status", "failed")
        except Exception:
            pass


def main():
    while True:
        try:
            job: Optional[Tuple[str, str]] = cast(
                Optional[Tuple[str, str]],
                r.brpop(["jobs"], timeout=5)
            )

            if job:
                _, job_id = job
                process_job(job_id)

        except Exception as e:
            logger.error(f"Worker loop error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
