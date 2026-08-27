from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.database import Base, engine


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="WorkHub Auth Service",
    description="Authentication microservice for WorkHub",
    version="1.0.0"
)


# Register authentication routes
app.include_router(auth_router)