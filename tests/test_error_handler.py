"""
Tests for Enhanced Error Handler
"""
import pytest
from datetime import datetime
from src.services.enhanced_error_handler import EnhancedErrorHandler, ErrorContext
from googleapiclient.errors import HttpError

class TestEnhancedErrorHandler:
    """Test cases for EnhancedErrorHandler."""
    
    def test_init(self):
        """Test error handler initialization."""
        handler = EnhancedErrorHandler()
        assert handler is not None
        assert handler.error_codes is not None
        assert handler.retryable_errors is not None
    
    def test_handle_http_error(self):
        """Test HTTP error handling."""
        handler = EnhancedErrorHandler()
        context = ErrorContext(
            service="TestService",
            operation="test_operation",
            timestamp=datetime.now()
        )
        
        # Mock HttpError
        mock_error = Mock(spec=HttpError)
        mock_error.resp.status = 403
        mock_error.error_details = [{"reason": "PERMISSION_DENIED"}]
        
        response = handler.handle_google_api_error(mock_error, context)
        
        assert response.error_code == "PERMISSION_DENIED"
        assert response.error_type == "GoogleAPIError"
        assert response.context == context
    
    def test_handle_generic_error(self):
        """Test generic error handling."""
        handler = EnhancedErrorHandler()
        context = ErrorContext(
            service="TestService",
            operation="test_operation",
            timestamp=datetime.now()
        )
        
        error = ValueError("Test error")
        response = handler.handle_generic_error(error, context)
        
        assert response.error_code == "GENERIC_ERROR"
        assert response.error_type == "ValueError"
        assert response.context == context
    
    def test_is_retryable(self):
        """Test retryable error detection."""
        handler = EnhancedErrorHandler()
        context = ErrorContext(
            service="TestService",
            operation="test_operation",
            timestamp=datetime.now()
        )
        
        # Test retryable error
        mock_error = Mock(spec=HttpError)
        mock_error.resp.status = 503
        mock_error.error_details = [{"reason": "UNAVAILABLE"}]
        
        response = handler.handle_google_api_error(mock_error, context)
        assert handler.is_retryable(response) is True
        
        # Test non-retryable error
        mock_error.resp.status = 400
        mock_error.error_details = [{"reason": "INVALID_ARGUMENT"}]
        
        response = handler.handle_google_api_error(mock_error, context)
        assert handler.is_retryable(response) is False
    
    def test_get_retry_delay(self):
        """Test retry delay calculation."""
        handler = EnhancedErrorHandler()
        context = ErrorContext(
            service="TestService",
            operation="test_operation",
            timestamp=datetime.now()
        )
        
        mock_error = Mock(spec=HttpError)
        mock_error.resp.status = 503
        mock_error.error_details = [{"reason": "UNAVAILABLE"}]
        
        response = handler.handle_google_api_error(mock_error, context)
        delay = handler.get_retry_delay(response, 0)
        
        assert delay > 0
        assert delay <= 300  # Max delay
