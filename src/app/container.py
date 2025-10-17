"""
YouTube2Sheets Dependency Injection Container
Simple dependency injection container for service management.
"""
from typing import Dict, Any, Optional
from services.youtube_service import YouTubeService, YouTubeConfig
from services.sheets_service import SheetsService, SheetsConfig
from services.automator import YouTubeToSheetsAutomator
from src.domain.models import AppConfig
from config_loader import load_config


class AppContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._config: Optional[AppConfig] = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the container with services."""
        # Load configuration
        config_data = load_config()
        self._config = AppConfig(
            youtube_api_key=config_data.get('youtube_api_key', ''),
            youtube_secondary_api_key=config_data.get('youtube_secondary_api_key'),
            google_sheets_service_account=config_data.get('google_sheets_service_account_json', ''),
            default_spreadsheet_url=config_data.get('default_spreadsheet_url', ''),
            debug_logging=config_data.get('debug', False)
        )
        
        # Register services
        self._register_services()
    
    def _register_services(self):
        """Register all services in the container."""
        # YouTube Service
        youtube_config = YouTubeConfig(
            api_key=self._config.youtube_api_key,
            secondary_api_key=self._config.youtube_secondary_api_key
        )
        self._services['youtube_service'] = YouTubeService(youtube_config)
        
        # Sheets Service
        if self._config.google_sheets_service_account:
            sheets_config = SheetsConfig(
                service_account_file=self._config.google_sheets_service_account,
                spreadsheet_id=self._extract_spreadsheet_id(self._config.default_spreadsheet_url)
            )
            self._services['sheets_service'] = SheetsService(sheets_config)
        else:
            self._services['sheets_service'] = None
        
        # Automator Service
        self._services['automator'] = YouTubeToSheetsAutomator(
            youtube_api_key=self._config.youtube_api_key,
            service_account_file=self._config.google_sheets_service_account,
            spreadsheet_url=self._config.default_spreadsheet_url
        )
    
    def _extract_spreadsheet_id(self, url: str) -> str:
        """Extract spreadsheet ID from Google Sheets URL."""
        if not url:
            return ""
        
        # Extract ID from URL like: https://docs.google.com/spreadsheets/d/ID/edit
        if '/spreadsheets/d/' in url:
            start = url.find('/spreadsheets/d/') + len('/spreadsheets/d/')
            end = url.find('/', start)
            if end == -1:
                end = url.find('?', start)
            if end == -1:
                end = len(url)
            return url[start:end]
        
        return ""
    
    def get(self, service_name: str) -> Any:
        """Get a service by name."""
        return self._services.get(service_name)
    
    def get_youtube_service(self) -> YouTubeService:
        """Get YouTube service."""
        return self._services.get('youtube_service')
    
    def get_sheets_service(self) -> Optional[SheetsService]:
        """Get Sheets service."""
        return self._services.get('sheets_service')
    
    def get_automator(self) -> YouTubeToSheetsAutomator:
        """Get Automator service."""
        return self._services.get('automator')
    
    def get_config(self) -> AppConfig:
        """Get application configuration."""
        return self._config
    
    def is_service_available(self, service_name: str) -> bool:
        """Check if a service is available."""
        service = self._services.get(service_name)
        return service is not None
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all registered services."""
        return self._services.copy()
    
    def register_service(self, name: str, service: Any) -> None:
        """Register a new service."""
        self._services[name] = service
    
    def unregister_service(self, name: str) -> None:
        """Unregister a service."""
        if name in self._services:
            del self._services[name]
