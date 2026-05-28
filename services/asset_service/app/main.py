from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.body_size_limit import BodySizeLimitMiddleware
from app.logging_utils import build_dependency_health_log, log_event
from app.metrics import metrics_response
from app.rate_limit import RateLimitMiddleware
from app.request_context import RequestIDMiddleware, get_request_id
from app.retry_utils import retry_database_operation
from app.security_headers import SecurityHeadersMiddleware
from app.tracing import setup_tracing

from . import auth
from .database import get_db
from .models import Asset, AuditLog
from .schemas import AssetCreate, AssetResponse, AssetUpdate


app = FastAPI(
    title="Asset Service",
    description="Operations platform asset management service",
    version="1.0.0",
    root_path="/api/assets",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

setup_tracing(app)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.add_middleware(
    BodySizeLimitMiddleware,
    max_body_size_bytes=1_048_576,
)

app.add_middleware(
    RateLimitMiddleware,
    max_requests=100,
    window_seconds=60,
)

app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": get_request_id(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Request validation failed",
            "status_code": 422,
            "request_id": get_request_id(),
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "request_id": get_request_id(),
        },
    )


def get_actor(current_user: dict) -> str:
    return (
        current_user.get("email")
        or current_user.get("username")
        or current_user.get("sub")
        or "unknown"
    )


def write_audit_log(
    db: Session,
    action: str,
    actor: str,
    result: str,
    asset_id: int | None = None,
):
    audit_log = AuditLog(
        action=action,
        actor=actor,
        result=result,
        asset_id=asset_id,
    )

    db.add(audit_log)


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "service": "asset-service",
    }


@app.get("/health/live", tags=["Health"])
def health_live():
    return {
        "status": "alive",
        "service": "asset-service",
    }


@app.get("/health/startup", tags=["Health"])
def health_startup():
    return {
        "status": "started",
        "service": "asset-service",
    }

@app.get("/health/ready", tags=["Health"])
def health_ready(db: Session = Depends(get_db)):
    try:
        retry_database_operation(
            lambda: db.execute(text("SELECT 1")),
            db=db,
        )

        log_event(
            build_dependency_health_log(
                dependency="database",
                status="available",
                severity="info",
            )
        )

        return {
            "status": "ready",
            "service": "asset-service",
            "checks": {
                "database": "ok",
            },
        }

    except Exception as exc:
        db.rollback()

        log_event(
            build_dependency_health_log(
                dependency="database",
                status="unavailable",
                severity="critical",
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
        )

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "asset-service",
                "checks": {
                    "database": "unavailable",
                },
            },
        )

@app.get("/db-health", tags=["Health"])
def db_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected",
        }

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "database": "disconnected",
            },
        )


@app.get("/ready", tags=["Health"])
def readiness_check():
    return {
        "status": "deprecated",
        "message": "Use /health/ready instead",
        "service": "asset-service",
    }


@app.get("/metrics", tags=["Metrics"])
def metrics():
    return metrics_response()


@app.post("/assets", response_model=AssetResponse, tags=["Assets"])
def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.require_permission("asset:create")),
):
    actor = get_actor(current_user)

    try:
        db_asset = Asset(
            hostname=asset.hostname,
            owner=asset.owner,
            status=asset.status,
        )

        db.add(db_asset)
        db.flush()

        write_audit_log(
            db=db,
            action="asset.create",
            actor=actor,
            result="success",
            asset_id=db_asset.id,
        )

        db.commit()
        db.refresh(db_asset)

        return db_asset

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Asset could not be created because it conflicts with an existing record",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while creating asset",
        )


@app.get("/assets", response_model=list[AssetResponse], tags=["Assets"])
def get_assets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.require_permission("asset:read")),
):
    return db.query(Asset).all()


@app.get("/assets/{asset_id}", response_model=AssetResponse, tags=["Assets"])
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.require_permission("asset:read")),
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
    current_user: dict = Depends(auth.require_permission("asset:update")),
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
            asset_id=asset.id,
        )

        db.commit()
        db.refresh(asset)

        return asset

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Asset update conflicts with an existing record",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while updating asset",
        )


@app.delete("/assets/{asset_id}", tags=["Assets"])
def delete_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.require_permission("asset:delete")),
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
            asset_id=asset.id,
        )

        db.delete(asset)
        db.commit()

        return {"message": f"Asset {asset_id} deleted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while deleting asset",
        )


@app.get("/audit-logs", tags=["Audit"])
def get_audit_logs(
    action: str | None = Query(default=None),
    actor: str | None = Query(default=None),
    result: str | None = Query(default=None),
    asset_id: int | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    sort_order: str = Query(default="desc"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: dict = Depends(auth.require_permission("audit:read")),
):
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action == action)

    if actor:
        query = query.filter(AuditLog.actor == actor)

    if result:
        query = query.filter(AuditLog.result == result)

    if asset_id is not None:
        query = query.filter(AuditLog.asset_id == asset_id)

    if start_date:
        try:
            parsed_start = datetime.fromisoformat(start_date)
            query = query.filter(AuditLog.timestamp >= parsed_start)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid start_date format. Use ISO format.",
            )

    if end_date:
        try:
            parsed_end = datetime.fromisoformat(end_date)
            query = query.filter(AuditLog.timestamp <= parsed_end)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid end_date format. Use ISO format.",
            )

    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="sort_order must be either 'asc' or 'desc'",
        )

    if sort_order == "asc":
        query = query.order_by(AuditLog.timestamp.asc())
    else:
        query = query.order_by(AuditLog.timestamp.desc())

    total = query.count()
    logs = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "sort_order": sort_order,
        "items": logs,
    }


@app.get("/", tags=["Root"])
def root():
    return {"message": "Asset Service running"}