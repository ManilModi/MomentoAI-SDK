class MomentoAIError(Exception):
    """Base exception for Momento AI SDK."""


class AuthenticationError(MomentoAIError):
    """Raised when API key is missing or invalid."""


class APIError(MomentoAIError):
    """Raised for non-2xx HTTP responses from the API."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"APIError {status_code}: {message}")
