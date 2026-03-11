from fastapi import FastAPI
from app.settings import settings
from app.routers import meetings
from app.settings import settings


# create fastapi application instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# register meetings router
app.include_router(meetings.router)

# expose a simple endpoint to verify the service is running
@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.app_env,
    }