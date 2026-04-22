# HNG14 Stage 2 DevOps - Job Processing System

A production-ready, containerized job processing system featuring a Node.js frontend, Python FastAPI backend, and worker service communicating via Redis.

## Table of Contents

- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [CI/CD Pipeline](#cicd-pipeline)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                       │
├─────────────┬────────────────┬─────────────┬────────────┤
│  Frontend   │      API       │   Worker    │   Redis    │
│ (Node.js)   │   (FastAPI)    │  (Python)   │            │
│  Port 3000  │   Port 8000    │   (no port) │  (internal)│
└─────────────┴────────────────┴─────────────┴────────────┘
```

### Services

1. **Frontend** (Node.js/Express): User-facing interface for job submission and status tracking
2. **API** (Python/FastAPI): REST endpoints for job creation and status retrieval
3. **Worker** (Python): Background service that processes jobs from the queue
4. **Redis**: In-memory data store and message queue (internal only)

## Prerequisites

### Required Software

- **Docker** (version 20.10+)
- **Docker Compose** (version 1.29+)
- **Git**

### System Requirements

- Minimum 2GB free disk space
- Minimum 2GB available RAM
- Linux, macOS, or Windows (with WSL2/Docker Desktop)

### Optional (for local development without Docker)

- Python 3.11+
- Node.js 18+
- Redis server

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-fork-url>
cd hng14-stage2-devops

# Copy environment template
cp .env.example .env

# Modify if needed (optional for default setup)
# nano .env
```

### 2. Start the Stack

```bash
# Build and start all services
docker-compose up -d

# Wait for services to be ready (usually 10-15 seconds)
sleep 10

# Verify services are running and healthy
docker-compose ps
```

### 3. Test the Application

```bash
# Submit a job
curl -X POST http://localhost:3000/submit

# You'll receive a response like:
# {"job_id": "abc123..."}

# Check job status
curl http://localhost:3000/status/abc123...

# Expected response once job completes:
# {"status": "completed", ...}
```

## Configuration

### Environment Variables

All configuration is managed through environment variables defined in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `redis` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_PASSWORD` | empty | Redis authentication password |
| `API_HOST` | `0.0.0.0` | API binding address |
| `API_PORT` | `8000` | API port |
| `FRONTEND_PORT` | `3000` | Frontend port |
| `API_URL` | `http://api:8000` | API URL for frontend requests |
| `ENVIRONMENT` | `production` | Deployment environment |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### Environment Setup

```bash
# Copy the example file
cp .env.example .env

# Edit with your values (optional)
nano .env

# Note: Do NOT commit .env to git
```

## Running the Application

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View logs from specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f frontend

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Full cleanup (removes volumes)
docker-compose down -v
```

### Individual Service Logs

```bash
# API logs
docker-compose logs api

# Worker logs
docker-compose logs worker

# Frontend logs
docker-compose logs frontend

# Redis logs
docker-compose logs redis
```

### Health Checks

```bash
# Check service health status
docker-compose ps

# Expected output shows all services with status "healthy" or "up"
# Verify with:
docker inspect <container-id> --format='{{.State.Health.Status}}'
```

### Manual Testing

```bash
# Access API documentation
curl http://localhost:8000/docs

# Create a job
curl -X POST http://localhost:8000/jobs

# Get job status
curl http://localhost:8000/jobs/<job_id>

# Submit through frontend
curl -X POST http://localhost:3000/submit \
  -H "Content-Type: application/json" \
  -d '{}'

# Check job status through frontend
curl http://localhost:3000/status/<job_id>
```

## CI/CD Pipeline

The project includes an automated GitHub Actions pipeline that runs on every push and pull request.

### Pipeline Stages

1. **Lint** - Code quality checks
   - Python: flake8
   - JavaScript: ESLint
   - Dockerfiles: hadolint

2. **Test** - Unit tests with coverage
   - Pytest for API (minimum 3 tests)
   - Coverage report generation
   - Redis mocking

3. **Build** - Docker image construction
   - Multi-stage builds
   - Image optimization
   - SHA-based tagging

4. **Security Scan** - Vulnerability detection
   - Trivy scan on all images
   - CRITICAL severity enforcement
   - SARIF report generation

5. **Integration Test** - Full stack validation
   - Docker Compose stack startup
   - Job submission end-to-end test
   - Status polling verification
   - Cleanup on completion/failure

6. **Deploy** - Production deployment (main branch only)
   - Rolling updates
   - Health check validation
   - Automatic rollback on failure

### Triggering the Pipeline

```bash
# Push to any branch (runs lint through integration-test)
git push origin feature-branch

# Push to main (runs full pipeline including deploy)
git push origin main
```

### Viewing Pipeline Results

- GitHub Actions tab in repository
- Individual workflow run details
- Artifact downloads (coverage reports, scan results)

## Project Structure

```
hng14-stage2-devops/
├── .github/
│   └── workflows/
│       └── pipeline.yml           # CI/CD pipeline configuration
├── api/
│   ├── Dockerfile                 # API service container
│   ├── main.py                    # FastAPI application
│   ├── requirements.txt           # Production dependencies
│   ├── requirements-dev.txt       # Development dependencies
│   └── test_main.py              # Unit tests
├── frontend/
│   ├── Dockerfile                 # Frontend service container
│   ├── app.js                     # Express application
│   ├── package.json               # Node.js dependencies
│   └── views/
│       └── index.html             # Frontend UI
├── worker/
│   ├── Dockerfile                 # Worker service container
│   ├── worker.py                  # Job processing logic
│   └── requirements.txt           # Worker dependencies
├── docker-compose.yml             # Multi-container orchestration
├── .env.example                   # Environment variable template
├── .flake8                        # Python linting configuration
├── .eslintrc.json                 # JavaScript linting configuration
├── .hadolintignore                # Dockerfile linting exceptions
├── README.md                      # This file
└── FIXED.md                       # Bug fixes documentation
```

## Troubleshooting

### Services Not Starting

```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs <service-name>

# Restart services
docker-compose restart

# Full reset
docker-compose down -v && docker-compose up -d
```

### Health Check Failures

```bash
# Check health status
docker-compose ps

# Inspect container health
docker inspect <container-id> --format='{{.State.Health}}'

# View health check output
docker inspect <container-id> | grep -A 10 '"Health"'
```

### Port Already in Use

```bash
# Change ports in .env
API_PORT=8001
FRONTEND_PORT=3001

# Restart services
docker-compose down && docker-compose up -d
```

### Redis Connection Issues

```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping

# Check Redis password
echo $REDIS_PASSWORD

# If empty password not working, verify in docker-compose.yml
```

### Memory Issues

```bash
# Check Docker resource usage
docker stats

# Reduce service resource limits in docker-compose.yml if needed
# Restart services
docker-compose down && docker-compose up -d
```

### Tests Failing

```bash
# Run tests locally
cd api
pip install -r requirements-dev.txt
pytest test_main.py -v

# With coverage
pytest test_main.py --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

## Successful Startup Checklist

After `docker-compose up -d`, verify:

```bash
✓ All services show "healthy" or "up" status
  docker-compose ps

✓ API responds with documentation
  curl http://localhost:8000/docs

✓ Frontend responds to requests
  curl http://localhost:3000/

✓ Job creation works
  curl -X POST http://localhost:8000/jobs

✓ Redis is accessible
  docker-compose exec redis redis-cli ping

✓ Worker is processing jobs
  docker-compose logs worker | grep "Processing job"
```

## Common Logs

### API Starting

```
INFO:     Application startup complete [uvicorn]
INFO:     Uvicorn running on http://0.0.0.0:8000
Connected to Redis at redis:6379
```

### Worker Processing

```
INFO - Processing job <uuid>
INFO - Job <uuid> completed successfully
```

### Frontend Starting

```
Frontend running on port 3000
```

## Development

### Running Locally (without Docker)

```bash
# Install dependencies
pip install -r api/requirements.txt
cd frontend && npm install

# Start Redis (in a separate terminal)
redis-server

# Start API
cd api && python main.py

# Start worker (in separate terminal)
cd worker && python worker.py

# Start frontend (in separate terminal)
cd frontend && npm start
```

### Running Tests

```bash
cd api
pip install -r requirements-dev.txt
pytest test_main.py -v --cov
```

### Linting

```bash
# Python
flake8 api/main.py worker/worker.py

# JavaScript
cd frontend && npm install eslint
npx eslint app.js

# Dockerfiles
hadolint api/Dockerfile frontend/Dockerfile worker/Dockerfile
```

## Security Considerations

- All credentials stored in `.env` (never committed)
- Services run as non-root users
- Multi-stage builds eliminate build tools from final images
- Redis not exposed on host machine
- Health checks ensure service readiness
- Trivy scanning detects vulnerabilities

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Express.js Documentation](https://expressjs.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Redis Documentation](https://redis.io/documentation)

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [FIXED.md](FIXED.md) for known bugs and solutions
3. Check GitHub Actions logs for CI/CD issues
4. Review service logs: `docker-compose logs <service>`

## License

[Your License Here]
