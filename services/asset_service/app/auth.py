from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.error_utils import forbidden_error, unauthorized_error
from app.logging_utils import (
    build_auth_failure_log,
    build_permission_denied_log,
    log_event,
)
from app.request_context import get_request_id, get_source_ip

from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)

ROLE_PERMISSIONS = {
    "admin": {
        "asset:read",
        "asset:create",
        "asset:update",
        "asset:delete",
        "audit:read",
        "user:manage",
    },
    "viewer": {
        "asset:read",
        "audit:read",
    },
}


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],    
        )

        return payload

    except ExpiredSignatureError:
        log_event(
            build_auth_failure_log(
                request_id=get_request_id(),
                actor=None,
                role=None,
                source_ip=get_source_ip(),
                reason="token_expired",
            )
        )

        unauthorized_error("Token has expired")

    except JWTError:
        log_event(
            build_auth_failure_log(
                request_id=get_request_id(),
                actor=None,
                role=None,
                source_ip=get_source_ip(),
                reason="invalid_token",
            )
        )

        unauthorized_error("Invalid token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None:
        log_event(
            build_auth_failure_log(
                request_id=get_request_id(),
                actor=None,
                role=None,
                source_ip=get_source_ip(),
                reason="missing_authorization_token",
            )
        )

        unauthorized_error("Missing authorization token")

    payload = verify_token(credentials.credentials)

    email = payload.get("sub")
    role = payload.get("role")

    if not email:
        log_event(
            build_auth_failure_log(
                request_id=get_request_id(),
                actor=None,
                role=role,
                source_ip=get_source_ip(),
                reason="missing_subject_claim",
            )
        )

        unauthorized_error("Token missing subject claim")

    if not role:
        log_event(
            build_auth_failure_log(
                request_id=get_request_id(),
                actor=email,
                role=None,
                source_ip=get_source_ip(),
                reason="missing_role_claim",
            )
        )

        unauthorized_error("Token missing role claim")

    return {
        "email": email,
        "role": role,
        "permissions": ROLE_PERMISSIONS.get(role, set()),
    }


def require_role(required_role: str):
    def role_checker(
        current_user: dict = Depends(get_current_user),
    ):
        if current_user["role"] != required_role:
            forbidden_error()

        return current_user

    return role_checker


def require_permission(required_permission: str):
    def permission_checker(
        current_user: dict = Depends(get_current_user),
    ):
        user_permissions = current_user.get("permissions", set())

        if required_permission not in user_permissions:
            log_event(
                build_permission_denied_log(
                    request_id=get_request_id(),
                    actor=current_user.get("email"),
                    role=current_user.get("role"),
                    source_ip=get_source_ip(),
                    permission=required_permission,
                )
            )

            forbidden_error()

        return current_user

    return permission_checker