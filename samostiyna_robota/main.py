from fastapi import FastAPI

app = FastAPI(title="Task API samostiyna robota", version="1.0.0")

@app.get("/")
def root():
    return {"message": "API gut", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
