from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import products, users, login, cart
from app.core.db import engine
from sqlmodel import SQLModel

from app.models import product, user, cart as cart_model  # noqa: F401  registers table metadata for create_all

SQLModel.metadata.create_all(engine)

app = FastAPI(title=settings.app_name)


app.include_router(products.router)
app.include_router(users.router)
app.include_router(login.router)
app.include_router(cart.router)
