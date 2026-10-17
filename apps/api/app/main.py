import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from .config import settings
from .logging import setup_logging, logger
from .errors import (
    ApiException,
    api_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from .routers import health, meta, analyses, chat, trust


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"Disha AI API starting up in mode: {settings.DATA_MODE}")
    yield
    logger.info("Disha AI API shutting down")


app = FastAPI(
    title="Disha AI API",
    description="Location Intelligence & Trustworthy AI Verification Engine",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
origins = settings.cors_origin_list
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Register Exception Handlers
app.add_exception_handler(ApiException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register Routers
app.include_router(health.router)
app.include_router(meta.router)
app.include_router(analyses.router)
app.include_router(chat.router)
app.include_router(trust.router)
