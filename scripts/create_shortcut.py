#!/usr/bin/env python3
"""Create a Windows desktop shortcut for YouTube2Sheets."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    desktop = Path.home() / "Desktop"
    shortcut_path = desktop / "YouTube2Sheets - Modern 2025.lnk"

    # Find Python executable
    python_exe = None
    
    # Try virtual environment first
    if os.getenv("VIRTUAL_ENV"):
        venv_python = Path(os.getenv("VIRTUAL_ENV")) / "Scripts" / "python.exe"
        if venv_python.exists():
            python_exe = venv_python
    
    # Try system Python
    if not python_exe:
        import sys
        python_exe = Path(sys.executable)
    
    if not python_exe or not python_exe.exists():
        raise FileNotFoundError("Python executable not found. Please ensure Python is installed.")

    # Use LAUNCH_GUI.pyw as the primary launcher (ensures window visibility)
    launch_script = project_root / "LAUNCH_GUI.pyw"
    
    # Check if launch script exists
    if not launch_script.exists():
        raise FileNotFoundError(f"Launch script not found: {launch_script}")
    
    # Use custom YouTube2Sheets icon
    icon = project_root / "YouTube2Sheets.ico"
    if not icon.exists():
        # Use Python icon as fallback
        icon = str(python_exe).replace("python.exe", "pythonw.exe")

    # Target pythonw.exe (no console) with RUN_ME.pyw
    target = str(python_exe).replace("python.exe", "pythonw.exe")
    if not Path(target).exists():
        target = str(python_exe)
    
    # Escape quotes for VBScript
    arguments = str(launch_script)
    
    vbs_content = f'''
Set shell = CreateObject("WScript.Shell")
Set shortcut = shell.CreateShortcut("{shortcut_path}")
shortcut.TargetPath = "{target}"
shortcut.Arguments = "{arguments}"
shortcut.WorkingDirectory = "{project_root}"
shortcut.Description = "YouTube2Sheets - Modern 2025 Edition with Dynamic Features and Batch Processing"
shortcut.IconLocation = "{icon}"
shortcut.Save
'''

    vbs_path = project_root / "scripts" / "_create_shortcut_temp.vbs"
    vbs_path.write_text(vbs_content, encoding="utf-8")
    try:
        subprocess.run(["cscript", str(vbs_path)], check=True)
        print(f"Shortcut created at {shortcut_path}")
    finally:
        if vbs_path.exists():
            vbs_path.unlink()


if __name__ == "__main__":
    main()
