"""Canonical exception hierarchy for the YouTube2Sheets backend."""

from __future__ import annotations


class YouTube2SheetsError(Exception):
    """Base exception for all custom errors in the YouTube2Sheets backend."""


class ConfigurationError(YouTube2SheetsError):
    """Raised when required configuration or environment values are missing."""


class APIError(YouTube2SheetsError):
    """Raised for failures when communicating with external APIs."""

    def __init__(self, message: str, api_name: str | None = None, status_code: int | None = None) -> None:
        super().__init__(message)
        self.api_name = api_name
        self.status_code = status_code


class ValidationError(YouTube2SheetsError):
    """Raised when inbound data is malformed or invalid."""


class ProcessingError(YouTube2SheetsError):
    """Raised when video processing or transformation fails."""


class SchedulerError(YouTube2SheetsError):
    """Raised for scheduler-specific problems (job configuration, execution, etc.)."""

