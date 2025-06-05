# src/veedb/exceptions.py


class VNDBAPIError(Exception):
    """Base class for VNDB API errors."""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

    def __str__(self):
        if self.status_code:
            return f"(Status {self.status_code}) {self.message}"
        return self.message


class InvalidRequestError(VNDBAPIError):
    """HTTP 400 - Invalid request body or query."""

    def __init__(
        self, message: str = "Invalid request body or query.", status_code: int = 400
    ):
        super().__init__(message, status_code)


class AuthenticationError(VNDBAPIError):
    """HTTP 401 - Invalid authentication token."""

    def __init__(
        self,
        message: str = "Invalid authentication token or token missing for protected endpoint.",
        status_code: int = 401,
    ):
        super().__init__(message, status_code)


class NotFoundError(VNDBAPIError):
    """HTTP 404 - Invalid API path or HTTP method, or resource not found."""

    def __init__(
        self,
        message: str = "Resource not found or invalid API path.",
        status_code: int = 404,
    ):
        super().__init__(message, status_code)


class RateLimitError(VNDBAPIError):
    """HTTP 429 - Throttled."""

    def __init__(
        self,
        message: str = "API request limit reached. Please wait before trying again.",
        status_code: int = 429,
    ):
        super().__init__(message, status_code)


class ServerError(VNDBAPIError):
    """HTTP 500, 502, etc. - Server error."""

    def __init__(
        self,
        message: str = "An unexpected server error occurred.",
        status_code: int = 500,
    ):
        super().__init__(message, status_code)


# You could also add more specific errors if needed, e.g., for "Too much data selected"
class TooMuchDataSelectedError(InvalidRequestError):
    """Specific error for when the 'Too much data selected' message is returned by VNDB."""

    def __init__(
        self,
        message: str = "Too much data selected. Reduce fields or results per page.",
        status_code: int = 400,
    ):
        super().__init__(message, status_code)
