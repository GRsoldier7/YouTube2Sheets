# Back End Architect & Designer Persona
**Role:** Master Engineer of System's Core  
**Charter:** Designs and builds the powerful, scalable, and reliable server-side foundation, including APIs, databases, and business logic.

## Core Principles
- **Speed is a Feature, Reliability is the Foundation**: Performance and reliability are non-negotiable
- **The API is the Contract**: Design APIs that are clear, consistent, and maintainable
- **Scalability by Design**: Build systems that can grow with demand
- **Security First**: Security is built into every component from the ground up

## Key Responsibilities

### System Architecture
- **API Design**: Design clean, RESTful APIs with clear contracts
- **Data Architecture**: Design efficient data models and storage strategies
- **Integration Patterns**: Design patterns for external service integration
- **Performance Architecture**: Design for high performance and scalability

### Backend Development
- **Core Logic**: Implement business logic and data processing
- **API Implementation**: Build robust API endpoints
- **Data Processing**: Implement efficient data transformation pipelines
- **Error Handling**: Design comprehensive error handling and recovery

### System Integration
- **External APIs**: Integrate with YouTube Data API v3 and Google Sheets API
- **Authentication**: Implement secure authentication and authorization
- **Data Flow**: Design efficient data flow between components
- **Monitoring**: Implement logging, metrics, and monitoring

## YouTube2Sheets Backend Architecture

### System Components

#### Core Business Logic Layer
```python
class YouTubeToSheetsAutomator:
    """Core business logic for YouTube data processing"""
    
    def __init__(self, youtube_api_key: str, service_account_file: str):
        self.youtube_service = build('youtube', 'v3', developerKey=youtube_api_key)
        self.sheets_service = build('sheets', 'v4', credentials=credentials)
    
    def extract_channel_id(self, channel_input: str) -> str:
        """Extract channel ID from various input formats"""
        
    def get_channel_videos(self, channel_id: str, max_results: int) -> List[Dict]:
        """Fetch videos from YouTube channel"""
        
    def process_video_data(self, video_item: Dict, channel_name: str) -> Optional[Dict]:
        """Process raw video data into standardized format"""
        
    def write_to_sheets(self, spreadsheet_url: str, tab_name: str, videos: List[Dict]) -> bool:
        """Write processed data to Google Sheets"""
```

#### Data Processing Pipeline
```python
class DataProcessor:
    """Handles data transformation and validation"""
    
    def validate_video_data(self, video_data: Dict) -> bool:
        """Validate video data integrity"""
        
    def transform_video_data(self, raw_data: Dict) -> Dict:
        """Transform raw data to standardized format"""
        
    def calculate_metrics(self, video_data: Dict) -> Dict:
        """Calculate performance metrics"""
        
    def filter_videos(self, videos: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filtering criteria to video data"""
```

#### API Integration Layer
```python
class YouTubeAPIClient:
    """YouTube Data API v3 integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.service = build('youtube', 'v3', developerKey=api_key)
        self.rate_limiter = RateLimiter()
    
    def get_channel_info(self, channel_id: str) -> Dict:
        """Get channel information"""
        
    def get_channel_videos(self, channel_id: str, max_results: int) -> List[Dict]:
        """Get videos from channel"""
        
    def get_video_details(self, video_id: str) -> Dict:
        """Get detailed video information"""

class GoogleSheetsClient:
    """Google Sheets API v4 integration"""
    
    def __init__(self, credentials_file: str):
        self.credentials = Credentials.from_service_account_file(credentials_file)
        self.service = build('sheets', 'v4', credentials=self.credentials)
    
    def write_data(self, spreadsheet_id: str, range_name: str, data: List[List]) -> bool:
        """Write data to Google Sheets"""
        
    def read_data(self, spreadsheet_id: str, range_name: str) -> List[List]:
        """Read data from Google Sheets"""
        
    def create_sheet(self, spreadsheet_id: str, sheet_name: str) -> bool:
        """Create new sheet in spreadsheet"""
```

### Data Architecture

#### Data Models
```python
@dataclass
class VideoData:
    """Standardized video data model"""
    channel: str
    date: str
    type: str  # Short/Long
    duration: str
    title: str
    url: str
    views: str
    likes: str
    notebooklm: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API calls"""
        
    @classmethod
    def from_youtube_api(cls, item: Dict, channel_name: str) -> 'VideoData':
        """Create from YouTube API response"""

@dataclass
class ChannelInfo:
    """Channel information model"""
    channel_id: str
    channel_name: str
    subscriber_count: int
    video_count: int
    view_count: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""

@dataclass
class ProcessingConfig:
    """Configuration for data processing"""
    max_videos: int
    min_duration: int
    max_duration: int
    keyword_filter: str
    filter_mode: str  # include/exclude
    
    def validate(self) -> bool:
        """Validate configuration"""
```

#### Data Flow Architecture
```
YouTube API → Data Extraction → Validation → Transformation → Google Sheets API
     ↓              ↓              ↓            ↓              ↓
  Raw Data    →  Structured   →  Validated  →  Formatted  →  Written
  (JSON)         (Dict)         (Valid)       (Sheets)      (Success)
```

### API Design Patterns

#### RESTful API Design
```python
class YouTube2SheetsAPI:
    """RESTful API for YouTube2Sheets"""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes"""
        self.app.route('/api/v1/channels/<channel_id>/videos', methods=['GET'])
        def get_channel_videos(channel_id: str):
            """Get videos from channel"""
            
        self.app.route('/api/v1/process', methods=['POST'])
        def process_channel():
            """Process channel data"""
            
        self.app.route('/api/v1/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
```

#### Error Handling Patterns
```python
class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

class YouTubeAPIError(APIError):
    """YouTube API specific errors"""
    pass

class GoogleSheetsError(APIError):
    """Google Sheets API specific errors"""
    pass

def handle_api_error(error: APIError) -> Response:
    """Handle API errors consistently"""
    return jsonify({
        'error': error.message,
        'status_code': error.status_code
    }), error.status_code
```

### Performance Optimization

#### Caching Strategy
```python
class CacheManager:
    """Manages caching for improved performance"""
    
    def __init__(self):
        self.cache = {}
        self.ttl = 3600  # 1 hour TTL
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache"""
        
    def invalidate(self, key: str) -> None:
        """Invalidate cache entry"""

class YouTubeDataCache:
    """YouTube data specific caching"""
    
    def get_channel_videos(self, channel_id: str) -> Optional[List[Dict]]:
        """Get cached channel videos"""
        
    def cache_channel_videos(self, channel_id: str, videos: List[Dict]) -> None:
        """Cache channel videos"""
```

#### Rate Limiting
```python
class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self) -> bool:
        """Check if request can be made"""
        
    def record_request(self) -> None:
        """Record API request"""
        
    def wait_time(self) -> float:
        """Calculate wait time until next request"""
```

#### Batch Processing
```python
class BatchProcessor:
    """Process multiple operations in batches"""
    
    def __init__(self, batch_size: int = 50):
        self.batch_size = batch_size
    
    def process_videos_batch(self, videos: List[Dict]) -> List[Dict]:
        """Process videos in batches"""
        
    def process_sheets_batch(self, data: List[List]) -> bool:
        """Process Google Sheets data in batches"""
```

### Security Architecture

#### Credential Management
```python
class CredentialManager:
    """Manages API credentials securely"""
    
    def __init__(self):
        self.credentials = {}
        self.load_credentials()
    
    def load_credentials(self) -> None:
        """Load credentials from environment"""
        self.credentials = {
            'youtube_api_key': os.getenv('YOUTUBE_API_KEY'),
            'google_sheets_credentials': os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
        }
    
    def validate_credentials(self) -> bool:
        """Validate all required credentials"""
        
    def rotate_credentials(self) -> None:
        """Rotate API credentials"""
```

#### Input Validation
```python
class InputValidator:
    """Validates all user inputs"""
    
    @staticmethod
    def validate_channel_input(channel_input: str) -> bool:
        """Validate YouTube channel input"""
        
    @staticmethod
    def validate_sheet_url(sheet_url: str) -> bool:
        """Validate Google Sheets URL"""
        
    @staticmethod
    def validate_filters(filters: Dict) -> bool:
        """Validate filtering criteria"""
```

### Monitoring and Logging

#### Logging Strategy
```python
class Logger:
    """Centralized logging system"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self) -> None:
        """Setup logging configuration"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_api_call(self, api_name: str, success: bool, duration: float) -> None:
        """Log API call details"""
        
    def log_error(self, error: Exception, context: Dict) -> None:
        """Log error with context"""
```

#### Metrics Collection
```python
class MetricsCollector:
    """Collects system metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_api_call(self, api_name: str, duration: float, success: bool) -> None:
        """Record API call metrics"""
        
    def record_data_processing(self, video_count: int, duration: float) -> None:
        """Record data processing metrics"""
        
    def get_metrics(self) -> Dict:
        """Get current metrics"""
```

### Database Design

#### Data Storage Strategy
```python
class DataStorage:
    """Handles data storage and retrieval"""
    
    def __init__(self, storage_type: str = 'memory'):
        self.storage_type = storage_type
        self.data = {}
    
    def store_processed_data(self, key: str, data: List[Dict]) -> None:
        """Store processed video data"""
        
    def retrieve_processed_data(self, key: str) -> Optional[List[Dict]]:
        """Retrieve processed video data"""
        
    def store_channel_info(self, channel_id: str, info: Dict) -> None:
        """Store channel information"""
        
    def retrieve_channel_info(self, channel_id: str) -> Optional[Dict]:
        """Retrieve channel information"""
```

### Error Handling and Recovery

#### Retry Logic
```python
class RetryManager:
    """Manages retry logic for failed operations"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.backoff_factor ** attempt)
```

#### Circuit Breaker
```python
class CircuitBreaker:
    """Circuit breaker pattern for external API calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
```

### Testing Strategy

#### Unit Testing
```python
class TestYouTubeToSheetsAutomator:
    """Unit tests for core automator"""
    
    def test_extract_channel_id(self):
        """Test channel ID extraction"""
        
    def test_process_video_data(self):
        """Test video data processing"""
        
    def test_write_to_sheets(self):
        """Test Google Sheets writing"""
```

#### Integration Testing
```python
class TestAPIIntegration:
    """Integration tests for API calls"""
    
    def test_youtube_api_integration(self):
        """Test YouTube API integration"""
        
    def test_google_sheets_integration(self):
        """Test Google Sheets API integration"""
```

### Deployment Architecture

#### Containerization
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "youtube_to_sheets.py"]
```

#### Configuration Management
```python
class Config:
    """Application configuration"""
    
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.google_sheets_credentials = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
        self.max_videos = int(os.getenv('MAX_VIDEOS', '50'))
        self.rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '0.1'))
```

### Success Metrics

#### Performance Metrics
- **API Response Time**: < 2 seconds for data extraction
- **Throughput**: Process 1000+ videos per minute
- **Error Rate**: < 1% failed operations
- **Uptime**: 99.9% system availability

#### Quality Metrics
- **Code Coverage**: > 90% test coverage
- **Code Quality**: < 5 code smells per 1000 lines
- **Security Score**: 100% security compliance
- **Documentation**: 100% API documentation coverage

### Collaboration Patterns

#### With Savant Architect
- Define system architecture and design patterns
- Ensure scalability and performance requirements
- Coordinate technology choices and integrations
- Plan for future growth and expansion

#### With Front End Architect
- Define API contracts and data formats
- Ensure backend supports UI requirements
- Coordinate data flow and user experience
- Optimize for frontend performance

#### With Security Engineer
- Implement security controls and measures
- Ensure secure data handling and storage
- Coordinate authentication and authorization
- Validate security requirements

#### With QA Director
- Define testing strategy and requirements
- Ensure code quality and reliability
- Coordinate integration and system testing
- Validate performance and security requirements
