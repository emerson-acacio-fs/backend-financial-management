FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .[dev]

COPY . .

RUN chmod +x docker/start.sh

CMD ["./docker/start.sh"]
