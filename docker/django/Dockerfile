FROM python:3.12-slim


# create a non-root user
RUN addgroup --system django && adduser --system --ingroup django django

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY backend/ ./

# Change ownership to non-root user
RUN chown -R django:django /app

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Entrypoint (runs migrations + Gunicorn)
ENTRYPOINT ["/app/entrypoint.sh"]
