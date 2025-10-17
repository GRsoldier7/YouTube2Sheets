#!/usr/bin/env python3
"""
Update Desktop Shortcut - Future-Proof Version
==============================================
Creates a robust desktop shortcut that uses the diagnostic tool and robust launcher.
"""

import os
import sys
from pathlib import Path

def create_robust_desktop_shortcut():
    """Create a robust desktop shortcut with diagnostic capabilities."""
    try:
        project_root = Path(__file__).resolve().parent.parent
        desktop = Path.home() / "Desktop"
        shortcut_name = "YouTube2Sheets - Professional 2026.lnk"
        shortcut_path = desktop / shortcut_name
        
        # Get Python executable
        python_exe = Path(sys.executable)
        pythonw_exe = python_exe.parent / "pythonw.exe"
        target_exe = str(pythonw_exe) if pythonw_exe.exists() else str(python_exe)
        
        # Create VBScript for the shortcut
        vbs_content = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target_exe}"
oLink.Arguments = """{project_root}\\ROBUST_LAUNCHER.pyw"""
oLink.WorkingDirectory = "{project_root}"
oLink.Description = "YouTube2Sheets - Professional Automation Suite"
oLink.IconLocation = "{target_exe},0"
oLink.Save
'''
        
        # Write VBScript
        vbs_file = project_root / "create_shortcut.vbs"
        with open(vbs_file, 'w') as f:
            f.write(vbs_content)
        
        # Execute VBScript
        os.system(f'cscript "{vbs_file}"')
        
        # Clean up
        vbs_file.unlink()
        
        print(f"✅ Desktop shortcut created: {shortcut_path}")
        print(f"   Target: {target_exe}")
        print(f"   Arguments: {project_root}\\ROBUST_LAUNCHER.pyw")
        print(f"   Working Directory: {project_root}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create desktop shortcut: {e}")
        return False

def create_diagnostic_shortcut():
    """Create a diagnostic shortcut for troubleshooting."""
    try:
        project_root = Path(__file__).resolve().parent.parent
        desktop = Path.home() / "Desktop"
        shortcut_name = "YouTube2Sheets - Diagnostic Tool.lnk"
        shortcut_path = desktop / shortcut_name
        
        # Get Python executable
        python_exe = Path(sys.executable)
        
        # Create VBScript for the diagnostic shortcut
        vbs_content = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{python_exe}"
oLink.Arguments = """{project_root}\\DIAGNOSTIC_TOOL.py"""
oLink.WorkingDirectory = "{project_root}"
oLink.Description = "YouTube2Sheets - Diagnostic Tool"
oLink.IconLocation = "{python_exe},0"
oLink.Save
'''
        
        # Write VBScript
        vbs_file = project_root / "create_diagnostic_shortcut.vbs"
        with open(vbs_file, 'w') as f:
            f.write(vbs_content)
        
        # Execute VBScript
        os.system(f'cscript "{vbs_file}"')
        
        # Clean up
        vbs_file.unlink()
        
        print(f"✅ Diagnostic shortcut created: {shortcut_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create diagnostic shortcut: {e}")
        return False

def main():
    """Create both shortcuts."""
    print("🎯 Creating Future-Proof Desktop Shortcuts")
    print("=" * 50)
    
    # Create main shortcut
    if create_robust_desktop_shortcut():
        print("✅ Main shortcut created successfully")
    else:
        print("❌ Failed to create main shortcut")
        return 1
    
    # Create diagnostic shortcut
    if create_diagnostic_shortcut():
        print("✅ Diagnostic shortcut created successfully")
    else:
        print("❌ Failed to create diagnostic shortcut")
        return 1
    
    print("\n🎉 All shortcuts created successfully!")
    print("\nYou now have:")
    print("1. YouTube2Sheets - Professional 2026.lnk (Main application)")
    print("2. YouTube2Sheets - Diagnostic Tool.lnk (Troubleshooting)")
    print("\nIf you encounter any issues, run the Diagnostic Tool first!")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    input("\nPress Enter to exit...")
    sys.exit(exit_code)
