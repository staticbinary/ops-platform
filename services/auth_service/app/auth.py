import json
import logging
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext

from app.metrics import (
    record_expired_token,
    record_invalid_token,
    record_permission_denied,
    record_privilege_escalation_attempt,
)

from . import models

SECRET_KEY = "super-secret-dev-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

logger = logging.getLogger("auth-service")
logger.setLevel(logging.INFO)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token"
)


def log_security_event(
    event: str,
    reason: str,
    request: Request = None,
    user_email: str = None,
    outcome: str = "failure",
    severity: str = "warning"
):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "auth-service",
        "environment": "development",
        "severity": severity,
        "category": "security",
        "event": event,
        "reason": reason,
        "outcome": outcome,
        "user_email": user_email,
    }

    if request:
        payload["method"] = request.method
        payload["path"] = request.url.path
        payload["client"] = request.client.host if request.client else None

    logger.warning(json.dumps(payload))


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str, request: Request = None):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except ExpiredSignatureError:
        log_security_event(
            event="token.expired",
            reason="expired_token",
            request=request
        )

        record_expired_token(
            reason="expired_token"
        )

        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except JWTError:
        log_security_event(
            event="token.invalid",
            reason="invalid_token",
            request=request
        )

        record_invalid_token(
            reason="invalid_token"
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme)
):
    payload = verify_token(token, request)

    return {
        "email": payload.get("sub"),
        "role": payload.get("role")
    }


def require_role(required_role: str):
    def role_checker(
        request: Request,
        current_user: dict = Depends(get_current_user)
    ):
        if current_user["role"] != required_role:
            log_security_event(
                event="permission.denied",
                reason="insufficient_role",
                request=request,
                user_email=current_user.get("email")
            )

            record_permission_denied(
                reason="insufficient_role",
                required_role=required_role,
            )

            record_privilege_escalation_attempt(
                required_role=required_role,
            )

            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker


def create_audit_log(
    db,
    event_type: str,
    outcome: str,
    user_email: str = None,
    detail: str = None
):
    log = models.AuditLog(
        event_type=event_type,
        user_email=user_email,
        outcome=outcome,
        detail=detail
    )

    db.add(log)
    db.commit()