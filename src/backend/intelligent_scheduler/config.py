"""Configuration primitives for the intelligent scheduler add-on."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntelligentSchedulerConfig:
    """Runtime options for the intelligent scheduler add-on."""

    enable_startup_recovery: bool = True
    missed_job_threshold_hours: int = 6
    monitor_interval_minutes: int = 15


