"""Tests for configuration loader utilities."""

from __future__ import annotations

from pathlib import Path

import json

import pytest

from src.config.loader import GUIConfig, LoggingConfig, load_gui_config, load_logging_config


def test_load_gui_config_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.config.loader.CONFIG_DIR", tmp_path)
    config = load_gui_config()
    assert isinstance(config, GUIConfig)
    assert config.window_width == 1200
    assert config.window_height == 800


def test_load_gui_config_reads_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.config.loader.CONFIG_DIR", tmp_path)
    (tmp_path / "gui.json").write_text(
        json.dumps({"theme": "light", "window": {"width": 900, "height": 700}}), encoding="utf-8"
    )
    config = load_gui_config()
    assert config.theme == "light"
    assert config.window_width == 900
    assert config.window_height == 700


def test_load_logging_config_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.config.loader.CONFIG_DIR", tmp_path)
    config = load_logging_config()
    assert isinstance(config, LoggingConfig)
    assert config.level == "INFO"
    assert config.file_path.endswith("youtube2sheets.log")


def test_load_logging_config_reads_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.config.loader.CONFIG_DIR", tmp_path)
    (tmp_path / "logging.json").write_text(
        json.dumps({"level": "DEBUG", "file": "logs/app.log", "json_logging": True}), encoding="utf-8"
    )
    config = load_logging_config()
    assert config.level == "DEBUG"
    assert config.file_path == "logs/app.log"
    assert config.json_logging is True
