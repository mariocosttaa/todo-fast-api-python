from fastapi import Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.utilis.logger import get_logger

logger = get_logger(__name__)


def _clean_validation_errors(exc: RequestValidationError):
    """Normalize FastAPI / Pydantic validation errors.

    Removes the 'Value error, ' prefix that FastAPI adds when a ValueError is raised
    inside Pydantic validators, keeping only our custom message text.
    """
    errors = []
    for err in exc.errors():
        msg = err.get("msg", "")
        # FastAPI formats ValueError as 'Value error, <our message>'
        if msg.lower().startswith("value error, "):
            msg = msg[len("Value error, ") :]
        cleaned = {
            "loc": err.get("loc", []),
            "msg": msg,
            "type": err.get("type", "value_error"),
        }
        errors.append(cleaned)
    return errors


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom RequestValidationError handler used across the app."""
    errors = _clean_validation_errors(exc)

    logger.info(
        f"[VALIDATION ERROR] {request.method} {request.url.path} - errors={errors}"
    )

    return JSONResponse(status_code=422, content={"detail": errors})


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI app."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
