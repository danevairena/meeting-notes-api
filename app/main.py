from fastapi import FastAPI

from app.settings import settings


# create fastapi application instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


# expose a simple endpoint to verify the service is running
@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.app_env,
    }