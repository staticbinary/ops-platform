import time

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.metrics import metrics_response, record_request_metric
from app.tracing import setup_tracing

from . import auth, models, schemas
from .database import Base, engine, get_db


app = FastAPI(title="Auth Service")

setup_tracing(app)

Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_seconds = time.perf_counter() - start_time

    record_request_metric(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_seconds=duration_seconds,
    )

    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return metrics_response()


@app.post("/register", response_model=schemas.UserResponse)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = auth.hash_password(user.password)

    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role="viewer"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login")
def login_user(
    request: Request,
    user: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if not existing_user:
        auth.create_audit_log(
            db=db,
            event_type="login",
            outcome="failure",
            user_email=user.email,
            detail="User not found"
        )

        auth.log_security_event(
            event="auth.failed",
            reason="user_not_found",
            request=request,
            user_email=user.email
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not auth.verify_password(
        user.password,
        existing_user.hashed_password
    ):
        auth.create_audit_log(
            db=db,
            event_type="login",
            outcome="failure",
            user_email=user.email,
            detail="Invalid password"
        )

        auth.log_security_event(
            event="auth.failed",
            reason="invalid_password",
            request=request,
            user_email=user.email
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = auth.create_access_token(
        data={
            "sub": existing_user.email,
            "role": existing_user.role
        }
    )

    auth.create_audit_log(
        db=db,
        event_type="login",
        outcome="success",
        user_email=existing_user.email,
        detail="JWT issued"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": existing_user.role
    }


@app.post("/token")
def token_login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == form_data.username)
        .first()
    )

    if not existing_user:
        auth.create_audit_log(
            db=db,
            event_type="token_login",
            outcome="failure",
            user_email=form_data.username,
            detail="User not found"
        )

        auth.log_security_event(
            event="auth.failed",
            reason="user_not_found",
            request=request,
            user_email=form_data.username
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not auth.verify_password(
        form_data.password,
        existing_user.hashed_password
    ):
        auth.create_audit_log(
            db=db,
            event_type="token_login",
            outcome="failure",
            user_email=form_data.username,
            detail="Invalid password"
        )

        auth.log_security_event(
            event="auth.failed",
            reason="invalid_password",
            request=request,
            user_email=form_data.username
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = auth.create_access_token(
        data={
            "sub": existing_user.email,
            "role": existing_user.role
        }
    )

    auth.create_audit_log(
        db=db,
        event_type="token_login",
        outcome="success",
        user_email=existing_user.email,
        detail="OAuth2 token issued"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/me")
def read_current_user(
    current_user: dict = Depends(auth.get_current_user)
):
    return current_user


@app.get("/admin")
def admin_only(
    current_user: dict = Depends(auth.require_role("admin"))
):
    return {
        "message": "Admin access granted",
        "user": current_user
    }


@app.get("/audit", response_model=list[schemas.AuditLogResponse])
def read_audit_logs(
    current_user: dict = Depends(auth.require_role("admin")),
    db: Session = Depends(get_db)
):
    logs = (
        db.query(models.AuditLog)
        .order_by(models.AuditLog.id.desc())
        .all()
    )

    return logs


@app.post("/dev/promote-admin/{email}", response_model=schemas.UserResponse)
def promote_user_to_admin(
    email: str,
    db: Session = Depends(get_db)
):
    user = (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.role = "admin"

    db.commit()
    db.refresh(user)

    auth.create_audit_log(
        db=db,
        event_type="role_change",
        outcome="success",
        user_email=user.email,
        detail="User promoted to admin via dev endpoint"
    )

    return user