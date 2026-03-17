from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router
from app.db import registry  # noqa: F401

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "FastAPI Notes API is running"}


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV}
