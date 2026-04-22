# Stage 1: Builder
FROM node:18-alpine as builder

WORKDIR /build

COPY package*.json ./
RUN npm ci --only=production


# Stage 2: Runtime
FROM node:18-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy node modules from builder
COPY --from=builder /build/node_modules ./node_modules

# Copy application code
COPY app.js .
COPY views/ ./views/

# Change ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Run application
CMD ["node", "app.js"]
