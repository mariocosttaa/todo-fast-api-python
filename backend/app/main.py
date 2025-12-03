from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import web
from app.utilis.logger import setup_logging, get_logger
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Setup logging first
setup_logging()
logger = get_logger(__name__)

# Load .env from project root (one shared config for backend & frontend)
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title=os.getenv("APP_NAME", "Todo FastAPI"),
    description="A FastAPI-based Todo application with authentication",
    version="1.0.0"
)

# CORS middleware (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware - logs all requests like Laravel
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get client IP
    client_ip = request.client.host if request.client else "Unknown"
    
    # Log incoming request
    logger.info(
        f"[REQUEST] {request.method} {request.url.path} - "
        f"IP: {client_ip} - "
        f"Query: {dict(request.query_params)}"
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log successful response
        logger.info(
            f"[RESPONSE] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"IP: {client_ip}"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"[ERROR] {request.method} {request.url.path} - "
            f"Exception: {str(e)} - "
            f"Time: {process_time:.3f}s - "
            f"IP: {client_ip}",
            exc_info=True
        )
        raise

# Exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"[UNHANDLED EXCEPTION] {request.method} {request.url.path} - {str(exc)}",
        exc_info=True
    )
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Root endpoints (not versioned - for health checks, monitoring)
@app.get("/")
def read_root():
    return {"message": "API ToDo - FastAPI", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

# API v1 routes
app.include_router(web.router, prefix="/api/v1")

logger.info("Application started successfully")

    