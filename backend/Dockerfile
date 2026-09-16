FROM python:3.11-slim

WORKDIR /app

# Copy the whole project before installing - pip needs the actual `app`
# package source present to resolve the pyproject.toml build (this mirrors
# the `pip install .` flow already proven to work in local dev per RUNNING.md).
COPY . .
RUN pip install --no-cache-dir .

EXPOSE 8000
# Render (and most free hosts) assign the port dynamically via $PORT at
# runtime; falling back to 8000 keeps `docker-compose up` working locally.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
