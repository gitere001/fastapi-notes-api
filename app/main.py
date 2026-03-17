from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
)


@app.get("/")
def root():
    return {"message": "FastAPI Notes API is running"}


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV}
