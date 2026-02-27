class NSError(Exception):
    """Base exception for all py-ns errors."""


class APIError(NSError):
    """Raised when the NS API returns an error response."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Raised on 401/403 responses."""


class NotFoundError(APIError):
    """Raised on 404 responses."""


class RateLimitError(APIError):
    """Raised on 429 responses."""


class ServerError(APIError):
    """Raised on 5xx responses."""
