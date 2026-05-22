from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Asset
from .schemas import AssetCreate, AssetResponse

app = FastAPI(title="Asset Service")

Base.metadata.create_all(bind=engine)


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


@app.post("/assets", response_model=AssetResponse)
def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db)
):
    db_asset = Asset(
        hostname=asset.hostname,
        owner=asset.owner,
        status=asset.status
    )

    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    return db_asset


@app.get("/assets", response_model=list[AssetResponse])
def get_assets(db: Session = Depends(get_db)):
    return db.query(Asset).all()


@app.get("/")
def root():
    return {
        "message": "Asset Service running"
    }