FROM python:3.12-slim@sha256:57cd7c3a7a273101a6485ba99423ee568157882804b1124b4dd04266317710de

# Schema-compatible certification stage label; forces a distinct immutable digest for rollback drills.
LABEL org.opencontainers.image.title="arrivia-recs" \
      org.opencontainers.image.revision="candidate-c2" \
      arrivia.certification.stage="candidate"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

COPY pyproject.toml README.md requirements.lock requirements-build.lock ./
COPY src ./src

RUN pip install --no-cache-dir -r requirements-build.lock \
    && pip install --no-cache-dir -r requirements.lock \
    && pip install --no-cache-dir --no-build-isolation --no-deps . \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=4)"

CMD ["python", "-m", "uvicorn", "arrivia_recs.main:app", "--host", "0.0.0.0", "--port", "8080"]
