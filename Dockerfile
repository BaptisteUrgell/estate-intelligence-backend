FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4 /uv /uvx /bin/

WORKDIR /app

# Install dependencies (we copy only the necessary files first to cache this layer)
COPY pyproject.toml ./
# If uv.lock exists, it'll be copied. If not, uv sync will resolve it.
COPY uv.lock* ./

RUN uv sync --no-dev --no-install-project

# Copy project source
COPY . .

# Install project
RUN uv sync --no-dev

# Run application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
