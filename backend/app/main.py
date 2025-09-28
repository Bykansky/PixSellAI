import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

from app.api import generate, swipe, train, product
app.include_router(generate.router, prefix="/api")
app.include_router(swipe.router, prefix="/api")
app.include_router(train.router, prefix="/api")
app.include_router(product.router, prefix="/api")
