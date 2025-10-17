"""
Configuration loader for YouTube2Sheets application.
Handles loading and saving of API keys and settings.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables and config file."""
    config = {}
    
    # Load from config file first (higher priority)
    # Look for config.json in the current working directory
    config_file = Path('config.json')
    if not config_file.exists():
        # Try in the parent directory if not found
        config_file = Path('../config.json')
    
    if config_file.exists():
        try:
            print(f"Loading config from: {config_file.absolute()}")
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                print(f"Loaded config keys: {list(file_config.keys())}")
                config.update(file_config)
                print(f"Updated config keys: {list(config.keys())}")
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    else:
        print(f"Config file not found: {config_file.absolute()}")
    
    # Then override with environment variables (only if they exist)
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    if youtube_key:
        config['youtube_api_key'] = youtube_key
    
    service_account = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON') or os.getenv('GOOGLE_CREDENTIALS_FILE')
    if service_account:
        config['google_sheets_service_account_json'] = service_account
    
    spreadsheet_url = os.getenv('DEFAULT_SPREADSHEET_URL')
    if spreadsheet_url:
        config['default_spreadsheet_url'] = spreadsheet_url
    
    return config


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file."""
    try:
        config_file = Path('config.json')
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def get_env_var(key: str, default: str = '') -> str:
    """Get environment variable with fallback."""
    return os.getenv(key, default)
