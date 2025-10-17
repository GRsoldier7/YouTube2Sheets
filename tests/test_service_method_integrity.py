#!/usr/bin/env python3
"""
Service Method Integrity Tests
Validates that all service methods exist and prevents naming inconsistencies
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.sheets_service import SheetsService
from src.services.youtube_service import YouTubeService
from src.domain.models import SheetsConfig, YouTubeConfig


class TestServiceMethodIntegrity:
    """Test service method integrity and naming consistency."""
    
    def test_sheets_service_methods_exist(self):
        """Verify all expected SheetsService methods exist."""
        expected_methods = [
            'create_sheet_tab',
            'create_table_structure', 
            'get_existing_tabs',  # NOT get_sheet_tabs
            'verify_access',
            'is_at_cell_limit',
            'write_videos_to_sheet'
        ]
        
        for method_name in expected_methods:
            assert hasattr(SheetsService, method_name), \
                f"SheetsService missing method: {method_name}"
    
    def test_no_deprecated_method_names(self):
        """Ensure deprecated method names are not present."""
        deprecated = ['get_sheet_tabs']
        
        for method_name in deprecated:
            assert not hasattr(SheetsService, method_name), \
                f"SheetsService has deprecated method: {method_name}"
    
    def test_youtube_service_methods_exist(self):
        """Verify all expected YouTubeService methods exist."""
        expected_methods = [
            'get_channel_videos',
            'resolve_channel_id',
            '_make_request',
            '_parse_duration'
        ]
        
        for method_name in expected_methods:
            assert hasattr(YouTubeService, method_name), \
                f"YouTubeService missing method: {method_name}"
    
    def test_method_signatures_match_usage(self):
        """Test that method signatures match expected usage patterns."""
        # Test SheetsService method signatures
        sheets_methods = {
            'create_sheet_tab': ('tab_name',),
            'get_existing_tabs': (),
            'verify_access': (),
            'is_at_cell_limit': (),
            'write_videos_to_sheet': ('tab_name', 'videos')
        }
        
        for method_name, expected_args in sheets_methods.items():
            method = getattr(SheetsService, method_name)
            import inspect
            sig = inspect.signature(method)
            actual_args = [param for param in sig.parameters.keys() if param != 'self']
            
            # Check that we have the expected number of arguments
            assert len(actual_args) == len(expected_args), \
                f"{method_name} has {len(actual_args)} args, expected {len(expected_args)}"
    
    def test_no_typos_in_method_names(self):
        """Test for common typos in method names."""
        common_typos = [
            ('get_sheet_tabs', 'get_existing_tabs'),
            ('get_existing_tab', 'get_existing_tabs'),
            ('create_sheet_tabs', 'create_sheet_tab'),
            ('write_video_to_sheet', 'write_videos_to_sheet'),
            ('verify_acess', 'verify_access'),
            ('is_at_cell_limits', 'is_at_cell_limit')
        ]
        
        for typo, correct in common_typos:
            assert not hasattr(SheetsService, typo), \
                f"SheetsService has typo method '{typo}', should be '{correct}'"
    
    def test_method_names_are_consistent(self):
        """Test that method names follow consistent naming patterns."""
        sheets_methods = [
            'create_sheet_tab',
            'get_existing_tabs', 
            'verify_access',
            'is_at_cell_limit',
            'write_videos_to_sheet'
        ]
        
        # All method names should be snake_case
        for method_name in sheets_methods:
            assert method_name.islower(), f"Method {method_name} should be lowercase"
            assert '_' in method_name or method_name.isalpha(), \
                f"Method {method_name} should use snake_case"
    
    def test_method_docstrings_exist(self):
        """Test that all public methods have docstrings."""
        public_methods = [
            'create_sheet_tab',
            'create_table_structure',
            'get_existing_tabs',
            'verify_access', 
            'is_at_cell_limit',
            'write_videos_to_sheet'
        ]
        
        for method_name in public_methods:
            method = getattr(SheetsService, method_name)
            assert method.__doc__ is not None, \
                f"Method {method_name} missing docstring"
            assert len(method.__doc__.strip()) > 10, \
                f"Method {method_name} has insufficient docstring"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
