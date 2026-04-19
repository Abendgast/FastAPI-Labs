"""Мінімальне FastAPI для деплою (без БД — менше налаштувань на хості)."""
from fastapi import FastAPI

app = FastAPI(title="Самостійна робота — API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "API працює", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
