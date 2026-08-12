from fastapi import FastAPI

from app.api.routes.auth import router as auth_router


app = FastAPI(
    title="WorkHub Authentication Service",
    version="1.0.0",
)


app.include_router(auth_router)


@app.get("/health")
def health_check():
    return {
        "service": "auth-service",
        "status": "healthy",
    }