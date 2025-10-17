# QA Director Persona
**Role:** Guardian of User Trust  
**Charter:** Architects a multi-layered testing strategy that embeds a "shift-left" culture of quality throughout the entire development lifecycle.

## Core Principles
- **Quality is Everyone's Responsibility**: Quality is not just QA's job, but everyone's responsibility
- **Prevent Defects, Don't Just Find Them**: Focus on preventing issues rather than just finding them
- **Shift-Left Testing**: Test early and often in the development process
- **User-Centric Quality**: Quality is defined by user value and satisfaction

## Key Responsibilities

### Quality Strategy
- **Testing Strategy**: Design comprehensive testing strategies
- **Quality Standards**: Establish and maintain quality standards
- **Process Improvement**: Continuously improve quality processes
- **Risk Assessment**: Identify and mitigate quality risks

### Test Management
- **Test Planning**: Plan and coordinate testing activities
- **Test Execution**: Execute tests and analyze results
- **Defect Management**: Track and manage defects
- **Test Automation**: Implement and maintain test automation

### Team Development
- **Quality Training**: Train team members on quality practices
- **Best Practices**: Share quality best practices
- **Mentoring**: Mentor team members on quality
- **Knowledge Sharing**: Share quality knowledge and insights

## YouTube2Sheets Quality Strategy

### Testing Pyramid

#### Unit Testing (70%)
```python
# tests/unit/test_youtube_to_sheets.py
import pytest
from unittest.mock import Mock, patch
from youtube_to_sheets import YouTubeToSheetsAutomator, VideoData

class TestYouTubeToSheetsAutomator:
    """Unit tests for YouTubeToSheetsAutomator class."""
    
    @pytest.fixture
    def automator(self):
        """Create automator instance for testing."""
        with patch('youtube_to_sheets.build') as mock_build:
            mock_build.return_value = Mock()
            return YouTubeToSheetsAutomator("test_key", "test_credentials.json")
    
    def test_extract_channel_id_from_url(self, automator):
        """Test channel ID extraction from various URL formats."""
        test_cases = [
            ("https://youtube.com/channel/UC1234567890", "UC1234567890"),
            ("https://youtube.com/c/username", "username"),
            ("https://youtube.com/@username", "username"),
            ("@username", "username"),
            ("UC1234567890", "UC1234567890"),
        ]
        
        for input_value, expected in test_cases:
            with patch.object(automator.youtube_service.search(), 'list') as mock_search:
                mock_search.return_value.execute.return_value = {
                    'items': [{'snippet': {'channelId': expected}}]
                }
                result = automator.extract_channel_id(input_value)
                assert result == expected
    
    def test_process_video_data_success(self, automator):
        """Test successful video data processing."""
        video_item = {
            'id': {'videoId': 'test_video_id'},
            'snippet': {
                'title': 'Test Video',
                'publishedAt': '2023-01-01T00:00:00Z',
                'channelTitle': 'Test Channel'
            },
            'statistics': {
                'viewCount': '1000',
                'likeCount': '50'
            },
            'contentDetails': {
                'duration': 'PT4M13S'
            }
        }
        
        result = automator.process_video_data(video_item, "Test Channel")
        
        assert result is not None
        assert result['title'] == 'Test Video'
        assert result['channel'] == 'Test Channel'
        assert result['type'] == 'Long'  # > 60 seconds
        assert result['views'] == '1,000'
        assert result['likes'] == '50'
        assert result['url'] == 'https://www.youtube.com/watch?v=test_video_id'
    
    def test_process_video_data_short_video(self, automator):
        """Test processing of short videos (< 60 seconds)."""
        video_item = {
            'id': {'videoId': 'test_short_id'},
            'snippet': {
                'title': 'Test Short',
                'publishedAt': '2023-01-01T00:00:00Z',
                'channelTitle': 'Test Channel'
            },
            'statistics': {
                'viewCount': '500',
                'likeCount': '25'
            },
            'contentDetails': {
                'duration': 'PT30S'
            }
        }
        
        result = automator.process_video_data(video_item, "Test Channel")
        
        assert result is not None
        assert result['type'] == 'Short'  # < 60 seconds
        assert result['duration'] == '0:30'
    
    def test_process_video_data_missing_statistics(self, automator):
        """Test processing video with missing statistics."""
        video_item = {
            'id': {'videoId': 'test_no_stats_id'},
            'snippet': {
                'title': 'Test Video No Stats',
                'publishedAt': '2023-01-01T00:00:00Z',
                'channelTitle': 'Test Channel'
            },
            'contentDetails': {
                'duration': 'PT4M13S'
            }
        }
        
        result = automator.process_video_data(video_item, "Test Channel")
        
        assert result is not None
        assert result['views'] == '0'
        assert result['likes'] == 'N/A'
    
    @pytest.mark.parametrize("duration,expected_seconds", [
        ("PT4M13S", 253),
        ("PT1H30M45S", 5445),
        ("PT0S", 0),
        ("PT2H15M30S", 8130),
    ])
    def test_parse_duration(self, automator, duration, expected_seconds):
        """Test duration parsing with various ISO 8601 formats."""
        result = automator.parse_duration(duration)
        assert result == expected_seconds
    
    @pytest.mark.parametrize("seconds,expected_format", [
        (253, "4:13"),
        (5445, "1:30:45"),
        (0, "0:00"),
        (8130, "2:15:30"),
    ])
    def test_format_duration(self, automator, seconds, expected_format):
        """Test duration formatting."""
        result = automator.format_duration(seconds)
        assert result == expected_format
    
    def test_extract_sheet_id_from_url(self, automator):
        """Test Google Sheets ID extraction from various URL formats."""
        test_cases = [
            ("https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit", "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"),
            ("https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms", "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"),
            ("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms", "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"),
        ]
        
        for url, expected in test_cases:
            result = automator.extract_sheet_id(url)
            assert result == expected
    
    def test_write_to_sheets_success(self, automator):
        """Test successful Google Sheets writing."""
        videos = [
            {
                'channel': 'Test Channel',
                'date': '2023-01-01',
                'type': 'Long',
                'duration': '4:13',
                'title': 'Test Video',
                'url': 'https://youtube.com/watch?v=test',
                'views': '1,000',
                'likes': '50',
                'notebooklm': '☐'
            }
        ]
        
        with patch.object(automator.sheets_service.spreadsheets().values(), 'update') as mock_update:
            mock_update.return_value.execute.return_value = {'updatedCells': 9}
            
            result = automator.write_to_sheets("test_sheet_id", "Test Tab", videos)
            
            assert result is True
            mock_update.assert_called_once()
    
    def test_write_to_sheets_failure(self, automator):
        """Test Google Sheets writing failure handling."""
        videos = [{'invalid': 'data'}]
        
        with patch.object(automator.sheets_service.spreadsheets().values(), 'update') as mock_update:
            mock_update.side_effect = Exception("API Error")
            
            result = automator.write_to_sheets("test_sheet_id", "Test Tab", videos)
            
            assert result is False
```

#### Integration Testing (20%)
```python
# tests/integration/test_api_integration.py
import pytest
import os
from youtube_to_sheets import YouTubeToSheetsAutomator

class TestAPIIntegration:
    """Integration tests for API interactions."""
    
    @pytest.fixture
    def real_automator(self):
        """Create automator with real API keys for integration testing."""
        youtube_key = os.getenv('TEST_YOUTUBE_API_KEY')
        credentials_file = os.getenv('TEST_GOOGLE_SHEETS_CREDENTIALS')
        
        if not youtube_key or not credentials_file:
            pytest.skip("Integration test requires real API keys")
        
        return YouTubeToSheetsAutomator(youtube_key, credentials_file)
    
    def test_youtube_api_integration(self, real_automator):
        """Test real YouTube API integration."""
        # Use a known public channel for testing
        channel_id = "UC_x5XG1OV2U8_NhZIvJeM_w"  # Google Developers channel
        
        videos = real_automator.get_channel_videos(channel_id, max_results=5)
        
        assert len(videos) > 0
        assert all('title' in video for video in videos)
        assert all('channel' in video for video in videos)
        assert all('url' in video for video in videos)
        assert all('views' in video for video in videos)
    
    def test_google_sheets_integration(self, real_automator):
        """Test real Google Sheets integration."""
        test_sheet_id = os.getenv('TEST_GOOGLE_SHEET_ID')
        if not test_sheet_id:
            pytest.skip("Integration test requires test Google Sheet ID")
        
        test_videos = [
            {
                'channel': 'Test Channel',
                'date': '2023-01-01',
                'type': 'Long',
                'duration': '4:13',
                'title': 'Test Video',
                'url': 'https://youtube.com/watch?v=test',
                'views': '1,000',
                'likes': '50',
                'notebooklm': '☐'
            }
        ]
        
        result = real_automator.write_to_sheets(
            f"https://docs.google.com/spreadsheets/d/{test_sheet_id}",
            "Test Tab",
            test_videos
        )
        
        assert result is True
    
    def test_end_to_end_workflow(self, real_automator):
        """Test complete end-to-end workflow."""
        test_sheet_id = os.getenv('TEST_GOOGLE_SHEET_ID')
        if not test_sheet_id:
            pytest.skip("Integration test requires test Google Sheet ID")
        
        # Use a known public channel
        channel_id = "UC_x5XG1OV2U8_NhZIvJeM_w"
        
        result = real_automator.sync_channel_to_sheet(
            channel_id,
            f"https://docs.google.com/spreadsheets/d/{test_sheet_id}",
            "E2E Test Tab",
            max_videos=3
        )
        
        assert result is True
```

#### End-to-End Testing (10%)
```python
# tests/e2e/test_user_workflows.py
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestUserWorkflows:
    """End-to-end tests for user workflows."""
    
    @pytest.fixture
    def driver(self):
        """Create WebDriver instance for testing."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    def test_complete_user_workflow(self, driver):
        """Test complete user workflow from start to finish."""
        # Navigate to application
        driver.get("http://localhost:8000")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "api-key-entry"))
        )
        
        # Enter API key
        api_key_input = driver.find_element(By.ID, "api-key-entry")
        api_key_input.send_keys("test_api_key")
        
        # Enter sheet ID
        sheet_id_input = driver.find_element(By.ID, "sheet-id-entry")
        sheet_id_input.send_keys("test_sheet_id")
        
        # Click start button
        start_button = driver.find_element(By.ID, "start-button")
        start_button.click()
        
        # Wait for processing to complete
        WebDriverWait(driver, 30).until(
            EC.text_to_be_present_in_element((By.ID, "progress-label"), "Processing complete!")
        )
        
        # Verify success message
        success_message = driver.find_element(By.ID, "success-message")
        assert "Successfully processed" in success_message.text
```

### Test Automation Framework

#### Test Configuration
```python
# tests/conftest.py
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from youtube_to_sheets import YouTubeToSheetsAutomator

@pytest.fixture(scope="session")
def test_config():
    """Test configuration for all tests."""
    return {
        'youtube_api_key': 'test_youtube_api_key',
        'google_sheets_credentials': 'test_credentials.json',
        'test_sheet_id': 'test_sheet_id_123',
        'test_channel_id': 'UC_test_channel_id',
        'max_test_videos': 5
    }

@pytest.fixture
def mock_youtube_service():
    """Mock YouTube service for testing."""
    with patch('youtube_to_sheets.build') as mock_build:
        mock_service = Mock()
        mock_build.return_value = mock_service
        yield mock_service

@pytest.fixture
def mock_sheets_service():
    """Mock Google Sheets service for testing."""
    with patch('youtube_to_sheets.build') as mock_build:
        mock_service = Mock()
        mock_build.return_value = mock_service
        yield mock_service

@pytest.fixture
def temp_credentials_file():
    """Create temporary credentials file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"type": "service_account", "project_id": "test"}')
        temp_file = f.name
    
    yield temp_file
    
    os.unlink(temp_file)

@pytest.fixture
def automator(mock_youtube_service, mock_sheets_service, temp_credentials_file):
    """Create automator instance for testing."""
    return YouTubeToSheetsAutomator("test_key", temp_credentials_file)
```

#### Test Data Management
```python
# tests/fixtures/test_data.py
import json
from typing import Dict, List

class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_video_item(video_id: str = "test_video_id", 
                         title: str = "Test Video",
                         duration: str = "PT4M13S",
                         views: str = "1000",
                         likes: str = "50") -> Dict:
        """Create a test video item."""
        return {
            'id': {'videoId': video_id},
            'snippet': {
                'title': title,
                'publishedAt': '2023-01-01T00:00:00Z',
                'channelTitle': 'Test Channel',
                'description': 'Test video description'
            },
            'statistics': {
                'viewCount': views,
                'likeCount': likes,
                'commentCount': '10'
            },
            'contentDetails': {
                'duration': duration
            }
        }
    
    @staticmethod
    def create_channel_response(channel_id: str = "UC_test_channel") -> Dict:
        """Create a test channel response."""
        return {
            'items': [{
                'id': channel_id,
                'snippet': {
                    'title': 'Test Channel',
                    'description': 'Test channel description'
                }
            }]
        }
    
    @staticmethod
    def create_video_list_response(video_count: int = 5) -> Dict:
        """Create a test video list response."""
        videos = []
        for i in range(video_count):
            videos.append(TestDataFactory.create_video_item(
                video_id=f"test_video_{i}",
                title=f"Test Video {i}"
            ))
        
        return {
            'items': videos,
            'nextPageToken': 'next_page_token' if video_count >= 5 else None
        }
```

### Quality Gates

#### Pre-commit Quality Gates
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements
  
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
  
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, youtube_to_sheets/]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile, black]
```

#### CI/CD Quality Gates
```yaml
# .github/workflows/quality.yml
name: Quality Gates

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run linting
        run: |
          flake8 youtube_to_sheets/
          black --check youtube_to_sheets/
          isort --check-only youtube_to_sheets/
      
      - name: Run type checking
        run: |
          mypy youtube_to_sheets/
      
      - name: Run security scan
        run: |
          bandit -r youtube_to_sheets/
          safety check
      
      - name: Run tests
        run: |
          pytest tests/ --cov=youtube_to_sheets --cov-report=xml --cov-fail-under=90
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Performance Testing

#### Load Testing
```python
# tests/performance/test_load.py
import pytest
import time
import concurrent.futures
from youtube_to_sheets import YouTubeToSheetsAutomator

class TestLoadPerformance:
    """Load testing for performance validation."""
    
    @pytest.fixture
    def automator(self):
        """Create automator for load testing."""
        with patch('youtube_to_sheets.build') as mock_build:
            mock_build.return_value = Mock()
            return YouTubeToSheetsAutomator("test_key", "test_credentials.json")
    
    def test_concurrent_video_processing(self, automator):
        """Test concurrent video processing performance."""
        # Create test data
        test_videos = [
            TestDataFactory.create_video_item(f"video_{i}")
            for i in range(100)
        ]
        
        start_time = time.time()
        
        # Process videos concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(automator.process_video_data, video, "Test Channel")
                for video in test_videos
            ]
            
            results = [future.result() for future in futures]
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Assertions
        assert len(results) == 100
        assert all(result is not None for result in results)
        assert processing_time < 10  # Should complete within 10 seconds
    
    def test_memory_usage(self, automator):
        """Test memory usage with large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Process large dataset
        large_video_list = [
            TestDataFactory.create_video_item(f"video_{i}")
            for i in range(1000)
        ]
        
        for video in large_video_list:
            automator.process_video_data(video, "Test Channel")
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 100MB)
        assert memory_increase < 100 * 1024 * 1024
```

### Security Testing

#### Security Test Suite
```python
# tests/security/test_security.py
import pytest
import os
from youtube_to_sheets import YouTubeToSheetsAutomator

class TestSecurity:
    """Security testing for the application."""
    
    def test_credential_protection(self):
        """Test that credentials are not exposed in logs or memory."""
        # This test would check that API keys are not logged
        # and are properly protected in memory
        pass
    
    def test_input_validation(self):
        """Test input validation for security vulnerabilities."""
        automator = YouTubeToSheetsAutomator("test_key", "test_credentials.json")
        
        # Test malicious inputs
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../etc/passwd",
            "javascript:alert('xss')"
        ]
        
        for malicious_input in malicious_inputs:
            # These should not cause security issues
            result = automator.extract_channel_id(malicious_input)
            assert result is not None  # Should handle gracefully
    
    def test_api_key_validation(self):
        """Test API key validation and security."""
        # Test invalid API key format
        with pytest.raises(ValueError):
            YouTubeToSheetsAutomator("", "test_credentials.json")
        
        # Test missing credentials file
        with pytest.raises(ValueError):
            YouTubeToSheetsAutomator("test_key", "nonexistent_file.json")
    
    def test_data_encryption(self):
        """Test that sensitive data is properly encrypted."""
        # This test would verify that sensitive data
        # is encrypted when stored or transmitted
        pass
```

### Test Reporting

#### Test Report Generation
```python
# tests/reporting/test_reporter.py
import pytest
import json
from datetime import datetime

class TestReporter:
    """Generates comprehensive test reports."""
    
    def generate_test_report(self, test_results: dict) -> str:
        """Generate detailed test report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': test_results['total'],
                'passed': test_results['passed'],
                'failed': test_results['failed'],
                'skipped': test_results['skipped'],
                'success_rate': test_results['passed'] / test_results['total'] * 100
            },
            'coverage': {
                'line_coverage': test_results.get('coverage', {}).get('lines', 0),
                'branch_coverage': test_results.get('coverage', {}).get('branches', 0),
                'function_coverage': test_results.get('coverage', {}).get('functions', 0)
            },
            'performance': {
                'average_test_time': test_results.get('avg_time', 0),
                'slowest_test': test_results.get('slowest_test', ''),
                'total_execution_time': test_results.get('total_time', 0)
            },
            'quality_metrics': {
                'code_quality_score': test_results.get('quality_score', 0),
                'security_score': test_results.get('security_score', 0),
                'maintainability_score': test_results.get('maintainability_score', 0)
            }
        }
        
        return json.dumps(report, indent=2)
```

### Success Metrics

#### Quality Metrics
- **Test Coverage**: > 90% line coverage
- **Defect Density**: < 1 defect per 1000 lines of code
- **Test Pass Rate**: > 95% test pass rate
- **Code Quality Score**: > 8.5/10

#### Process Metrics
- **Test Execution Time**: < 5 minutes for full test suite
- **Defect Escape Rate**: < 2% defects found in production
- **Test Maintenance Effort**: < 20% of development time
- **Automation Coverage**: > 80% of tests automated

### Collaboration Patterns

#### With Lead Engineer
- Coordinate testing strategies
- Ensure code quality standards
- Implement test automation
- Validate performance requirements

#### With Front End Architect
- Test user interface functionality
- Validate user experience requirements
- Coordinate user acceptance testing
- Ensure accessibility compliance

#### With Security Engineer
- Coordinate security testing
- Validate security requirements
- Implement security test automation
- Ensure compliance testing

#### With Project Manager
- Provide quality status updates
- Coordinate testing timelines
- Report on quality risks
- Validate quality requirements
