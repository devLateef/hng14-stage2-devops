import pytest
import uuid
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import sys
import os

# -------------------------
# SAFE IMPORT PATH
# -------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from main import app, is_valid_uuid


# -------------------------
# CLIENT FIXTURE
# -------------------------
@pytest.fixture
def client():
    return TestClient(app)


# -------------------------
# REDIS MOCK FIXTURE (CLEAN RESET SAFE)
# -------------------------
@pytest.fixture(autouse=True)
def mock_redis():
    mock = MagicMock()
    mock.ping.return_value = True

    main.r = mock  # patch redis instance

    yield mock

    # cleanup after each test
    main.r = None


# -------------------------
# VALIDATION TESTS
# -------------------------
class TestValidation:

    def test_is_valid_uuid_with_valid_uuid(self):
        assert is_valid_uuid(str(uuid.uuid4())) is True

    def test_is_valid_uuid_with_invalid_uuid(self):
        assert is_valid_uuid("not-a-uuid") is False
        assert is_valid_uuid("123") is False

    def test_is_valid_uuid_with_none(self):
        assert is_valid_uuid(None) is False


# -------------------------
# JOB CREATION
# -------------------------
class TestJobCreation:

    def test_create_job_success(self, client, mock_redis):
        mock_redis.lpush.return_value = 1
        mock_redis.hset.return_value = 1

        response = client.post("/jobs")

        assert response.status_code == 200
        data = response.json()

        assert "job_id" in data
        assert is_valid_uuid(data["job_id"])

        mock_redis.lpush.assert_called_once()
        mock_redis.hset.assert_called_once()

    def test_create_job_redis_error(self, client, mock_redis):
        import redis
        mock_redis.lpush.side_effect = redis.RedisError("fail")

        response = client.post("/jobs")

        assert response.status_code == 500


# -------------------------
# JOB RETRIEVAL
# -------------------------
class TestJobRetrieval:

    def test_get_job_success(self, client, mock_redis):
        job_id = str(uuid.uuid4())
        mock_redis.hget.return_value = "queued"

        response = client.get(f"/jobs/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"

    def test_get_job_invalid_uuid(self, client):
        response = client.get("/jobs/bad-id")

        assert response.status_code == 400

    def test_get_job_not_found(self, client, mock_redis):
        job_id = str(uuid.uuid4())
        mock_redis.hget.return_value = None

        response = client.get(f"/jobs/{job_id}")

        assert response.status_code == 404