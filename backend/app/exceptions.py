"""
Custom exceptions for the application.
"""
from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception with HTTP status code."""
    
    def __init__(
        self, 
        detail: str, 
        status_code: int = 400,
        headers: Optional[Dict[str, str]] = None
    ):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers
        super().__init__(detail)


class ResourceNotFoundError(AppException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: int | str):
        detail = f"{resource_type.capitalize()} with id {resource_id} not found"
        super().__init__(detail, status_code=404)


class ResourceAlreadyExistsError(AppException):
    """Raised when attempting to create a resource that already exists."""
    
    def __init__(self, resource_type: str, identifier: str):
        detail = f"{resource_type.capitalize()} with {identifier} already exists"
        super().__init__(detail, status_code=400)


class ValidationError(AppException):
    """Raised when input validation fails."""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        if field:
            detail = f"Validation error for field '{field}': {detail}"
        super().__init__(detail, status_code=422)


class DatabaseError(AppException):
    """Raised when a database operation fails."""
    
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(detail, status_code=500)


class ExternalServiceError(AppException):
    """Raised when an external service (OpenAI, etc.) fails."""
    
    def __init__(self, service_name: str, detail: str = "Service temporarily unavailable"):
        full_detail = f"{service_name} error: {detail}"
        super().__init__(full_detail, status_code=503)


class RateLimitExceeded(AppException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, detail: str = "Rate limit exceeded. Please try again later."):
        super().__init__(detail, status_code=429)


class AuthenticationError(AppException):
    """Raised when authentication fails."""
    
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(detail, status_code=401)


class AuthorizationError(AppException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail, status_code=403)
