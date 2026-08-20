from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current UTC time without timezone information."""
    return datetime.now(UTC).replace(tzinfo=None)
