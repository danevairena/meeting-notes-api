import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import MeetingNotFoundError
from app.logging_config import configure_logging
from app.routers import meetings
from app.settings import settings


# configure logging before app creation
configure_logging()

# create module logger
logger = logging.getLogger(__name__)

# create fastapi application instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# register meetings router
app.include_router(meetings.router)


# handle known domain error for missing meetings
@app.exception_handler(MeetingNotFoundError)
def handle_meeting_not_found(_: Request, exc: MeetingNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
        },
    )


# handle unexpected server errors with a consistent response shape
@app.exception_handler(Exception)
def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("unexpected error occurred", exc_info=exc)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "internal server error",
        },
    )


# expose a simple endpoint to verify the service is running
@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.app_env,
    }