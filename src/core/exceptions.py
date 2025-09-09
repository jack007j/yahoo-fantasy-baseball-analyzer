"""
Custom exceptions for the Yahoo Fantasy Baseball application.
"""

from typing import Optional, Dict, Any


class YahooFantasyBaseException(Exception):
    """Base exception for all Yahoo Fantasy Baseball application errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(YahooFantasyBaseException):
    """Raised when there are configuration or setup issues."""
    pass


class AuthenticationError(YahooFantasyBaseException):
    """Raised when Yahoo OAuth authentication fails."""
    pass


class APIError(YahooFantasyBaseException):
    """Base class for API-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[Dict[str, Any]] = None) -> None:
        self.status_code = status_code
        self.response_data = response_data or {}
        details = {"status_code": status_code, "response_data": response_data}
        super().__init__(message, details)


class YahooAPIError(APIError):
    """Raised when Yahoo Fantasy API requests fail."""
    pass


class MLBAPIError(APIError):
    """Raised when MLB Stats API requests fail."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, 
                 status_code: Optional[int] = None) -> None:
        self.retry_after = retry_after
        details = {"retry_after": retry_after, "status_code": status_code}
        super().__init__(message, status_code, details)


class DataValidationError(YahooFantasyBaseException):
    """Raised when data validation fails."""
    pass


class PlayerMatchingError(YahooFantasyBaseException):
    """Raised when player matching between APIs fails."""
    pass


class CacheError(YahooFantasyBaseException):
    """Raised when caching operations fail."""
    pass


class AnalysisError(YahooFantasyBaseException):
    """Raised when analysis operations fail."""
    pass


class NetworkError(YahooFantasyBaseException):
    """Raised when network operations fail."""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None) -> None:
        self.original_exception = original_exception
        details = {"original_exception": str(original_exception) if original_exception else None}
        super().__init__(message, details)


class TimeoutError(NetworkError):
    """Raised when network requests timeout."""
    pass


# Error code mappings for structured error handling
ERROR_CODES = {
    "CONFIG_MISSING": "Required configuration is missing",
    "CONFIG_INVALID": "Configuration values are invalid",
    "AUTH_TOKEN_EXPIRED": "OAuth token has expired",
    "AUTH_TOKEN_INVALID": "OAuth token is invalid",
    "AUTH_REFRESH_FAILED": "Failed to refresh OAuth token",
    "API_RATE_LIMITED": "API rate limit exceeded",
    "API_UNAVAILABLE": "API service is unavailable",
    "API_INVALID_RESPONSE": "API returned invalid response",
    "DATA_NOT_FOUND": "Requested data not found",
    "DATA_INVALID_FORMAT": "Data is in invalid format",
    "PLAYER_NOT_MATCHED": "Player could not be matched between APIs",
    "CACHE_READ_FAILED": "Failed to read from cache",
    "CACHE_WRITE_FAILED": "Failed to write to cache",
    "ANALYSIS_INCOMPLETE": "Analysis could not be completed",
    "NETWORK_TIMEOUT": "Network request timed out",
    "NETWORK_CONNECTION": "Network connection failed"
}


def get_error_message(error_code: str) -> str:
    """Get human-readable error message for error code."""
    return ERROR_CODES.get(error_code, "An unknown error occurred")


def create_error_response(error_code: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create standardized error response dictionary."""
    return {
        "error": True,
        "error_code": error_code,
        "message": get_error_message(error_code),
        "details": details or {}
    }