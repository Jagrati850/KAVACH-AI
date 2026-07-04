"""
KAVACH AI — Custom Exceptions
Structured exception hierarchy for clean error handling.
"""

from typing import Any, Optional


class KavachException(Exception):
    """Base exception for all KAVACH AI errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        detail: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class AuthenticationError(KavachException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, status_code=401)


class AuthorizationError(KavachException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message, status_code=403)


class NotFoundError(KavachException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource", resource_id: str = ""):
        msg = f"{resource} not found"
        if resource_id:
            msg = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=msg, status_code=404)


class ValidationError(KavachException):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation error", detail: Any = None):
        super().__init__(message=message, status_code=422, detail=detail)


class DuplicateError(KavachException):
    """Raised when a unique constraint is violated."""

    def __init__(self, field: str = "Resource"):
        super().__init__(
            message=f"{field} already exists",
            status_code=409,
        )


class FileTooLargeError(KavachException):
    """Raised when an uploaded file exceeds size limits."""

    def __init__(self, max_size_mb: int = 10):
        super().__init__(
            message=f"File exceeds maximum size of {max_size_mb}MB",
            status_code=413,
        )


class AIProcessingError(KavachException):
    """Raised when an AI engine fails to process input."""

    def __init__(self, engine: str = "AI", message: str = "Processing failed"):
        super().__init__(
            message=f"{engine} engine: {message}",
            status_code=500,
        )


class RateLimitError(KavachException):
    """Raised when rate limit is exceeded."""

    def __init__(self):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=429,
        )
