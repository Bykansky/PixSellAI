import subprocess
import sys
from fastapi import FastAPI
from .api import generate
from . import config

app = FastAPI(
    title="PixSellAI",
    description="API for generating professional product photos",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    """
    При старте FastAPI запускаем RQ воркер в фоновом процессе.
    """
    command = [
        sys.executable,
        "-m", "rq", "worker",
        "--url", config.REDIS_URL,
        "default"
    ]
    subprocess.Popen(command)

app.include_router(generate.router, prefix="/api", tags=["Generation"])

@app.get("/", tags=["Health Check"])
def read_root():
    return {"Status": "OK"}
