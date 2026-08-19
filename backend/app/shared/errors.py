"""
Custom domain exceptions for explicit error handling.
"""


class DomainError(Exception):
    """Base class for all domain exceptions."""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(DomainError):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with id {identifier} not found",
            code="NOT_FOUND"
        )


class ValidationError(DomainError):
    """Raised when validation fails."""

    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message=message, code="VALIDATION_ERROR")


class AuthorizationError(DomainError):
    """Raised when authorization check fails."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message=message, code="FORBIDDEN")


class ConflictError(DomainError):
    """Raised when a resource conflict occurs."""

    def __init__(self, message: str):
        super().__init__(message=message, code="CONFLICT")
