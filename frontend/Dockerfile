# Stage 1: Builder
FROM node:18-alpine as builder

WORKDIR /build

COPY package*.json ./
RUN npm ci --only=production


# Stage 2: Runtime
FROM node:18-alpine

WORKDIR /app

# Install curl for healthcheck
RUN apk add --no-cache curl

# Create non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

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
