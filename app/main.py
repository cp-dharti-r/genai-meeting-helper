from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.meetings import router as meetings_router
from app.api.events import router as events_router
from app.utils.config import WEB_ORIGIN
from app.services.scheduler import start_scheduler

app = FastAPI(title="GenAI Meeting Helper", version="0.1.0")

# CORS configuration - allow all localhost origins
# Note: Cannot use "*" with allow_credentials=True, so we list specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        WEB_ORIGIN,
    ] if WEB_ORIGIN else [
        "http://localhost:8080",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,  # Set to False to allow wildcard, or True with specific origins
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handlers to ensure CORS headers are always included
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Ensure CORS headers on HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Ensure CORS headers on validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Ensure CORS headers on all exceptions"""
    from loguru import logger
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/")
def root():
    return {"status": "ok", "app": "genai-meeting-helper"}

@app.get("/health")
def health():
    return {"healthy": True}

app.include_router(meetings_router)
app.include_router(events_router)

# start background scheduler for rolling summaries
start_scheduler()
