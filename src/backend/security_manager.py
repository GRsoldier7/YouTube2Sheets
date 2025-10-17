"""Security and configuration helpers for YouTube2Sheets."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .exceptions import ConfigurationError

# Load environment variables once upon import
load_dotenv()


def get_env_var(name: str, *, required: bool = True, default: Optional[str] = None) -> Optional[str]:
    """Fetch an environment variable, raising :class:`ConfigurationError` if missing."""

    value = os.getenv(name, default)
    if required and not value:
        raise ConfigurationError(f"Missing required environment variable: {name}")
    return value


def validate_service_account_path(path: str) -> str:
    """Ensure the Google service account credential file exists and is readable."""

    credential_path = Path(path).expanduser().resolve()
    if not credential_path.exists():
        raise ConfigurationError(f"Google service account file not found: {credential_path}")
    if credential_path.is_dir():
        raise ConfigurationError(f"Expected file but found directory: {credential_path}")
    return str(credential_path)


def default_spreadsheet_url() -> Optional[str]:
    """Return the optional default spreadsheet URL from the environment."""

    return os.getenv("SPREADSHEET_URL")

