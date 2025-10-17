"""Tests for the scheduler CLI runner."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest import mock

import pytest

from src.backend import scheduler_runner
from src.backend.scheduler_sheet_manager import JobConfiguration, JobStatus, ScheduleType


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("YTS_SCHEDULER_SHEET_ID", raising=False)
    monkeypatch.delenv("GOOGLE_SHEET_ID", raising=False)
    monkeypatch.delenv("YTS_SCHEDULER_TAB", raising=False)


def test_load_scheduler_config_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_SHEET_ID", "primary-sheet")
    config = scheduler_runner.load_scheduler_config(sheet_id_override=None, tab_name_override=None)
    assert config.sheet_id == "primary-sheet"
    assert config.tab_name == "Scheduler"


def test_load_scheduler_config_prefers_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_SHEET_ID", "fallback")
    config = scheduler_runner.load_scheduler_config(sheet_id_override="manual", tab_name_override="Jobs")
    assert config.sheet_id == "manual"
    assert config.tab_name == "Jobs"


def test_render_due_jobs_outputs_summary() -> None:
    job = JobConfiguration(
        job_id="job-1",
        channel_input="@mkbhd",
        spreadsheet_url="https://example.com",
        tab_name="Tech",
        schedule_type=ScheduleType.DAILY,
        max_videos=50,
        status=JobStatus.PENDING,
        last_run=None,
        notes="",
    )
    job.compute_next_run(reference=datetime.now(timezone.utc))
    output = scheduler_runner.render_due_jobs([job])
    assert "job-1" in output
    assert "Tech" in output


def test_render_status_summary_counts_jobs() -> None:
    summary = scheduler_runner.render_status_summary(
        {
            "total_jobs": 3,
            "enabled_jobs": 2,
            "disabled_jobs": 1,
            "pending": 1,
            "running": 1,
            "completed": 1,
            "failed": 0,
        }
    )
    assert "Total Jobs: 3" in summary
    assert "Enabled: 2 | Disabled: 1" in summary


def test_main_dry_run(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_job = JobConfiguration(
        job_id="job-1",
        channel_input="@channel",
        spreadsheet_url="https://sheet",
        tab_name="Tab",
        schedule_type=ScheduleType.DAILY,
        max_videos=50,
        status=JobStatus.PENDING,
        last_run=None,
        notes="",
    )

    fake_manager = SimpleNamespace(fetch_jobs=lambda: [fake_job])

    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-123")
    monkeypatch.setattr(scheduler_runner, "build_scheduler_manager", lambda config, logger: fake_manager)
    monkeypatch.setattr(scheduler_runner, "collect_due_jobs", lambda manager, reference=None: [fake_job])
    monkeypatch.setattr(scheduler_runner, "configure_logging", lambda level: mock.Mock())

    exit_code = scheduler_runner.main(["--dry-run"])
    assert exit_code == 0


def test_main_execute(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-123")
    monkeypatch.setattr(
        scheduler_runner,
        "run_scheduler_once",
        lambda config, logger: {"job-1": "completed"},
    )
    monkeypatch.setattr(scheduler_runner, "configure_logging", lambda level: mock.Mock())

    exit_code = scheduler_runner.main([])
    assert exit_code == 0


