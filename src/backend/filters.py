"""Filtering helpers for YouTube video records."""

from __future__ import annotations

from typing import Iterable, List, Sequence

from .data_processor import VideoRecord


def filter_by_duration(records: Iterable[VideoRecord], min_seconds: int | None = None, max_seconds: int | None = None) -> List[VideoRecord]:
    """Return records whose durations fall within the provided bounds."""

    selected: List[VideoRecord] = []
    for record in records:
        # Convert duration string back to seconds for comparison
        parts = record.duration.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            total_seconds = hours * 3600 + minutes * 60 + seconds
        else:
            minutes, seconds = map(int, parts)
            total_seconds = minutes * 60 + seconds

        if min_seconds is not None and total_seconds < min_seconds:
            continue
        if max_seconds is not None and total_seconds > max_seconds:
            continue
        selected.append(record)

    return selected


def filter_by_keywords(records: Iterable[VideoRecord], keywords: Sequence[str], mode: str = "include") -> List[VideoRecord]:
    """Filter records by keyword presence in the title.

    Parameters
    ----------
    records:
        The video records to filter.
    keywords:
        The keywords to match against video titles (case-insensitive).
    mode:
        ``"include"`` to keep records containing any keyword,
        ``"exclude"`` to remove records containing any keyword.
    """

    if not keywords:
        return list(records)

    lowered = [kw.lower() for kw in keywords]
    selected: List[VideoRecord] = []

    for record in records:
        title = record.title.lower()
        has_keyword = any(kw in title for kw in lowered)

        if mode == "include" and has_keyword:
            selected.append(record)
        elif mode == "exclude" and not has_keyword:
            selected.append(record)

    return selected


def apply_filters(records: Iterable[VideoRecord], *, min_seconds: int | None = None, max_seconds: int | None = None, keywords: Sequence[str] | None = None, keyword_mode: str = "include") -> List[VideoRecord]:
    """Apply duration and keyword filters in sequence and return a list."""

    filtered = list(records)
    filtered = filter_by_duration(filtered, min_seconds=min_seconds, max_seconds=max_seconds)
    filtered = filter_by_keywords(filtered, keywords or [], mode=keyword_mode)
    return filtered

