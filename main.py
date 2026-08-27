from fastapi import FastAPI

from app.shared.database import Base, engine

# Import models
from app.user_service.models.user import User
from app.auth_service.models.token import RefreshToken

from app.auth_service.api.routes.auth import router as auth_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="WorkHub API"
)

app.include_router(auth_router)