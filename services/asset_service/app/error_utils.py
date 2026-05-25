from fastapi import HTTPException, status


def unauthorized_error(detail: str = "Authentication required"):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": "unauthorized",
            "message": detail,
        },
    )


def forbidden_error(detail: str = "Insufficient permissions"):
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": "forbidden",
            "message": detail,
        },
    )


def not_found_error(resource: str = "Resource"):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": "not_found",
            "message": f"{resource} not found",
        },
    )


def server_error(detail: str = "Internal server error"):
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "server_error",
            "message": detail,
        },
    )