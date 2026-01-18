# ============================================
# ⚡ MistralMeter - Backend API
# Production-ready FastAPI container
# ============================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="Malek Gatoufi"
LABEL description="MistralMeter API - LLM Evaluation Platform"
LABEL version="2.0.0"

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create non-root user for security
RUN groupadd -r mistral && useradd -r -g mistral mistral

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY datasets/ ./datasets/

# Change ownership
RUN chown -R mistral:mistral /app

# Switch to non-root user
USER mistral

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
