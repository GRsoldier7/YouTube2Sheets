"""Tests for the intelligent scheduler engine."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.backend.intelligent_scheduler.engine import (
    IntelligentScheduler,
    IntelligentSchedulerConfig,
    MissedJob,
)
from src.backend.scheduler_sheet_manager import JobConfiguration, JobStatus, ScheduleType


def _make_job(job_id: str, *, next_run_delta_hours: float) -> JobConfiguration:
    job = JobConfiguration(
        job_id=job_id,
        channel_input="@channel",
        spreadsheet_url="https://sheet",
        tab_name="Tab",
        schedule_type=ScheduleType.DAILY,
        max_videos=50,
        status=JobStatus.PENDING,
        last_run=None,
        notes="",
    )
    job.next_run = datetime.now(timezone.utc) - timedelta(hours=next_run_delta_hours)
    return job


def test_detect_missed_jobs_returns_overdue_jobs() -> None:
    config = IntelligentSchedulerConfig(missed_job_threshold_hours=2)
    engine = IntelligentScheduler(config=config)
    overdue = _make_job("overdue", next_run_delta_hours=3)
    fresh = _make_job("fresh", next_run_delta_hours=1)
    missed = engine.detect_missed_jobs([overdue, fresh])
    assert len(missed) == 1
    assert isinstance(missed[0], MissedJob)
    assert missed[0].job.job_id == "overdue"


def test_detect_missed_jobs_empty_when_all_recent() -> None:
    config = IntelligentSchedulerConfig(missed_job_threshold_hours=4)
    engine = IntelligentScheduler(config=config)
    jobs = [_make_job("job", next_run_delta_hours=1)]
    assert engine.detect_missed_jobs(jobs) == []
