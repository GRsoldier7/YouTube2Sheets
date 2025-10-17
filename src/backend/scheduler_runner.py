"""Command-line interface for running scheduled YouTube2Sheets jobs.

This module provides a thin CLI wrapper around
`YouTubeToSheetsAutomator` and `SchedulerSheetManager` so operators can
trigger scheduled synchronization cycles, preview pending jobs, or
inspect scheduler status without opening the GUI. The design favours a
lean, dependency-light implementation: logging is configured locally
with a conservative default, and the only required configuration values
are drawn from environment variables (or CLI overrides) that already
power the core application.

Future enhancements (e.g., intelligent scheduler add-ons) can hook into
`run_scheduler_once` without altering the CLI surface.
"""

from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional

from .exceptions import ConfigurationError, SchedulerError, YouTube2SheetsError
from .scheduler_sheet_manager import JobConfiguration, JobStatus, SchedulerSheetManager
from .youtube2sheets import YouTubeToSheetsAutomator
from src.backend.intelligent_scheduler import initialize_intelligent_scheduler
from src.config import load_logging_config


LOGGER_NAME = "youtube2sheets.scheduler"


@dataclass(slots=True)
class SchedulerCLIConfig:
    """Configuration required to run the scheduler CLI."""

    sheet_id: str
    tab_name: str = "Scheduler"


def configure_logging(level: Optional[str] = None) -> logging.Logger:
    """Configure logging for the scheduler CLI and return the module logger."""

    cfg = load_logging_config()
    resolved_level = (level or cfg.level).upper()

    log_dir = Path(cfg.file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")

    root = logging.getLogger()
    root.setLevel(resolved_level)
    root.handlers.clear()

    file_handler = logging.FileHandler(cfg.file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    return logging.getLogger(LOGGER_NAME)


def load_scheduler_config(*, sheet_id_override: Optional[str], tab_name_override: Optional[str]) -> SchedulerCLIConfig:
    """Resolve scheduler configuration from CLI overrides and environment variables."""

    sheet_id = sheet_id_override or os.getenv("YTS_SCHEDULER_SHEET_ID") or os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise ConfigurationError(
            "Scheduler requires either YTS_SCHEDULER_SHEET_ID or GOOGLE_SHEET_ID to be set"
        )

    tab_name = tab_name_override or os.getenv("YTS_SCHEDULER_TAB", "Scheduler")
    return SchedulerCLIConfig(sheet_id=sheet_id, tab_name=tab_name)


def collect_due_jobs(manager: SchedulerSheetManager, *, reference: Optional[datetime] = None) -> List[JobConfiguration]:
    """Return jobs that are due for execution without running them."""

    reference_time = reference or datetime.now(timezone.utc)
    due_jobs: List[JobConfiguration] = []

    jobs = manager.fetch_jobs()
    for job in jobs:
        job.compute_next_run(reference=reference_time)
        if job.is_due(reference=reference_time):
            due_jobs.append(job)

    return due_jobs


def summarize_jobs(jobs: Iterable[JobConfiguration]) -> dict[str, int]:
    """Build a simple status summary for the supplied jobs."""

    summary = {
        "total_jobs": 0,
        "enabled_jobs": 0,
        "disabled_jobs": 0,
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
    }

    for job in jobs:
        summary["total_jobs"] += 1
        if job.status == JobStatus.FAILED:
            summary["failed"] += 1
        elif job.status == JobStatus.COMPLETED:
            summary["completed"] += 1
        elif job.status == JobStatus.RUNNING:
            summary["running"] += 1
        else:
            summary["pending"] += 1

        if job.status in (JobStatus.RUNNING, JobStatus.PENDING, JobStatus.COMPLETED):
            summary["enabled_jobs"] += 1
        else:
            summary["disabled_jobs"] += 1

    return summary


def build_scheduler_manager(config: SchedulerCLIConfig, *, logger: logging.Logger) -> SchedulerSheetManager:
    """Instantiate the YouTube automator and return its scheduler manager."""

    automator = YouTubeToSheetsAutomator()
    logger.debug("Enabling scheduler for sheet '%s' (tab '%s')", config.sheet_id, config.tab_name)
    automator.enable_scheduler(config.sheet_id, config.tab_name)

    if not automator.scheduler:
        raise SchedulerError("Scheduler failed to initialise via YouTubeToSheetsAutomator")

    return automator.scheduler


def run_scheduler_once(config: SchedulerCLIConfig, *, logger: logging.Logger) -> dict[str, str]:
    """Execute due jobs immediately and return status by job ID."""

    automator = YouTubeToSheetsAutomator()
    automator.enable_scheduler(config.sheet_id, config.tab_name)
    logger.info("Running scheduled jobs for sheet '%s' (tab '%s')", config.sheet_id, config.tab_name)
    if os.getenv("ENABLE_INTELLIGENT_SCHEDULER", "false").lower() in {"1", "true", "yes"}:
        scheduler = initialize_intelligent_scheduler()
        assert automator.scheduler is not None
        missed = scheduler.detect_missed_jobs(automator.scheduler.fetch_jobs())
        for missed_job in missed:
            logger.warning(
                "Missed job detected: %s (%.1f hours overdue)", missed_job.job.job_id, missed_job.missed_hours
            )
    return automator.run_scheduler_once()


def render_due_jobs(jobs: Iterable[JobConfiguration]) -> str:
    """Return a human-readable report for due jobs."""

    lines = []
    for job in jobs:
        next_run = job.next_run.isoformat() if job.next_run else "unscheduled"
        lines.append(
            f"- {job.job_id} | tab='{job.tab_name}' | channel_input='{job.channel_input}' | next_run={next_run}"
        )

    return "\n".join(lines) if lines else "No jobs are due for execution."


def render_status_summary(summary: dict[str, int]) -> str:
    """Produce a user-facing status summary string."""

    return (
        "Scheduler Status\n"
        f"Total Jobs: {summary['total_jobs']}\n"
        f"Enabled: {summary['enabled_jobs']} | Disabled: {summary['disabled_jobs']}\n"
        f"Pending: {summary['pending']} | Running: {summary['running']} | Completed: {summary['completed']} | Failed: {summary['failed']}"
    )


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments (exposed for testing)."""

    parser = argparse.ArgumentParser(description="YouTube2Sheets Scheduler CLI")
    parser.add_argument("--dry-run", action="store_true", help="Preview due jobs without executing them")
    parser.add_argument("--status", action="store_true", help="Show scheduler status and job counts")
    parser.add_argument("--sheet-id", dest="sheet_id", help="Override scheduler sheet ID")
    parser.add_argument("--tab-name", dest="tab_name", help="Override scheduler tab name")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity (default: INFO)",
    )

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point for the scheduler CLI."""

    args = parse_args(argv)
    logger = configure_logging(args.log_level)

    try:
        config = load_scheduler_config(sheet_id_override=args.sheet_id, tab_name_override=args.tab_name)
    except ConfigurationError as exc:
        logger.error("Configuration error: %s", exc)
        return 1

    try:
        if args.status:
            manager = build_scheduler_manager(config, logger=logger)
            jobs = manager.fetch_jobs()
            summary = summarize_jobs(jobs)
            print(render_status_summary(summary))
            return 0

        if args.dry_run:
            manager = build_scheduler_manager(config, logger=logger)
            due_jobs = collect_due_jobs(manager)
            print("Due Jobs Preview")
            print(render_due_jobs(due_jobs))
            logger.info("Dry run completed - %s job(s) due", len(due_jobs))
            return 0

        results = run_scheduler_once(config, logger=logger)
        if results:
            print("Scheduler Execution Results")
            for job_id, status in results.items():
                print(f"- {job_id}: {status}")
        else:
            print("No jobs were executed.")
        return 0

    except YouTubeToSheetsError as exc:
        logger.exception("Scheduler failed")
        print(f"Scheduler failed: {exc}")
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())


