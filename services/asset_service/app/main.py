from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Asset
from .schemas import AssetCreate, AssetUpdate, AssetResponse

app = FastAPI(
    title="Asset Service",
    description="Operations platform asset management service",
    version="1.0.0",
    root_path="/api/assets"
)

Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "asset-service"}


@app.get("/db-health", tags=["Health"])
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


@app.post("/assets", response_model=AssetResponse, tags=["Assets"])
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    db_asset = Asset(
        hostname=asset.hostname,
        owner=asset.owner,
        status=asset.status
    )

    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    return db_asset


@app.get("/assets", response_model=list[AssetResponse], tags=["Assets"])
def get_assets(db: Session = Depends(get_db)):
    return db.query(Asset).all()


@app.get("/assets/{asset_id}", response_model=AssetResponse, tags=["Assets"])
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@app.put("/assets/{asset_id}", response_model=AssetResponse, tags=["Assets"])
def update_asset(
    asset_id: int,
    updated_asset: AssetUpdate,
    db: Session = Depends(get_db)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    asset.hostname = updated_asset.hostname
    asset.owner = updated_asset.owner
    asset.status = updated_asset.status

    db.commit()
    db.refresh(asset)

    return asset


@app.delete("/assets/{asset_id}", tags=["Assets"])
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    db.delete(asset)
    db.commit()

    return {"message": f"Asset {asset_id} deleted successfully"}


@app.get("/", tags=["Root"])
def root():
    return {"message": "Asset Service running"}