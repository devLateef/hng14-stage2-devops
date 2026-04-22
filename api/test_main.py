import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, is_valid_uuid


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_redis(mocker):
    """Mock Redis client."""
    mock = MagicMock()
    mock.ping.return_value = True
    mocker.patch('main.r', mock)
    return mock


class TestValidation:
    """Test input validation functions."""

    def test_is_valid_uuid_with_valid_uuid(self):
        """Test that valid UUIDs are correctly identified."""
        valid_uuid = str(uuid.uuid4())
        assert is_valid_uuid(valid_uuid) is True

    def test_is_valid_uuid_with_invalid_uuid(self):
        """Test that invalid UUIDs are correctly rejected."""
        assert is_valid_uuid("not-a-uuid") is False
        assert is_valid_uuid("12345") is False
        assert is_valid_uuid("") is False

    def test_is_valid_uuid_with_none(self):
        """Test that None is correctly rejected."""
        assert is_valid_uuid(None) is False


class TestJobCreation:
    """Test job creation endpoint."""

    def test_create_job_success(self, client, mock_redis):
        """Test successful job creation."""
        mock_redis.lpush.return_value = 1
        mock_redis.hset.return_value = 1

        response = client.post("/jobs")

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert is_valid_uuid(data["job_id"]) is True
        mock_redis.lpush.assert_called_once()
        mock_redis.hset.assert_called_once()

    def test_create_job_redis_error(self, client, mock_redis):
        """Test job creation with Redis error."""
        import redis
        mock_redis.lpush.side_effect = redis.RedisError("Connection failed")

        response = client.post("/jobs")

        assert response.status_code == 500


class TestJobRetrieval:
    """Test job status retrieval endpoint."""

    def test_get_job_with_valid_uuid(self, client, mock_redis):
        """Test retrieving job status with valid UUID."""
        job_id = str(uuid.uuid4())
        mock_redis.hgetall.return_value = {
            "status": "queued",
            "created_at": "2024-01-01T00:00:00"
        }

        response = client.get(f"/jobs/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_get_job_with_invalid_uuid(self, client):
        """Test retrieving job status with invalid UUID."""
        response = client.get("/jobs/not-a-uuid")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid job ID format" in data["detail"]

    def test_get_job_not_found(self, client, mock_redis):
        """Test retrieving non-existent job."""
        job_id = str(uuid.uuid4())
        mock_redis.hgetall.return_value = {}

        response = client.get(f"/jobs/{job_id}")

        assert response.status_code == 404
