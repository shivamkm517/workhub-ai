from fastapi import FastAPI

from app.api.routes.user import router as user_router
from app.database import Base, engine


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="WorkHub User Service",
    description="User management microservice for WorkHub",
    version="1.0.0"
)


# Register user routes
app.include_router(user_router)