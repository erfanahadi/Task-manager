# =========================
# Builder stage
# =========================
FROM python:3.12-slim AS builder

# Create a non-root user
RUN addgroup --system django && adduser --system --ingroup django django

WORKDIR /app

# Install system dependencies needed for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------
# Install base dependencies (core/prod) in builder
# -------------------------
COPY backend/requirements-base.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements-base.txt

# -------------------------
# Install dev dependencies (optional, testing)
# -------------------------
COPY backend/requirements-dev.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements-dev.txt || true

# Copy project code
COPY backend/ ./

# =========================
# Runtime stage
# =========================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create non-root user
RUN addgroup --system django && adduser --system --ingroup django django

# Install only system runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy built wheels from builder
COPY --from=builder /wheels /wheels
COPY backend/requirements-base.txt .
COPY backend/requirements-dev.txt .

# Install wheels (no network access needed)
RUN pip install --no-cache-dir /wheels/*

# Copy project code
COPY backend/ ./

# Change ownership to non-root user
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Entrypoint (migrations + Gunicorn)
ENTRYPOINT ["/app/entrypoint.sh"]
