from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import products
from app.core.db import engine
from sqlmodel import SQLModel

SQLModel.metadata.create_all(engine)

app = FastAPI(title=settings.app_name)


app.include_router(products.router)
