"""Lightweight intelligent scheduler engine.

This module provides a simplified implementation inspired by the helper
scripts. It focuses on detecting overdue jobs and emitting recovery
recommendations while remaining optional. Heavy orchestration (parallel
execution, real-time monitoring) can be layered on later without
impacting core behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List

from ..scheduler_sheet_manager import JobConfiguration
from .config import IntelligentSchedulerConfig


@dataclass
class MissedJob:
    job: JobConfiguration
    expected_run_time: datetime
    missed_hours: float


class IntelligentScheduler:
    """Detect overdue jobs and recommend recovery actions."""

    def __init__(self, *, config: IntelligentSchedulerConfig) -> None:
        self.config = config

    def detect_missed_jobs(self, jobs: Iterable[JobConfiguration]) -> List[MissedJob]:
        now = datetime.now(timezone.utc)
        missed: List[MissedJob] = []
        for job in jobs:
            if not job.next_run:
                continue
            delta = now - job.next_run
            missed_hours = delta.total_seconds() / 3600
            if missed_hours >= self.config.missed_job_threshold_hours:
                missed.append(MissedJob(job=job, expected_run_time=job.next_run, missed_hours=missed_hours))
        return missed


def initialize_intelligent_scheduler(config: IntelligentSchedulerConfig | None = None) -> IntelligentScheduler:
    return IntelligentScheduler(config=config or IntelligentSchedulerConfig())


