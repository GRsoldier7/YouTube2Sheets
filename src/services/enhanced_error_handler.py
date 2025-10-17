"""
Enhanced Error Handler Service
Implements Google API best practices for error handling
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime
import logging
import traceback

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from googleapiclient.errors import HttpError, Error as GoogleAPIError
from google.auth.exceptions import GoogleAuthError
import requests.exceptions

@dataclass
class ErrorContext:
    """Context information for error handling."""
    service: str
    operation: str
    timestamp: datetime
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

@dataclass
class ErrorResponse:
    """Standardized error response."""
    error_code: str
    error_message: str
    error_type: str
    context: ErrorContext
    retry_after: Optional[int] = None
    user_action: Optional[str] = None
    technical_details: Optional[Dict[str, Any]] = None

class EnhancedErrorHandler:
    """Enhanced error handler following Google API best practices."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_codes = {
            # Google API Error Codes
            "INVALID_ARGUMENT": "The request contains an invalid argument",
            "PERMISSION_DENIED": "The caller does not have permission",
            "NOT_FOUND": "The specified resource was not found",
            "ALREADY_EXISTS": "The resource already exists",
            "RESOURCE_EXHAUSTED": "Quota exceeded or resource exhausted",
            "FAILED_PRECONDITION": "The system is not in the required state",
            "ABORTED": "The operation was aborted",
            "OUT_OF_RANGE": "The operation was attempted past the valid range",
            "UNIMPLEMENTED": "The operation is not implemented",
            "INTERNAL": "Internal server error",
            "UNAVAILABLE": "The service is currently unavailable",
            "DATA_LOSS": "Unrecoverable data loss or corruption",
            "UNAUTHENTICATED": "The request does not have valid authentication credentials"
        }
        
        self.retryable_errors = {
            "UNAVAILABLE", "INTERNAL", "RESOURCE_EXHAUSTED", "ABORTED"
        }
        
        self.user_actions = {
            "INVALID_ARGUMENT": "Please check your input parameters and try again",
            "PERMISSION_DENIED": "Please check your permissions and try again",
            "NOT_FOUND": "The requested resource was not found. Please verify the resource exists",
            "ALREADY_EXISTS": "The resource already exists. Please use a different identifier",
            "RESOURCE_EXHAUSTED": "API quota exceeded. Please try again later or contact support",
            "FAILED_PRECONDITION": "Please ensure all prerequisites are met before retrying",
            "UNAUTHENTICATED": "Please check your authentication credentials",
            "UNAVAILABLE": "Service temporarily unavailable. Please try again later"
        }
    
    def handle_google_api_error(self, error: GoogleAPIError, context: ErrorContext) -> ErrorResponse:
        """Handle Google API errors with proper categorization."""
        try:
            if isinstance(error, HttpError):
                return self._handle_http_error(error, context)
            else:
                return self._handle_generic_google_error(error, context)
        except Exception as e:
            self.logger.error(f"Error in error handler: {e}")
            return self._create_fallback_error(context, str(error))
    
    def _handle_http_error(self, error: HttpError, context: ErrorContext) -> ErrorResponse:
        """Handle HTTP errors from Google APIs."""
        status_code = error.resp.status if hasattr(error, 'resp') else 500
        error_details = error.error_details if hasattr(error, 'error_details') else []
        
        # Extract error information
        error_code = self._extract_error_code(error_details, status_code)
        error_message = self._extract_error_message(error_details, str(error))
        
        # Determine if retryable
        retry_after = self._calculate_retry_after(status_code, error_code)
        
        # Get user action
        user_action = self.user_actions.get(error_code, "Please try again later")
        
        # Create technical details
        technical_details = {
            "status_code": status_code,
            "error_details": error_details,
            "request_url": getattr(error, 'uri', None),
            "traceback": traceback.format_exc()
        }
        
        return ErrorResponse(
            error_code=error_code,
            error_message=error_message,
            error_type="GoogleAPIError",
            context=context,
            retry_after=retry_after,
            user_action=user_action,
            technical_details=technical_details
        )
    
    def _handle_generic_google_error(self, error: GoogleAPIError, context: ErrorContext) -> ErrorResponse:
        """Handle generic Google API errors."""
        error_message = str(error)
        error_code = "GOOGLE_API_ERROR"
        
        return ErrorResponse(
            error_code=error_code,
            error_message=error_message,
            error_type="GoogleAPIError",
            context=context,
            user_action="Please check your API configuration and try again",
            technical_details={"traceback": traceback.format_exc()}
        )
    
    def handle_auth_error(self, error: GoogleAuthError, context: ErrorContext) -> ErrorResponse:
        """Handle Google authentication errors."""
        error_message = str(error)
        error_code = "AUTHENTICATION_ERROR"
        
        return ErrorResponse(
            error_code=error_code,
            error_message=error_message,
            error_type="GoogleAuthError",
            context=context,
            user_action="Please check your authentication credentials and service account file",
            technical_details={"traceback": traceback.format_exc()}
        )
    
    def handle_network_error(self, error: requests.exceptions.RequestException, context: ErrorContext) -> ErrorResponse:
        """Handle network-related errors."""
        error_message = str(error)
        error_code = "NETWORK_ERROR"
        
        # Determine retry strategy based on error type
        retry_after = 5  # Default 5 seconds
        if isinstance(error, requests.exceptions.Timeout):
            retry_after = 10
        elif isinstance(error, requests.exceptions.ConnectionError):
            retry_after = 30
        
        return ErrorResponse(
            error_code=error_code,
            error_message=error_message,
            error_type="NetworkError",
            context=context,
            retry_after=retry_after,
            user_action="Please check your internet connection and try again",
            technical_details={"traceback": traceback.format_exc()}
        )
    
    def handle_validation_error(self, error: ValueError, context: ErrorContext) -> ErrorResponse:
        """Handle validation errors."""
        error_message = str(error)
        error_code = "VALIDATION_ERROR"
        
        return ErrorResponse(
            error_code=error_code,
            error_message=error_message,
            error_type="ValidationError",
            context=context,
            user_action="Please check your input data and try again",
            technical_details={"traceback": traceback.format_exc()}
        )
    
    def handle_generic_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Handle generic errors."""
        error_message = str(error)
        error_code = "GENERIC_ERROR"
        
        return ErrorResponse(
            error_code=error_code,
            error_message=error_message,
            error_type=type(error).__name__,
            context=context,
            user_action="An unexpected error occurred. Please try again",
            technical_details={"traceback": traceback.format_exc()}
        )
    
    def _extract_error_code(self, error_details: List[Dict], status_code: int) -> str:
        """Extract error code from error details."""
        if error_details:
            for detail in error_details:
                if "reason" in detail:
                    return detail["reason"]
        
        # Map status codes to error codes
        status_mapping = {
            400: "INVALID_ARGUMENT",
            401: "UNAUTHENTICATED",
            403: "PERMISSION_DENIED",
            404: "NOT_FOUND",
            409: "ALREADY_EXISTS",
            429: "RESOURCE_EXHAUSTED",
            500: "INTERNAL",
            503: "UNAVAILABLE"
        }
        
        return status_mapping.get(status_code, "UNKNOWN_ERROR")
    
    def _extract_error_message(self, error_details: List[Dict], fallback_message: str) -> str:
        """Extract error message from error details."""
        if error_details:
            for detail in error_details:
                if "message" in detail:
                    return detail["message"]
        
        return fallback_message
    
    def _calculate_retry_after(self, status_code: int, error_code: str) -> Optional[int]:
        """Calculate retry after time in seconds."""
        if error_code in self.retryable_errors:
            if status_code == 429:  # Rate limited
                return 60  # 1 minute
            elif status_code == 503:  # Service unavailable
                return 30  # 30 seconds
            else:
                return 5  # 5 seconds
        
        return None
    
    def _create_fallback_error(self, context: ErrorContext, error_message: str) -> ErrorResponse:
        """Create a fallback error response."""
        return ErrorResponse(
            error_code="UNKNOWN_ERROR",
            error_message=error_message,
            error_type="UnknownError",
            context=context,
            user_action="An unexpected error occurred. Please contact support",
            technical_details={"traceback": traceback.format_exc()}
        )
    
    def is_retryable(self, error_response: ErrorResponse) -> bool:
        """Check if an error is retryable."""
        return error_response.error_code in self.retryable_errors
    
    def get_retry_delay(self, error_response: ErrorResponse, attempt: int) -> int:
        """Get retry delay with exponential backoff."""
        if not self.is_retryable(error_response):
            return 0
        
        base_delay = error_response.retry_after or 5
        max_delay = 300  # 5 minutes max
        
        # Exponential backoff with jitter
        delay = min(base_delay * (2 ** attempt), max_delay)
        jitter = delay * 0.1  # 10% jitter
        
        return int(delay + jitter)
    
    def log_error(self, error_response: ErrorResponse, level: str = "ERROR"):
        """Log error with appropriate level."""
        log_message = f"[{error_response.error_code}] {error_response.error_message}"
        log_data = {
            "error_code": error_response.error_code,
            "error_type": error_response.error_type,
            "service": error_response.context.service,
            "operation": error_response.context.operation,
            "timestamp": error_response.context.timestamp.isoformat(),
            "retry_after": error_response.retry_after,
            "user_action": error_response.user_action
        }
        
        if level.upper() == "ERROR":
            self.logger.error(log_message, extra=log_data)
        elif level.upper() == "WARNING":
            self.logger.warning(log_message, extra=log_data)
        else:
            self.logger.info(log_message, extra=log_data)
    
    def format_user_message(self, error_response: ErrorResponse) -> str:
        """Format user-friendly error message."""
        return f"Error: {error_response.error_message}\n\nAction: {error_response.user_action}"
    
    def format_technical_message(self, error_response: ErrorResponse) -> str:
        """Format technical error message for debugging."""
        return f"""
Technical Error Details:
- Error Code: {error_response.error_code}
- Error Type: {error_response.error_type}
- Service: {error_response.context.service}
- Operation: {error_response.context.operation}
- Timestamp: {error_response.context.timestamp.isoformat()}
- Retry After: {error_response.retry_after} seconds
- Technical Details: {error_response.technical_details}
"""
