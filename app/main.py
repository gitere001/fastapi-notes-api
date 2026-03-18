from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.router import api_router
from app.db import registry  # noqa: F401
from app.db.redis import connect_redis, disconnect_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_redis()
    yield
    await disconnect_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    first_error = errors[0]
    field = first_error["loc"][-1]
    message = (
        f"{field} is required"
        if first_error["type"] == "missing"
        else first_error["msg"]
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": message},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )


@app.get("/")
def root():
    return {"message": "FastAPI Notes API is running"}


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV}
