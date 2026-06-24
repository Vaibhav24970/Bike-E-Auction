# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Base — Python + system deps
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

# Install system deps (psycopg2 build deps + dumb-init for signal handling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    dumb-init \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Dependencies — install Python packages
# ─────────────────────────────────────────────────────────────────────────────
FROM base AS deps

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: Production — minimal runtime image
# ─────────────────────────────────────────────────────────────────────────────
FROM base AS production

# Create non-root user
RUN useradd --system --create-home --shell /bin/bash appuser

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Create uploads directory for local storage driver
RUN mkdir -p uploads && chown appuser:appuser uploads

USER appuser

EXPOSE 8000

# Healthcheck — Docker will mark container unhealthy if this fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use dumb-init for proper PID 1 signal handling
ENTRYPOINT ["dumb-init", "--"]

# Run uvicorn directly (DB tables auto-create on startup)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
