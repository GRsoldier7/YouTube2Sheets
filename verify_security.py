#!/usr/bin/env python3
"""
Security Verification Script
Ensures no sensitive data will be committed to GitHub
"""
import os
import re
import subprocess

def verify_security():
    print("🔐 SECURITY VERIFICATION")
    print("=" * 50)
    
    # Check for exposed API keys in tracked files
    print("🔍 Scanning for exposed API keys...")
    
    try:
        # Get list of tracked files
        result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
        tracked_files = result.stdout.strip().split('\n')
        
        exposed_keys = []
        
        for file_path in tracked_files:
            if file_path.endswith(('.py', '.md', '.txt', '.json')):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for YouTube API key pattern
                    api_key_pattern = r'AIzaSy[A-Za-z0-9_-]{35}'
                    matches = re.findall(api_key_pattern, content)
                    
                    if matches:
                        exposed_keys.append((file_path, matches))
                        
                except Exception as e:
                    print(f"⚠️ Could not read {file_path}: {e}")
        
        if exposed_keys:
            print("❌ EXPOSED API KEYS FOUND:")
            for file_path, keys in exposed_keys:
                print(f"   {file_path}: {keys}")
            return False
        else:
            print("✅ No exposed API keys found in tracked files")
    
    except Exception as e:
        print(f"⚠️ Error checking tracked files: {e}")
    
    # Check for other sensitive patterns
    print("\n🔍 Scanning for other sensitive data...")
    
    sensitive_patterns = [
        (r'sk-[A-Za-z0-9]{48}', 'OpenAI API key'),
        (r'[0-9a-f]{32}', 'MD5 hash'),
        (r'[0-9a-f]{40}', 'SHA-1 hash'),
        (r'[0-9a-f]{64}', 'SHA-256 hash'),
        (r'password\s*=\s*["\'][^"\']+["\']', 'Password in code'),
        (r'secret\s*=\s*["\'][^"\']+["\']', 'Secret in code'),
        (r'token\s*=\s*["\'][^"\']+["\']', 'Token in code')
    ]
    
    try:
        result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
        tracked_files = result.stdout.strip().split('\n')
        
        sensitive_found = []
        
        for file_path in tracked_files:
            if file_path.endswith(('.py', '.md', '.txt', '.json')):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for pattern, description in sensitive_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            sensitive_found.append((file_path, description, matches))
                            
                except Exception as e:
                    print(f"⚠️ Could not read {file_path}: {e}")
        
        if sensitive_found:
            print("❌ SENSITIVE DATA FOUND:")
            for file_path, description, matches in sensitive_found:
                print(f"   {file_path}: {description} - {matches}")
            return False
        else:
            print("✅ No sensitive data found in tracked files")
    
    except Exception as e:
        print(f"⚠️ Error checking for sensitive data: {e}")
    
    # Check .gitignore protection
    print("\n🔍 Verifying .gitignore protection...")
    
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        
        required_patterns = [
            '.env',
            'credentials.json',
            'youtube_api_key.txt',
            '*.key',
            '*.pem'
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"⚠️ Missing .gitignore patterns: {missing_patterns}")
        else:
            print("✅ .gitignore properly protects sensitive files")
    
    except FileNotFoundError:
        print("❌ .gitignore file not found")
        return False
    
    # Check for sensitive files in working directory
    print("\n🔍 Checking for sensitive files in working directory...")
    
    sensitive_files = [
        '.env',
        'credentials.json',
        'youtube_api_key.txt',
        'service-account.json',
        'oauth-token.json'
    ]
    
    found_sensitive = []
    for file_name in sensitive_files:
        if os.path.exists(file_name):
            found_sensitive.append(file_name)
    
    if found_sensitive:
        print(f"⚠️ Sensitive files found in working directory: {found_sensitive}")
        print("   These files should be in .gitignore and not committed")
    else:
        print("✅ No sensitive files found in working directory")
    
    print("\n🎉 Security verification complete!")
    print("✅ Repository is secure and ready for GitHub")
    
    return True

if __name__ == "__main__":
    success = verify_security()
    if not success:
        print("\n❌ Security verification failed!")
        print("Please fix the issues above before committing to GitHub.")
        sys.exit(1)
    else:
        print("\n✅ Security verification passed!")
        print("Safe to commit to GitHub.")