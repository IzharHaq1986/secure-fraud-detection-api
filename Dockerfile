# syntax=docker/dockerfile:1

# -----------------------------------------------------------------------------
# Dockerfile
#
# Goal:
# - Reduce OS-level CVE surface by using a distroless runtime image.
# - Keep the runtime image minimal (no shell, no package manager).
# - Install Python dependencies in a build stage and copy only what is needed.
#
# Notes:
# - CI currently uses Python 3.11, so the build stage aligns to Python 3.11.
# - distroless/python3-debian12 provides a hardened Python runtime.
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Build stage: install Python dependencies into a portable directory (/install)
# -----------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Install dependencies first to maximize Docker layer cache reuse
COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir --prefix=/install -r /app/requirements.txt

# Copy application code after dependencies are installed
COPY app /app/app


# -----------------------------------------------------------------------------
# Runtime stage: distroless (minimal attack surface)
# -----------------------------------------------------------------------------
FROM gcr.io/distroless/python3-debian12:nonroot

WORKDIR /app

# Copy installed Python packages and entrypoints (uvicorn, etc.)
COPY --from=builder /install /usr/local

# Copy application code
COPY --from=builder /app/app /app/app

# Ensure the application package is discoverable
ENV PYTHONPATH=/app:/usr/local/lib/python3.11/site-packages

# FastAPI entrypoint
# - Use module execution so uvicorn resolves from /usr/local/bin
# - Bind to all interfaces for container networking
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["/usr/bin/python3.11","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).read()"]

CMD ["-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
