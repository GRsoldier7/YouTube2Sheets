#!/usr/bin/env python3
"""
Configuration Loader for YouTube2Sheets
Loads configuration from environment variables and .env file
"""

import os
from pathlib import Path

def load_config():
    """Load configuration with security-first approach (environment variables take priority)."""
    import json
    
    config = {}
    
    # SECURITY: Check environment variables first (most secure)
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    service_account = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
    spreadsheet_url = os.getenv('DEFAULT_SPREADSHEET_URL')
    
    # If environment variables are set, use them (production mode)
    if youtube_key and service_account:
        config['youtube_api_key'] = youtube_key
        config['google_sheets_service_account_json'] = service_account
        if spreadsheet_url:
            config['default_spreadsheet_url'] = spreadsheet_url
        print("Using environment variables for configuration (secure)")
        return config
    
    # Fallback to .env file
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"')
        
        # Re-check environment variables after loading .env
        youtube_key = os.getenv('YOUTUBE_API_KEY')
        service_account = os.getenv('GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON')
        spreadsheet_url = os.getenv('DEFAULT_SPREADSHEET_URL')
        
        if youtube_key and service_account:
            config['youtube_api_key'] = youtube_key
            config['google_sheets_service_account_json'] = service_account
            if spreadsheet_url:
                config['default_spreadsheet_url'] = spreadsheet_url
            print("Using .env file for configuration")
            return config
    
    # Last resort: load from config.json (development mode)
    config_file = Path(__file__).parent / "config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
            print("Using config.json for configuration (development mode)")
        except Exception as e:
            print(f"Warning: Could not load config.json: {e}")
    
    # Final environment variable overrides
    if youtube_key:
        config['youtube_api_key'] = youtube_key
    if service_account:
        config['google_sheets_service_account_json'] = service_account
    if spreadsheet_url:
        config['default_spreadsheet_url'] = spreadsheet_url
    
    return config

def save_config(youtube_key, service_account, spreadsheet_url):
    """Save configuration to environment variables."""
    os.environ['YOUTUBE_API_KEY'] = youtube_key
    os.environ['GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON'] = service_account
    os.environ['DEFAULT_SPREADSHEET_URL'] = spreadsheet_url
    
    # Also save to .env file
    env_file = Path(__file__).parent / ".env"
    with open(env_file, 'w') as f:
        f.write("# YouTube2Sheets Configuration\n")
        f.write(f"YOUTUBE_API_KEY=\"{youtube_key}\"\n")
        f.write(f"GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON=\"{service_account}\"\n")
        f.write(f"DEFAULT_SPREADSHEET_URL=\"{spreadsheet_url}\"\n")
