from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

SECRET_KEY = "super-secret-dev-key"
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer()


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    payload = verify_token(credentials.credentials)

    email = payload.get("sub")
    role = payload.get("role")

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Token missing subject claim"
        )

    if not role:
        raise HTTPException(
            status_code=401,
            detail="Token missing role claim"
        )

    return {
        "email": email,
        "role": role
    }


def require_role(required_role: str):
    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker