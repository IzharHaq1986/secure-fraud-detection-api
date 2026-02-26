# Use a slim, secure Python base image
FROM python:3.14-slim-bookworm

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure stdout/stderr are unbuffered
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Copy dependency files first (better Docker layer caching)
COPY requirements.lock.txt ./requirements.lock.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.lock.txt

# Copy application source
COPY app ./app

# Expose API port
EXPOSE 8000

# Default command (production ASGI server)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
