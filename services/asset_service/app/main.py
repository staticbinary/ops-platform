from fastapi import FastAPI
from sqlalchemy import text

from .database import engine

app = FastAPI(title="Asset Service")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "asset-service"
    }


@app.get("/db-health")
def db_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "error",
            "database": str(e)
        }


@app.get("/")
def root():
    return {
        "message": "Asset Service running"
    }