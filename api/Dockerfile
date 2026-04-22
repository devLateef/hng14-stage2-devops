FROM python:3.10-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.10-slim AS runtime

WORKDIR /app

RUN useradd -m -u 1001 appuser

COPY --from=builder /usr/local /usr/local
COPY . .

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
