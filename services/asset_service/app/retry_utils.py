import time
from collections.abc import Callable
from typing import TypeVar

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

T = TypeVar("T")


def retry_database_operation(
    operation: Callable[[], T],
    db: Session,
    attempts: int = 3,
    initial_delay_seconds: float = 0.2,
    backoff_factor: float = 2.0,
) -> T:
    last_exception: Exception | None = None
    delay = initial_delay_seconds

    for attempt in range(1, attempts + 1):
        try:
            return operation()

        except OperationalError as exc:
            db.rollback()

            last_exception = exc

            if attempt == attempts:
                break

            time.sleep(delay)
            delay *= backoff_factor

    if last_exception:
        raise last_exception

    raise RuntimeError("retry_database_operation failed unexpectedly")