"""
Phase 11: Failure Tracking

Exclusion and failure accounting for validation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from collections import defaultdict

from .base import ExclusionReason


@dataclass
class ExclusionEvent:
    """Single exclusion event."""
    timestamp: float
    reason: ExclusionReason
    detail: str = ""
    modality: str = ""


class ExclusionTracker:
    """
    Track exclusions and failures during validation.

    Maintains counts and detailed event logs for exclusion analysis.
    """

    def __init__(self):
        self.events: List[ExclusionEvent] = []
        self.counts: Dict[ExclusionReason, int] = defaultdict(int)
        self.total_recorded = 0

    def record(
        self,
        reason: ExclusionReason,
        timestamp: float = 0.0,
        detail: str = "",
        modality: str = "",
    ):
        """
        Record an exclusion event.

        Args:
            reason: Exclusion reason
            timestamp: Event timestamp
            detail: Additional details
            modality: Source modality
        """
        event = ExclusionEvent(
            timestamp=timestamp,
            reason=reason,
            detail=detail,
            modality=modality,
        )
        self.events.append(event)
        self.counts[reason] += 1
        self.total_recorded += 1

    def get_summary(self) -> Dict:
        """
        Get summary of exclusions.

        Returns:
            Dict with counts per reason and totals
        """
        total = self.total_recorded
        excluded = sum(self.counts.values())

        return {
            "total_recorded": total,
            "total_excluded": excluded,
            "exclusion_rate": excluded / max(total, 1),
            "counts": {r.value: c for r, c in self.counts.items()},
        }

    def get_by_reason(self, reason: ExclusionReason) -> List[ExclusionEvent]:
        """Get all events for a specific reason."""
        return [e for e in self.events if e.reason == reason]

    def get_recent(self, n: int = 20) -> List[ExclusionEvent]:
        """Get most recent n events."""
        return self.events[-n:]

    def clear(self):
        """Reset tracker."""
        self.events.clear()
        self.counts.clear()
        self.total_recorded = 0


def record_exclusion(
    tracker: ExclusionTracker,
    reason: ExclusionReason,
    timestamp: float = 0.0,
    detail: str = "",
    modality: str = "",
) -> None:
    """
    Record an exclusion event.

    Args:
        tracker: ExclusionTracker instance
        reason: Exclusion reason
        timestamp: Event timestamp
        detail: Additional details
        modality: Source modality
    """
    tracker.record(reason, timestamp, detail, modality)


def get_exclusion_summary(tracker: ExclusionTracker) -> Dict:
    """
    Get exclusion summary from tracker.

    Args:
        tracker: ExclusionTracker instance

    Returns:
        Summary dict
    """
    return tracker.get_summary()


def track_missing_data(
    tracker: ExclusionTracker,
    field_name: str,
    timestamp: float = 0.0,
) -> None:
    """Track missing data exclusion."""
    tracker.record(
        reason=ExclusionReason.MANUAL_EXCLUSION,
        timestamp=timestamp,
        detail=f"Missing field: {field_name}",
    )


def track_sync_failure(
    tracker: ExclusionTracker,
    delta_sec: float,
    tolerance_sec: float,
    timestamp: float = 0.0,
) -> None:
    """Track synchronization failure."""
    tracker.record(
        reason=ExclusionReason.SYNC_TOLERANCE,
        timestamp=timestamp,
        detail=f"Delta {delta_sec:.3f}s exceeds tolerance {tolerance_sec}s",
    )


def track_quality_failure(
    tracker: ExclusionTracker,
    sqi: float,
    threshold: float,
    timestamp: float = 0.0,
) -> None:
    """Track quality-based exclusion."""
    tracker.record(
        reason=ExclusionReason.LOW_SQI,
        timestamp=timestamp,
        detail=f"SQI {sqi:.3f} below threshold {threshold:.3f}",
    )


def track_reference_missing(
    tracker: ExclusionTracker,
    timestamp: float = 0.0,
) -> None:
    """Track missing reference exclusion."""
    tracker.record(
        reason=ExclusionReason.REFERENCE_MISSING,
        timestamp=timestamp,
        detail="No reference within tolerance",
    )


def track_estimate_missing(
    tracker: ExclusionTracker,
    timestamp: float = 0.0,
) -> None:
    """Track missing estimate exclusion."""
    tracker.record(
        reason=ExclusionReason.ESTIMATE_MISSING,
        timestamp=timestamp,
        detail="No valid estimate",
    )


def track_invalid_value(
    tracker: ExclusionTracker,
    value: float,
    field: str = "value",
    timestamp: float = 0.0,
) -> None:
    """Track invalid value exclusion."""
    tracker.record(
        reason=ExclusionReason.OUT_OF_RANGE,
        timestamp=timestamp,
        detail=f"Invalid {field}: {value}",
    )


def track_nan_value(
    tracker: ExclusionTracker,
    field: str = "value",
    timestamp: float = 0.0,
) -> None:
    """Track NaN value exclusion."""
    tracker.record(
        reason=ExclusionReason.NAN_VALUE,
        timestamp=timestamp,
        detail=f"NaN in {field}",
    )


def track_inf_value(
    tracker: ExclusionTracker,
    field: str = "value",
    timestamp: float = 0.0,
) -> None:
    """Track Inf value exclusion."""
    tracker.record(
        reason=ExclusionReason.INF_VALUE,
        timestamp=timestamp,
        detail=f"Inf in {field}",
    )


def track_insufficient_data(
    tracker: ExclusionTracker,
    count: int,
    minimum: int,
    timestamp: float = 0.0,
) -> None:
    """Track insufficient data exclusion."""
    tracker.record(
        reason=ExclusionReason.INSUFFICIENT_PAIRS,
        timestamp=timestamp,
        detail=f"Insufficient data: {count} < {minimum}",
    )


def format_exclusion_report(tracker: ExclusionTracker) -> str:
    """
    Format exclusion tracker as human-readable report.

    Args:
        tracker: ExclusionTracker instance

    Returns:
        Formatted report string
    """
    summary = tracker.get_summary()

    lines = [
        "Exclusion Report",
        "=" * 40,
        f"Total recorded: {summary['total_recorded']}",
        f"Total excluded: {summary['total_excluded']}",
        f"Exclusion rate: {summary['exclusion_rate']:.1%}",
        "",
        "By Reason:",
        "-" * 20,
    ]

    for reason, count in sorted(summary['counts'].items(), key=lambda x: -x[1]):
        lines.append(f"  {reason}: {count}")

    return "\n".join(lines)
