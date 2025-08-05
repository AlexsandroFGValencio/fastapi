FROM python:3.13-alpine

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --editable .

# Executa via python -m para evitar problemas de PATH
ENTRYPOINT ["python", "-m", "src.main"]