"""
YouTube to Google Sheets Automation - Core Logic
==============================================

This module contains the core backend logic for fetching data from the YouTube
and Google Sheets APIs, processing it, and handling all interactions with
the Google Sheet.

Author: AI Assistant
Version: 2.0
"""

from src.backend.youtube2sheets import SyncConfig, YouTubeToSheetsAutomator

__all__ = ["YouTubeToSheetsAutomator", "SyncConfig"]