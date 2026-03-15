FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/library

CMD ["uvicorn", "lab3.main:app", "--host", "0.0.0.0", "--port", "8000"]

