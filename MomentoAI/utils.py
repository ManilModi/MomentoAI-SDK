from typing import Any
from .exceptions import APIError, AuthenticationError




def handle_response(resp) -> Any:
    """Normalize API responses and raise helpful errors."""
    if resp.status_code == 401:
    # Prefer server message if provided
        try:
            detail = resp.json().get("detail", "Unauthorized")
        except Exception:
            detail = resp.text or "Unauthorized"
            raise AuthenticationError(detail)


    if resp.status_code >= 400:
        try:
            payload = resp.json()
        except Exception:
            payload = {"error": resp.text}
            message = payload.get("detail") or payload.get("error") or str(payload)
            raise APIError(resp.status_code, message)


# Successful response
    try:
        return resp.json()
    except Exception:
        return resp.text