#!/usr/bin/env bash
# Integration test: submit a job and poll until completed
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
TIMEOUT="${TIMEOUT:-60}"
POLL_INTERVAL=2

echo "==> Waiting for API to be ready at $API_URL ..."
deadline=$((SECONDS + TIMEOUT))
until curl -sf "$API_URL/health" > /dev/null; do
  if [ $SECONDS -ge $deadline ]; then
    echo "ERROR: API did not become ready within ${TIMEOUT}s"
    exit 1
  fi
  sleep "$POLL_INTERVAL"
done
echo "==> API is ready"

echo "==> Submitting job ..."
RESPONSE=$(curl -sf -X POST "$API_URL/jobs")
JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
echo "==> Job submitted: $JOB_ID"

echo "==> Polling job status ..."
deadline=$((SECONDS + TIMEOUT))
while true; do
  if [ $SECONDS -ge $deadline ]; then
    echo "ERROR: Job $JOB_ID did not complete within ${TIMEOUT}s"
    exit 1
  fi
  STATUS=$(curl -sf "$API_URL/jobs/$JOB_ID" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  echo "    status: $STATUS"
  if [ "$STATUS" = "completed" ]; then
    echo "==> Job completed successfully"
    exit 0
  fi
  sleep "$POLL_INTERVAL"
done
