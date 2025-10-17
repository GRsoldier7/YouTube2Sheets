"""Version information for YouTube2Sheets."""

from datetime import date

__version__ = "2.0.0"
__version_info__ = (2, 0, 0)
__build_date__ = "2025-09-30"
__codename__ = "PolyChronos Elite"

# Feature flags
FEATURES = {
    "etag_caching": True,
    "video_deduplication": True,
    "batch_processing": True,
    "intelligent_scheduler": False,  # Optional add-on
    "sheet_formatting": True,
    "conditional_formatting": True,
}


def get_version_string() -> str:
    """Get a human-readable version string."""
    return f"YouTube2Sheets v{__version__} ({__codename__}) - Built {__build_date__}"


def get_feature_status() -> dict[str, bool]:
    """Get the status of all features."""
    return FEATURES.copy()

