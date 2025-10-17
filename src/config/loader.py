"""Utility functions for loading structured configuration files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


CONFIG_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class GUIConfig:
    """GUI configuration options consumed by the CustomTkinter front-end."""

    theme: str
    window_width: int
    window_height: int


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration shared between GUI and backend."""

    level: str
    file_path: str
    json_logging: bool


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_gui_config() -> GUIConfig:
    """Load GUI configuration, falling back to defaults when missing."""

    default = GUIConfig(theme="dark", window_width=1200, window_height=800)
    config_path = CONFIG_DIR / "gui.json"
    if not config_path.exists():
        return default

    data = _load_json(config_path)
    return GUIConfig(
        theme=data.get("theme", default.theme),
        window_width=int(data.get("window", {}).get("width", default.window_width)),
        window_height=int(data.get("window", {}).get("height", default.window_height)),
    )


def load_logging_config() -> LoggingConfig:
    """Load logging configuration from file with defaults."""

    default = LoggingConfig(level="INFO", file_path="logs/youtube2sheets.log", json_logging=False)
    config_path = CONFIG_DIR / "logging.json"
    if not config_path.exists():
        return default

    data = _load_json(config_path)
    return LoggingConfig(
        level=str(data.get("level", default.level)),
        file_path=str(data.get("file", default.file_path)),
        json_logging=bool(data.get("json_logging", default.json_logging)),
    )


