from typing import Any
from .exceptions import APIError, AuthenticationError
import json

def handle_response(resp) -> Any:
    """Safely normalize API responses and raise helpful errors."""
    payload = None

    # Try parsing JSON safely
    try:
        if resp.text.strip():  # only try to parse if not empty
            payload = resp.json()
    except json.JSONDecodeError:
        payload = None

    # Handle authentication errors
    if resp.status_code == 401:
        detail = None
        if isinstance(payload, dict):
            detail = payload.get("detail")
        raise AuthenticationError(detail or resp.text or "Unauthorized")

    # Handle general HTTP errors
    if resp.status_code >= 400:
        message = None
        if isinstance(payload, dict):
            message = payload.get("detail") or payload.get("error")
        raise APIError(resp.status_code, message or resp.text or "Unknown error")

    # Return parsed payload if valid JSON; otherwise raw text
    if isinstance(payload, dict):
        return payload
    elif resp.text.strip():
        return resp.text
    else:
        return {"status_code": resp.status_code, "message": "Success (no content)"}
