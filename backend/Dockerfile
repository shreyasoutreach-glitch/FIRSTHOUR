FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Seed on container start (idempotent -- wipes and rebuilds the deterministic
# universe every time) then serve. For a persistent Postgres deployment where
# you don't want to reseed on every restart, override the command.
CMD ["sh", "-c", "python -m seed.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
