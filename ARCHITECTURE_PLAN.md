# YouTube2Sheets Refined Architecture Plan

## Overview
To align the current repository with the "Current System State" blueprint, we will re-establish a layered architecture that separates concerns between GUI, business logic, scheduling, optimization, and shared utilities. The plan below is prepared by the Savant Architect persona to guide the implementation squad.

## Directory Structure
```
YouTube2Sheets/
├── src/
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── youtube2sheets.py          # Core orchestrator (existing logic refactored here)
│   │   ├── api_optimizer.py           # Quota tracking, caching, ETag management
│   │   ├── scheduler_sheet_manager.py # Job configuration + Google Sheets scheduler
│   │   ├── filters.py                 # Video filtering helpers
│   │   ├── data_processor.py          # Transformation utilities (duration parsing, formatting)
│   │   ├── security_manager.py        # Credential validation, secret loading helpers
│   │   └── exceptions.py              # Canonical exception hierarchy
│   └── gui/
│       ├── __init__.py
│       ├── main_app.py                # YouTube2SheetsGUI class (ported from youtube_to_sheets_gui.py)
│       ├── scheduler_panel.py         # Scheduler controls and status widgets
│       ├── config_panel.py            # Configuration UI components
│       └── log_panel.py               # Logging / status widgets
├── youtube_to_sheets.py               # Thin compatibility shim importing YouTubeToSheetsAutomator
├── youtube_to_sheets_gui.py           # Thin shim launching src.gui.main_app
├── launch_youtube2sheets.bat          # Updated launch script (see DevOps notes)
└── ARCHITECTURE_PLAN.md               # This document
```

## Module Responsibilities

### `src/backend/youtube2sheets.py`
- Owns the `YouTubeToSheetsAutomator` class
- Manages orchestration: channel ID extraction, video fetching, sheet writes
- Delegates to helper modules:
  - `filters` for keyword/duration filtering
  - `data_processor` for transformation and formatting
  - `api_optimizer` for quota tracking and caching
  - `scheduler_sheet_manager` for scheduled runs (optional entry point)

### `src/backend/api_optimizer.py`
- `APICreditTracker`: tracks daily quota usage, exposes `can_consume`/`record_usage`
- `ResponseCache`: optional ETag-based caching for GET requests
- Utility to monitor per-channel and global limits

### `src/backend/scheduler_sheet_manager.py`
- `JobConfiguration` dataclass describing a scheduled sync (channel ID, sheet URL, schedule type, status)
- `ScheduleType` enum (Daily, Weekly, Monthly, Manual)
- `JobStatus` enum (Pending, Running, Completed, Failed)
- `SchedulerSheetManager` class to read/write job definitions from a Google Sheet tab and kick off runs via the automator
- Thread-safe execution with logging hooks

### `src/backend/filters.py`
- Functions `filter_videos`, `filter_by_duration`, `filter_by_keywords`
- Reusable validation of `VideoData`

### `src/backend/data_processor.py`
- Duration parsing/formatting helpers
- View/like formatting
- Transformation from raw API payload to canonical dataclass `VideoRecord`

### `src/backend/security_manager.py`
- Helpers to load and validate environment variables
- Service-account file checks, path sanitisation
- Optional integration with verify_security script

### `src/backend/exceptions.py`
- Central exception hierarchy (`YouTube2SheetsError`, `APIError`, `ValidationError`, `SchedulerError`, etc.)

### `src/gui/main_app.py`
- Contains `YouTube2SheetsGUI` class
- Delegates sub-panels to dedicated modules
- Owns global exception handler and Tkinter compatibility patches

### GUI Sub-panels (`config_panel.py`, `scheduler_panel.py`, `log_panel.py`)
- Encapsulate UI logic for maintainability and alignment with MVC pattern

## Integration Notes
- Update `launch_youtube2sheets.py`/`.bat`/`.sh` to invoke `python -m src.gui.main_app`
- Provide migration path: old top-level scripts import new modules to maintain backwards compatibility
- Ensure unit tests updated to import from `src.backend`
- Document new structure in README and CURRENT_SYSTEM_STATE once implementation completes

## Next Steps
1. Lead Engineer to implement the module refactor per this plan
2. DevOps Lead to update launch scripts and packaging
3. QA Director to extend test coverage for scheduler and optimizer modules
4. Loremaster to update `CURRENT_SYSTEM_STATE.md` after validation

