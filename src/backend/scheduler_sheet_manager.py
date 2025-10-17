"""Google Sheets driven scheduler for YouTube2Sheets."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, Iterable, List, Optional

from googleapiclient.discovery import Resource

from .exceptions import SchedulerError

logger = logging.getLogger(__name__)


class ScheduleType(str, Enum):
    """Supported schedule cadences."""

    MANUAL = "manual"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class JobStatus(str, Enum):
    """Lifecycle status of a scheduled job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class JobConfiguration:
    """Dataclass describing a scheduler job pulled from Google Sheets."""

    job_id: str
    channel_input: str
    spreadsheet_url: str
    tab_name: str
    schedule_type: ScheduleType
    max_videos: int = 50
    status: JobStatus = JobStatus.PENDING
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    notes: str = ""

    def compute_next_run(self, *, reference: Optional[datetime] = None) -> None:
        """Compute the next run timestamp based on schedule type."""

        reference_time = reference or datetime.now(timezone.utc)

        if self.schedule_type == ScheduleType.MANUAL:
            self.next_run = None
        elif self.schedule_type == ScheduleType.DAILY:
            base = (self.last_run or reference_time) + timedelta(days=1)
            self.next_run = base.replace(hour=reference_time.hour, minute=0, second=0, microsecond=0)
        elif self.schedule_type == ScheduleType.WEEKLY:
            base = (self.last_run or reference_time) + timedelta(weeks=1)
            self.next_run = base.replace(hour=reference_time.hour, minute=0, second=0, microsecond=0)
        elif self.schedule_type == ScheduleType.MONTHLY:
            base = self.last_run or reference_time
            next_month = base.month + 1 if base.month < 12 else 1
            year = base.year + 1 if next_month == 1 else base.year
            self.next_run = base.replace(year=year, month=next_month, hour=reference_time.hour, minute=0, second=0, microsecond=0)

    def is_due(self, *, reference: Optional[datetime] = None) -> bool:
        reference_time = reference or datetime.now(timezone.utc)
        if self.schedule_type == ScheduleType.MANUAL:
            return False
        if not self.next_run:
            self.compute_next_run(reference=reference_time)
        return bool(self.next_run and self.next_run <= reference_time)


class SchedulerSheetManager:
    """Coordinator that loads jobs from a Google Sheet and executes due ones."""

    def __init__(self, sheets_service: Resource, sheet_id: str, tab_name: str = "Scheduler") -> None:
        self._sheets_service = sheets_service
        self._sheet_id = sheet_id
        self._tab_name = tab_name
        self._lock = threading.Lock()

    def _read_sheet(self) -> List[List[str]]:
        range_name = f"{self._tab_name}!A2:I"
        response = (
            self._sheets_service.spreadsheets()
            .values()
            .get(spreadsheetId=self._sheet_id, range=range_name)
            .execute()
        )
        return response.get("values", [])

    def _write_rows(self, rows: List[List[str]]) -> None:
        range_name = f"{self._tab_name}!A2"
        body = {"values": rows}
        (
            self._sheets_service.spreadsheets()
            .values()
            .update(spreadsheetId=self._sheet_id, range=range_name, valueInputOption="RAW", body=body)
            .execute()
        )

    def fetch_jobs(self) -> List[JobConfiguration]:
        with self._lock:
            rows = self._read_sheet()

        jobs: List[JobConfiguration] = []
        for idx, row in enumerate(rows, start=2):  # Data begins at row 2
            try:
                job = self._row_to_job(row, row_number=idx)
                jobs.append(job)
            except SchedulerError as exc:
                logger.error("Skipping invalid scheduler row %s: %s", idx, exc)
                continue

        return jobs

    def update_job_status(self, jobs: Iterable[JobConfiguration]) -> None:
        rows: List[List[str]] = []
        for job in jobs:
            rows.append(
                [
                    job.job_id,
                    job.channel_input,
                    job.spreadsheet_url,
                    job.tab_name,
                    job.schedule_type.value,
                    str(job.max_videos),
                    job.status.value,
                    job.last_run.isoformat() if job.last_run else "",
                    job.notes,
                ]
            )

        with self._lock:
            self._write_rows(rows)

    def run_due_jobs(self, automator, *, reference: Optional[datetime] = None) -> Dict[str, JobStatus]:  # noqa: ANN001 - automator type intentionally duck-typed
        results: Dict[str, JobStatus] = {}

        jobs = self.fetch_jobs()
        for job in jobs:
            job.compute_next_run(reference=reference)
            if not job.is_due(reference=reference):
                continue

            logger.info("Running scheduled job %s", job.job_id)
            job.status = JobStatus.RUNNING
            self.update_job_status(jobs)

            try:
                success = automator.sync_channel_to_sheet(
                    channel_input=job.channel_input,
                    spreadsheet_url=job.spreadsheet_url,
                    tab_name=job.tab_name,
                    max_videos=job.max_videos,
                )
                job.last_run = datetime.now(timezone.utc)
                job.compute_next_run()
                job.status = JobStatus.COMPLETED if success else JobStatus.FAILED
            except Exception as exc:  # pragma: no cover - defensive catch
                logger.exception("Scheduled job %s failed: %s", job.job_id, exc)
                job.status = JobStatus.FAILED
                job.notes = str(exc)

            results[job.job_id] = job.status

        if jobs:
            self.update_job_status(jobs)

        return results

    def _row_to_job(self, row: List[str], *, row_number: int) -> JobConfiguration:
        try:
            job_id = row[0]
            channel_input = row[1]
            spreadsheet_url = row[2]
            tab_name = row[3] or "YouTube Data"
            schedule_type = ScheduleType(row[4].lower())
            max_videos = int(row[5]) if len(row) > 5 and row[5] else 50
            status_value = row[6] if len(row) > 6 and row[6] else JobStatus.PENDING.value
            last_run = row[7] if len(row) > 7 else ""
            notes = row[8] if len(row) > 8 else ""
        except (IndexError, ValueError) as exc:
            raise SchedulerError(f"Invalid scheduler row at {row_number}") from exc

        parsed_last_run = None
        if last_run:
            try:
                parsed_last_run = datetime.fromisoformat(last_run)
                if not parsed_last_run.tzinfo:
                    parsed_last_run = parsed_last_run.replace(tzinfo=timezone.utc)
            except ValueError:
                logger.warning("Could not parse last_run for job %s (row %s)", job_id, row_number)

        job = JobConfiguration(
            job_id=job_id,
            channel_input=channel_input,
            spreadsheet_url=spreadsheet_url,
            tab_name=tab_name,
            schedule_type=schedule_type,
            max_videos=max_videos,
            status=JobStatus(status_value.lower()),
            last_run=parsed_last_run,
            notes=notes,
        )
        job.compute_next_run()
        return job

