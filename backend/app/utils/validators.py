from typing import Any
from urllib.parse import urlsplit


def normalize_optional_http_url(value: Any) -> Any:
    """Normalize blank URLs and reject non-HTTP(S) or relative URLs."""
    if not isinstance(value, str):
        return value

    normalized_value = value.strip()
    if not normalized_value:
        return None

    parsed = urlsplit(normalized_value)
    if parsed.scheme not in {"http", "https"} or parsed.hostname is None:
        raise ValueError("Must be an absolute HTTP or HTTPS URL")

    return normalized_value
