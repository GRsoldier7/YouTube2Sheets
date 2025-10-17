#!/usr/bin/env python3
"""Fix the desktop shortcut for YouTube2Sheets with proper configuration."""

import os
import subprocess
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent.parent
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "YouTube2Sheets - Modern 2025.lnk"
    
    # Remove existing shortcut
    if shortcut_path.exists():
        shortcut_path.unlink()
        print("✅ Removed existing shortcut")
    
    # Find Python executable
    import sys
    python_exe = Path(sys.executable)
    pythonw_exe = python_exe.parent / "pythonw.exe"
    
    if pythonw_exe.exists():
        target_exe = str(pythonw_exe)
    else:
        target_exe = str(python_exe)
    
    # Use absolute paths
    launcher_script = project_root / "LAUNCH_GUI.pyw"
    icon_file = project_root / "YouTube2Sheets.ico"
    
    print(f"Project root: {project_root}")
    print(f"Target exe: {target_exe}")
    print(f"Launcher script: {launcher_script}")
    print(f"Icon file: {icon_file}")
    
    # Create VBScript for shortcut
    vbs_content = f'''
Set shell = CreateObject("WScript.Shell")
Set shortcut = shell.CreateShortcut("{shortcut_path}")

shortcut.TargetPath = "{target_exe}"
shortcut.Arguments = "{launcher_script}"
shortcut.WorkingDirectory = "{project_root}"
shortcut.Description = "YouTube2Sheets - Professional YouTube Automation Suite"
shortcut.IconLocation = "{icon_file}"

shortcut.Save
WScript.Echo "Shortcut created successfully"
'''
    
    vbs_path = project_root / "scripts" / "_fix_shortcut_temp.vbs"
    vbs_path.write_text(vbs_content, encoding="utf-8")
    
    try:
        result = subprocess.run(["cscript", str(vbs_path)], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {result.stdout.strip()}")
        print(f"✅ Shortcut created at: {shortcut_path}")
        
        # Test the shortcut by running the command
        print("\n🧪 Testing shortcut command...")
        test_cmd = [target_exe, str(launcher_script)]
        print(f"Command: {' '.join(test_cmd)}")
        print(f"Working directory: {project_root}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating shortcut: {e}")
        print(f"Error output: {e.stderr}")
    finally:
        if vbs_path.exists():
            vbs_path.unlink()

if __name__ == "__main__":
    main()
