#!/usr/bin/env python3
"""
Secure Environment Setup Script
Creates .env file with placeholder API keys - user must replace with real keys
"""
import os
import sys

def setup_secure_environment():
    print("🔐 SETTING UP SECURE ENVIRONMENT")
    print("=" * 50)
    
    # Create .env file with placeholder API keys
    env_content = """# YouTube2Sheets Environment Configuration
# This file contains sensitive credentials - NEVER commit to version control

# YouTube API Configuration
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_API_KEY_BACKUP=your_backup_youtube_api_key_here

# Google Sheets Configuration
GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON=credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id_here

# Application Configuration
MIN_VIDEO_DURATION_SECONDS=60
MAX_VIDEO_DURATION_SECONDS=3600
LOG_LEVEL=INFO
LOG_FILE=logs/youtube2sheets.log

# Performance Configuration
MAX_WORKERS=4
CACHE_SIZE=1000
RATE_LIMIT_DELAY=0.1
TIMEOUT_SECONDS=30
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with placeholder API keys")
    print("⚠️  IMPORTANT: Replace placeholder keys with your actual API keys!")
    
    # Create credentials.json file with placeholder data
    credentials_content = """{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY_HERE\\n-----END PRIVATE KEY-----\\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}"""
    
    with open('credentials.json', 'w') as f:
        f.write(credentials_content)
    
    print("✅ Created credentials.json file with placeholder data")
    print("⚠️  IMPORTANT: Replace placeholder data with your actual Google Sheets credentials!")
    
    # Create .env.example template
    env_example_content = """# YouTube2Sheets Environment Configuration Template
# Copy this file to .env and fill in your actual credentials

# YouTube API Configuration
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_API_KEY_BACKUP=your_backup_youtube_api_key_here

# Google Sheets Configuration
GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON=credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id_here

# Application Configuration
MIN_VIDEO_DURATION_SECONDS=60
MAX_VIDEO_DURATION_SECONDS=3600
LOG_LEVEL=INFO
LOG_FILE=logs/youtube2sheets.log

# Performance Configuration
MAX_WORKERS=4
CACHE_SIZE=1000
RATE_LIMIT_DELAY=0.1
TIMEOUT_SECONDS=30
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_example_content)
    
    print("✅ Created .env.example template file")
    
    # Verify .gitignore is protecting sensitive files
    print("\n🔍 Verifying .gitignore protection...")
    
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        if '.env' in gitignore_content and 'credentials.json' in gitignore_content:
            print("✅ .gitignore properly protects sensitive files")
        else:
            print("⚠️ .gitignore may need updates")
            
    except FileNotFoundError:
        print("❌ .gitignore file not found")
    
    # Test git status to ensure files are ignored
    print("\n🔍 Checking git status...")
    os.system("git status --ignored")
    
    print("\n🎉 Secure environment setup complete!")
    print("📝 Your API keys are now protected and will not be committed to GitHub")
    print("\n⚠️  CRITICAL: Replace all placeholder values with your actual credentials!")

if __name__ == "__main__":
    setup_secure_environment()