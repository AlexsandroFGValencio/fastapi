FROM python:3.14-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml ./

RUN uv pip install --system fastapi pydantic pydantic-settings sqlalchemy alembic psycopg[binary] \
    "elasticsearch>=8.12.0,<9.0.0" httpx aiohttp jinja2 beautifulsoup4 redis structlog \
    python-jose[cryptography] passlib[bcrypt] python-multipart playwright lxml uvicorn itsdangerous

COPY . .

EXPOSE 8000

CMD ["uvicorn", "trivaxion.main:app", "--host", "0.0.0.0", "--port", "8000"]
