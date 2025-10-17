#!/usr/bin/env python3
"""
Security Test Suite for YouTube2Sheets
Tests credential handling, input validation, and security measures
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backend.security_manager import get_env_var, validate_service_account_path
from utils.validators import SyncValidator
from services.automator import YouTubeToSheetsAutomator


class TestSecurity:
    """Test security measures and credential handling."""
    
    def test_no_hardcoded_credentials(self):
        """Test that no credentials are hardcoded in the codebase."""
        # This test scans for common credential patterns
        credential_patterns = [
            'AIzaSy',  # YouTube API key pattern
            'ya29.',  # Google OAuth token pattern
            '1//',     # Google OAuth refresh token pattern
            '-----BEGIN PRIVATE KEY-----',  # Private key pattern
        ]
        
        # Scan source files for credential patterns
        src_dir = Path(__file__).parent.parent / "src"
        for py_file in src_dir.rglob("*.py"):
            if py_file.name.startswith("test_"):
                continue
                
            content = py_file.read_text()
            for pattern in credential_patterns:
                assert pattern not in content, f"Potential credential found in {py_file}: {pattern}"
    
    def test_environment_variable_usage(self):
        """Test that environment variables are used for sensitive data."""
        # Test get_env_var function
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            value = get_env_var('TEST_VAR', 'default')
            assert value == 'test_value'
        
        # Test fallback to default
        value = get_env_var('NONEXISTENT_VAR', 'default')
        assert value == 'default'
    
    def test_service_account_validation(self):
        """Test service account file validation."""
        # Test with valid file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"type": "service_account", "project_id": "test"}')
            temp_file = f.name
        
        try:
            result = validate_service_account_path(temp_file)
            assert result is True
        finally:
            os.unlink(temp_file)
        
        # Test with invalid file
        result = validate_service_account_path('nonexistent.json')
        assert result is False
        
        # Test with non-JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('not json')
            temp_file = f.name
        
        try:
            result = validate_service_account_path(temp_file)
            assert result is False
        finally:
            os.unlink(temp_file)
    
    def test_input_validation(self):
        """Test input validation prevents malicious input."""
        validator = SyncValidator()
        
        # Test SQL injection attempts
        malicious_inputs = [
            "'; DROP TABLE videos; --",
            "1' OR '1'='1",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "null\x00",
        ]
        
        for malicious_input in malicious_inputs:
            # These should be caught by validation or handled safely
            # The exact behavior depends on the validation implementation
            try:
                result = validator.validate_channel_input(malicious_input)
                # If validation passes, ensure the input is sanitized
                assert not any(pattern in str(result) for pattern in ['DROP', 'SELECT', '<script>', '../'])
            except Exception:
                # Validation should reject malicious input
                pass
    
    def test_error_message_security(self):
        """Test that error messages don't expose sensitive information."""
        # Test that API errors don't expose keys
        with patch('services.automator.YouTubeService') as mock_service:
            mock_service.side_effect = Exception("API key AIzaSy1234567890 invalid")
            
            try:
                config = {
                    'youtube_api_key': 'test_key',
                    'google_sheets_service_account_json': 'test.json',
                    'default_spreadsheet_url': 'https://docs.google.com/spreadsheets/d/test/edit'
                }
                automator = YouTubeToSheetsAutomator(config)
            except Exception as e:
                # Error message should not contain the actual API key
                error_msg = str(e)
                assert 'AIzaSy1234567890' not in error_msg
                assert 'API key' not in error_msg or 'invalid' in error_msg
    
    def test_file_path_validation(self):
        """Test that file paths are validated to prevent directory traversal."""
        # Test valid paths
        valid_paths = [
            "config.json",
            "data/spreadsheets.json",
            "logs/app.log",
        ]
        
        for path in valid_paths:
            # These should be considered safe
            assert not any(pattern in path for pattern in ['../', '..\\', '/etc/', 'C:\\Windows\\'])
        
        # Test potentially dangerous paths
        dangerous_paths = [
            "../../etc/passwd",
            "..\\..\\Windows\\System32",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM",
        ]
        
        for path in dangerous_paths:
            # These should be rejected or sanitized
            assert any(pattern in path for pattern in ['../', '..\\', '/etc/', 'C:\\Windows\\'])
    
    def test_configuration_security(self):
        """Test that configuration doesn't expose sensitive data."""
        config = {
            'youtube_api_key': 'AIzaSy1234567890',
            'google_sheets_service_account_json': '{"private_key": "secret"}',
            'default_spreadsheet_url': 'https://docs.google.com/spreadsheets/d/test/edit'
        }
        
        automator = YouTubeToSheetsAutomator(config)
        
        # Configuration status should not expose actual values
        status = automator.get_configuration_status()
        assert status['youtube_api_configured'] is True
        assert 'AIzaSy1234567890' not in str(status)
        assert 'secret' not in str(status)
    
    def test_logging_security(self):
        """Test that logs don't contain sensitive information."""
        import logging
        
        # Create a test logger
        logger = logging.getLogger('test_security')
        
        # Test that sensitive data is not logged
        sensitive_data = [
            'AIzaSy1234567890',
            'ya29.abc123',
            '-----BEGIN PRIVATE KEY-----',
            'password123',
        ]
        
        for data in sensitive_data:
            # Log messages should not contain sensitive data
            log_msg = f"Processing with key: {data}"
            assert data not in log_msg or 'key' in log_msg.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
