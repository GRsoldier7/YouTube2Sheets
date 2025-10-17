"""
Test Enhanced Services
Tests for enhanced error handling, logging, and async services
"""
import sys
import os
from pathlib import Path
import pytest
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.services.enhanced_error_handler import EnhancedErrorHandler, ErrorContext
from src.services.enhanced_logging import get_logger, LogContext
from src.services.async_wrapper import AsyncWrapper
from src.services.youtube_service import YouTubeService, YouTubeConfig
from src.services.sheets_service import SheetsService, SheetsConfig

class TestEnhancedServices:
    """Test enhanced services."""
    
    def test_enhanced_error_handler(self):
        """Test enhanced error handler."""
        handler = EnhancedErrorHandler()
        assert handler is not None
        assert handler.error_codes is not None
        assert handler.retryable_errors is not None
    
    def test_enhanced_logging(self):
        """Test enhanced logging."""
        logger = get_logger("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"
    
    def test_error_context(self):
        """Test error context."""
        context = ErrorContext(
            service="TestService",
            operation="test_operation",
            timestamp=datetime.now()
        )
        assert context.service == "TestService"
        assert context.operation == "test_operation"
    
    def test_log_context(self):
        """Test log context."""
        context = LogContext(
            service="TestService",
            operation="test_operation"
        )
        assert context.service == "TestService"
        assert context.operation == "test_operation"
    
    def test_async_wrapper_creation(self):
        """Test async wrapper creation."""
        youtube_config = YouTubeConfig(api_key="test_key")
        sheets_config = SheetsConfig(
            service_account_file="test.json",
            spreadsheet_id="test_id"
        )
        
        wrapper = AsyncWrapper(youtube_config, sheets_config)
        assert wrapper is not None
        assert wrapper.youtube_config == youtube_config
        assert wrapper.sheets_config == sheets_config
    
    def test_youtube_service_enhanced(self):
        """Test YouTube service with enhancements."""
        config = YouTubeConfig(api_key="test_key")
        service = YouTubeService(config)
        
        assert service.error_handler is not None
        assert service.logger is not None
        assert isinstance(service.error_handler, EnhancedErrorHandler)
    
    def test_sheets_service_enhanced(self):
        """Test Sheets service with enhancements."""
        config = SheetsConfig(
            service_account_file="test.json",
            spreadsheet_id="test_id"
        )
        service = SheetsService(config)
        
        assert service.error_handler is not None
        assert service.logger is not None
        assert isinstance(service.error_handler, EnhancedErrorHandler)
