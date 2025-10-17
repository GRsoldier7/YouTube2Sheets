"""
Secure Configuration Loader
Implements proper credential masking and security controls
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class SecureConfigLoader:
    """Secure configuration loader with credential masking."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        self._config_cache: Optional[Dict[str, Any]] = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration with proper security controls."""
        if self._config_cache is not None:
            return self._config_cache
            
        config = {}
        
        # Load from config.json first
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.logger.info(f"Loaded config from {self.config_file}")
            except Exception as e:
                self.logger.error(f"Error loading config from {self.config_file}: {e}")
        
        # Override with environment variables (higher priority)
        env_overrides = {
            'youtube_api_key': os.environ.get('YOUTUBE_API_KEY'),
            'youtube_secondary_api_key': os.environ.get('YOUTUBE_SECONDARY_API_KEY'),
            'google_sheets_service_account_json': os.environ.get('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON'),
            'default_spreadsheet_url': os.environ.get('DEFAULT_SPREADSHEET_URL'),
            'environment': os.environ.get('ENVIRONMENT', 'production'),
            'debug': os.environ.get('DEBUG', 'false').lower() == 'true'
        }
        
        for key, value in env_overrides.items():
            if value is not None:
                config[key] = value
                self.logger.info(f"Overrode {key} from environment")
        
        # Validate required keys
        required_keys = ['youtube_api_key', 'google_sheets_service_account_json']
        missing_keys = [key for key in required_keys if not config.get(key)]
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
        
        # Mask sensitive values for logging
        self._config_cache = self._mask_sensitive_config(config)
        
        return self._config_cache
    
    def _mask_sensitive_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive configuration values for safe logging."""
        masked_config = config.copy()
        
        sensitive_keys = [
            'youtube_api_key',
            'youtube_secondary_api_key',
            'google_sheets_service_account_json'
        ]
        
        for key in sensitive_keys:
            if key in masked_config and masked_config[key]:
                value = str(masked_config[key])
                if len(value) > 8:
                    masked_config[key] = f"{value[:4]}...{value[-4:]}"
                else:
                    masked_config[key] = "***MASKED***"
        
        return masked_config
    
    def get_unmasked_config(self) -> Dict[str, Any]:
        """Get unmasked configuration for actual use."""
        if self._config_cache is None:
            self.load_config()
        
        # Return original config without masking
        config = {}
        
        # Load from config.json first
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading config from {self.config_file}: {e}")
        
        # Override with environment variables
        env_overrides = {
            'youtube_api_key': os.environ.get('YOUTUBE_API_KEY'),
            'youtube_secondary_api_key': os.environ.get('YOUTUBE_SECONDARY_API_KEY'),
            'google_sheets_service_account_json': os.environ.get('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON'),
            'default_spreadsheet_url': os.environ.get('DEFAULT_SPREADSHEET_URL'),
            'environment': os.environ.get('ENVIRONMENT', 'production'),
            'debug': os.environ.get('DEBUG', 'false').lower() == 'true'
        }
        
        for key, value in env_overrides.items():
            if value is not None:
                config[key] = value
        
        return config
    
    def validate_config(self) -> bool:
        """Validate configuration security."""
        try:
            config = self.get_unmasked_config()
            
            # Check for required keys
            required_keys = ['youtube_api_key', 'google_sheets_service_account_json']
            missing_keys = [key for key in required_keys if not config.get(key)]
            
            if missing_keys:
                self.logger.error(f"Missing required configuration keys: {missing_keys}")
                return False
            
            # Check API key format
            youtube_key = config.get('youtube_api_key', '')
            if not youtube_key.startswith('AIza'):
                self.logger.error("Invalid YouTube API key format")
                return False
            
            # Check service account file exists
            service_account_file = config.get('google_sheets_service_account_json')
            if service_account_file and not os.path.exists(service_account_file):
                self.logger.error(f"Service account file not found: {service_account_file}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False

# Global instance
secure_config_loader = SecureConfigLoader()

def load_config() -> Dict[str, Any]:
    """Load configuration with security controls."""
    return secure_config_loader.load_config()

def get_unmasked_config() -> Dict[str, Any]:
    """Get unmasked configuration for actual use."""
    return secure_config_loader.get_unmasked_config()

def validate_config() -> bool:
    """Validate configuration security."""
    return secure_config_loader.validate_config()

