#!/usr/bin/env python3
"""
YouTube2Sheets - Diagnostic Tool
================================
Comprehensive diagnostic tool to identify and fix common issues.
Run this if you encounter any problems with the GUI.
"""

import sys
import os
import traceback
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def check_python_version():
    """Check Python version compatibility."""
    print_header("Python Version Check")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print("✅ Python version compatible")
        return True

def check_project_structure():
    """Check if project structure is intact."""
    print_header("Project Structure Check")
    
    project_root = Path(__file__).resolve().parent
    required_files = [
        "src/gui/main_app.py",
        "src/backend/youtube2sheets.py",
        "src/backend/api_optimizer.py",
        "src/backend/filters.py",
        "src/backend/dedupe.py",
        "src/backend/batch_sheets_writer.py",
        "src/backend/scheduler_sheet_manager.py",
        "src/config_loader.py",
        "LAUNCH_GUI.pyw",
        "ROBUST_LAUNCHER.pyw"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All required files present")
        return True

def check_dependencies():
    """Check if all dependencies are installed."""
    print_header("Dependencies Check")
    
    # Package name to import name mapping
    package_imports = {
        "customtkinter": "customtkinter",
        "google-api-python-client": "googleapiclient",
        "google-auth": "google.auth",
        "google-auth-oauthlib": "google_auth_oauthlib",
        "google-auth-httplib2": "google_auth_httplib2",
        "requests": "requests",
        "structlog": "structlog"
    }
    
    missing_packages = []
    for package, import_name in package_imports.items():
        try:
            __import__(import_name)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        print("\n✅ All dependencies installed")
        return True

def check_gui_import():
    """Check if GUI can be imported without errors."""
    print_header("GUI Import Check")
    
    try:
        # Add project root to path
        project_root = Path(__file__).resolve().parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Test import
        from src.gui.main_app import YouTube2SheetsGUI
        print("✅ GUI module imported successfully")
        
        # Test instantiation
        app = YouTube2SheetsGUI()
        print("✅ GUI instance created successfully")
        
        # Clean up
        app.root.destroy()
        print("✅ GUI instance destroyed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI import failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def check_environment_variables():
    """Check if required environment variables are set."""
    print_header("Environment Variables Check")
    
    required_vars = [
        "YOUTUBE_API_KEY",
        "GOOGLE_CREDENTIALS_FILE"
    ]
    
    missing_vars = []
    for var in required_vars:
        if var in os.environ and os.environ[var]:
            print(f"✅ {var}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}")
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {missing_vars}")
        print("Set them in your .env file or system environment")
        return False
    else:
        print("\n✅ All environment variables set")
        return True

def run_quick_test():
    """Run a quick functionality test."""
    print_header("Quick Functionality Test")
    
    try:
        from src.gui.main_app import YouTube2SheetsGUI
        
        # Create GUI
        app = YouTube2SheetsGUI()
        print("✅ GUI created")
        
        # Test basic functionality
        app._append_log("Test log message")
        print("✅ Logging works")
        
        # Test channel parsing
        test_channels = app._parse_multiple_channels("@testchannel, https://youtube.com/@another")
        print(f"✅ Channel parsing works: {len(test_channels)} channels")
        
        # Clean up
        app.root.destroy()
        print("✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

def main():
    """Run all diagnostic checks."""
    print("🎯 YouTube2Sheets - Diagnostic Tool")
    print("This tool will check your installation and identify any issues.")
    
    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Dependencies", check_dependencies),
        ("GUI Import", check_gui_import),
        ("Environment Variables", check_environment_variables),
        ("Quick Test", run_quick_test)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Diagnostic Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your installation is working correctly.")
        print("You can now run: python ROBUST_LAUNCHER.pyw")
    else:
        print(f"\n⚠️  {total - passed} issues found. Please fix them before running the GUI.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = main()
    input("\nPress Enter to exit...")
    sys.exit(exit_code)
