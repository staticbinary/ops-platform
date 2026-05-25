import uuid

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from . import auth
from .database import Base, engine, get_db
from .models import Asset, AuditLog
from .schemas import AssetCreate, AssetUpdate, AssetResponse

app = FastAPI(
    title="Asset Service",
    description="Operations platform asset management service",
    version="1.0.0",
    root_path="/api/assets"
)

Base.metadata.create_all(bind=engine)


def get_actor(current_user: dict) -> str:
    return current_user.get("username") or current_user.get("sub") or "unknown"


def write_audit_log(
    db: Session,
    action: str,
    actor: str,
    result: str,
    asset_id: int | None = None
):
    audit_log = AuditLog(
        action=action,
        actor=actor,
        result=result,
        asset_id=asset_id
    )

    db.add(audit_log)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())

    print(f"[request_id={request_id}] Incoming request: {request.method} {request.url}")

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    print(f"[request_id={request_id}] Completed response: {response.status_code}")

    return response


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
def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.require_role("admin"))
):
    actor = get_actor(current_user)

    try:
        db_asset = Asset(
            hostname=asset.hostname,
            owner=asset.owner,
            status=asset.status
        )

        db.add(db_asset)
        db.flush()

        write_audit_log(
            db=db,
            action="asset.create",
            actor=actor,
            result="success",
            asset_id=db_asset.id
        )

        db.commit()
        db.refresh(db_asset)

        return db_asset

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Asset could not be created because it conflicts with an existing record"
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while creating asset"
        )


@app.get("/assets", response_model=list[AssetResponse], tags=["Assets"])
def get_assets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    return db.query(Asset).all()


@app.get("/assets/{asset_id}", response_model=AssetResponse, tags=["Assets"])
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.get_current_user)
):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@app.put("/assets/{asset_id}", response_model=AssetResponse, tags=["Assets"])
def update_asset(
    asset_id: int,
    updated_asset: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.require_role("admin"))
):
    actor = get_actor(current_user)

    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    try:
        asset.hostname = updated_asset.hostname
        asset.owner = updated_asset.owner
        asset.status = updated_asset.status

        write_audit_log(
            db=db,
            action="asset.update",
            actor=actor,
            result="success",
            asset_id=asset.id
        )

        db.commit()
        db.refresh(asset)

        return asset

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Asset update conflicts with an existing record"
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while updating asset"
        )


@app.delete("/assets/{asset_id}", tags=["Assets"])
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.require_role("admin"))
):
    actor = get_actor(current_user)

    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    try:
        write_audit_log(
            db=db,
            action="asset.delete",
            actor=actor,
            result="success",
            asset_id=asset.id
        )

        db.delete(asset)
        db.commit()

        return {"message": f"Asset {asset_id} deleted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while deleting asset"
        )


@app.get("/audit-logs", tags=["Audit"])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.require_role("admin"))
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()

    return logs


@app.get("/", tags=["Root"])
def root():
    return {"message": "Asset Service running"}