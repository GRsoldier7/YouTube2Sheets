# YouTube2Sheets - Enhanced

A modern, enterprise-grade YouTube to Google Sheets automation tool with comprehensive error handling, async operations, and advanced monitoring.

## Features

### Core Functionality
- **YouTube Data Integration**: Fetch video data from YouTube channels using the YouTube Data API v3
- **Google Sheets Integration**: Write data to Google Sheets with automatic formatting and conditional styling
- **Modern GUI**: CustomTkinter-based interface with responsive design
- **Async Operations**: High-performance async/await patterns for I/O operations
- **Comprehensive Error Handling**: Google API best practices with detailed error reporting

### Advanced Features
- **ETag Caching**: Optimized API calls with intelligent caching
- **Duplication Checking**: Smart duplicate detection and prevention
- **Performance Monitoring**: Real-time performance metrics and logging
- **Security**: Zero credential exposure with environment variable management
- **Modular Architecture**: Clean MVVM pattern with service layer separation

## Installation

### Prerequisites
- Python 3.8+
- Google Cloud Project with YouTube Data API v3 enabled
- Google Sheets API enabled
- Service Account credentials

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd YouTube2Sheets
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_enhanced.txt
   ```

3. **Configure credentials**
   ```bash
   # Copy your service account JSON file
   cp path/to/your/service-account.json credentials.json
   
   # Set environment variables
   export YOUTUBE_API_KEY="your_youtube_api_key"
   export GOOGLE_CREDENTIALS_FILE="credentials.json"
   export DEFAULT_SPREADSHEET_URL="https://docs.google.com/spreadsheets/d/your_spreadsheet_id/edit"
   ```

4. **Run the application**
   ```bash
   python ENHANCED_LAUNCHER.pyw
   ```

## Architecture

### Service Layer
- **YouTubeService**: Handles YouTube Data API v3 operations
- **SheetsService**: Manages Google Sheets API operations
- **AsyncWrapper**: Provides async patterns for synchronous services
- **EnhancedErrorHandler**: Comprehensive error handling following Google API best practices

### GUI Layer
- **EnhancedMainApp**: Modern GUI with async operations
- **CustomTkinter**: Modern, responsive interface components
- **Performance Monitoring**: Real-time metrics and logging

### Configuration
- **Environment Variables**: Secure credential management
- **Config Loader**: Flexible configuration loading with fallbacks
- **Service Configuration**: Type-safe configuration objects

## Usage

### Basic Usage

1. **Launch the application**
   ```bash
   python ENHANCED_LAUNCHER.pyw
   ```

2. **Enter YouTube channel IDs**
   - Paste channel IDs, URLs, or @handles
   - Multiple channels supported

3. **Select target sheet and tab**
   - Choose from available Google Sheets tabs
   - Create new tabs if needed

4. **Configure filters**
   - Set minimum duration
   - Add keyword filters
   - Exclude YouTube Shorts

5. **Start the sync**
   - Click "Start Enhanced Sync"
   - Monitor progress in real-time

### Advanced Usage

#### Async Operations
```python
from src.services.async_wrapper import create_async_wrapper
from src.services.youtube_service import YouTubeService, YouTubeConfig
from src.services.sheets_service import SheetsService, SheetsConfig

# Create configurations
youtube_config = YouTubeConfig(api_key="your_api_key")
sheets_config = SheetsConfig(
    service_account_file="credentials.json",
    spreadsheet_id="your_spreadsheet_id"
)

# Create async wrapper
async_wrapper = create_async_wrapper(youtube_config, sheets_config)

# Run async operations
videos = await async_wrapper.fetch_videos_async(["UC_x5XG1OV2P6uZZ5FSM9Ttw"])
success = await async_wrapper.write_videos_async(videos, "MyTab")
```

#### Error Handling
```python
from src.services.enhanced_error_handler import EnhancedErrorHandler, ErrorContext

error_handler = EnhancedErrorHandler()

try:
    # Your API operation
    pass
except Exception as e:
    context = ErrorContext(
        service="YourService",
        operation="your_operation",
        timestamp=datetime.now()
    )
    error_response = error_handler.handle_generic_error(e, context)
    error_handler.log_error(error_response)
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | Yes |
| `GOOGLE_CREDENTIALS_FILE` | Path to service account JSON | Yes |
| `DEFAULT_SPREADSHEET_URL` | Default Google Sheets URL | Yes |
| `DEBUG` | Enable debug logging | No |

### Configuration File

Create `config.json` for additional configuration:

```json
{
  "youtube_api_key": "your_api_key",
  "google_sheets_service_account_json": "credentials.json",
  "default_spreadsheet_url": "https://docs.google.com/spreadsheets/d/your_id/edit",
  "environment": "production",
  "debug": false
}
```

## API Reference

### YouTubeService

#### Methods
- `fetch_channel_videos(channel_id: str, max_results: int = 50) -> List[Video]`
- `search_videos(query: str, max_results: int = 50) -> List[Video]`

### SheetsService

#### Methods
- `write_videos_to_sheet(videos: List[Video], tab_name: str) -> bool`
- `get_sheet_tabs() -> List[str]`
- `create_sheet_tab(tab_name: str) -> bool`

### AsyncWrapper

#### Methods
- `fetch_videos_async(channel_ids: List[str], max_results: int = 50) -> List[Dict[str, Any]]`
- `write_videos_async(videos: List[Dict[str, Any]], tab_name: str) -> bool`
- `get_tabs_async() -> List[str]`

## Error Handling

The application implements comprehensive error handling following Google API best practices:

### Error Types
- **GoogleAPIError**: YouTube and Sheets API errors
- **GoogleAuthError**: Authentication errors
- **NetworkError**: Network connectivity issues
- **ValidationError**: Input validation errors

### Error Response Structure
```json
{
  "error_code": "PERMISSION_DENIED",
  "error_message": "The caller does not have permission",
  "error_type": "GoogleAPIError",
  "context": {
    "service": "YouTube",
    "operation": "fetch_videos",
    "timestamp": "2025-01-27T10:00:00Z"
  },
  "retry_after": 60,
  "user_action": "Please check your permissions and try again"
}
```

## Performance Monitoring

### Metrics Tracked
- **API Response Time**: Average response time for API calls
- **Cache Hit Rate**: Percentage of cache hits vs misses
- **Memory Usage**: Peak memory consumption
- **Error Rate**: Percentage of failed operations
- **Throughput**: Operations per second

### Logging

Structured JSON logging with the following levels:
- **INFO**: General application flow
- **WARNING**: Non-critical issues
- **ERROR**: Recoverable errors
- **CRITICAL**: Unrecoverable errors

## Security

### Credential Management
- Zero credential exposure in code
- Environment variable based configuration
- Secure service account authentication
- No hardcoded API keys

### Best Practices
- Input validation and sanitization
- Proper error handling without information leakage
- Secure random generation for sensitive operations
- Comprehensive audit logging

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure all dependencies are installed
   pip install -r requirements_enhanced.txt
   ```

2. **Authentication Errors**
   ```bash
   # Check service account file path
   export GOOGLE_CREDENTIALS_FILE="path/to/credentials.json"
   ```

3. **API Quota Exceeded**
   - Wait for quota reset
   - Check API usage in Google Cloud Console
   - Implement rate limiting

4. **Permission Denied**
   - Verify service account has access to spreadsheet
   - Check API permissions in Google Cloud Console

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
python ENHANCED_LAUNCHER.pyw
```

## Contributing

### Development Setup

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd YouTube2Sheets
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements_enhanced.txt
   pip install -r requirements-dev.txt
   ```

4. **Run tests**
   ```bash
   pytest tests/
   ```

### Code Standards

- **Type Hints**: All functions must have type hints
- **Docstrings**: Comprehensive docstrings for all classes and functions
- **Error Handling**: Proper exception handling following Google API best practices
- **Testing**: Unit tests for all business logic
- **Logging**: Structured logging for all operations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

## Changelog

### Version 2.0.0 (Enhanced)
- Added async/await patterns for I/O operations
- Implemented comprehensive error handling
- Enhanced logging and monitoring
- Improved performance and reliability
- Added modular architecture with service layer separation

### Version 1.0.0 (Initial)
- Basic YouTube to Google Sheets sync
- CustomTkinter GUI
- Google API integration
- Basic error handling
