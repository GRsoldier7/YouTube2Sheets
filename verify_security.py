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
    
    # Check if sensitive files are properly ignored
    print("\n🔍 Checking if sensitive files are ignored...")
    
    sensitive_files = ['.env', 'credentials.json']
    
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            try:
                result = subprocess.run(['git', 'check-ignore', file_path], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {file_path} is properly ignored")
                else:
                    print(f"❌ {file_path} is NOT ignored - will be committed!")
                    return False
            except Exception as e:
                print(f"⚠️ Error checking {file_path}: {e}")
        else:
            print(f"ℹ️ {file_path} does not exist")
    
    # Check git status
    print("\n🔍 Checking git status...")
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("📋 Files with changes:")
            print(result.stdout)
        else:
            print("✅ Working directory is clean")
            
    except Exception as e:
        print(f"⚠️ Error checking git status: {e}")
    
    print("\n🎉 Security verification complete!")
    return True

if __name__ == "__main__":
    verify_security()