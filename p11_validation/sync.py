"""
Phase 11: Synchronization Layer

Explicit timestamp-based synchronization for multi-sensor validation.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from collections import deque

from .base import (
    Modality,
    SyncConfig,
    ValidationStatus,
    ExclusionReason,
    HRRecord,
    RRRecord,
    ValidationResult,
)


def compute_time_delta(
    ts1: float,
    ts2: float
) -> float:
    """
    Compute time delta between two timestamps.
    """
    return ts2 - ts1


def validate_timestamp_sequence(
    timestamps: List[float],
    max_backwards_jump: float = 0.1,
) -> Tuple[bool, List[int]]:
    """Validate that timestamps are monotonically increasing."""
    if len(timestamps) < 2:
        return True, []
    invalid = []
    for i in range(1, len(timestamps)):
        delta = timestamps[i] - timestamps[i-1]
        if delta < -max_backwards_jump:
            invalid.append(i)
    return len(invalid) == 0, invalid


def detect_clock_drift(
    ref_timestamps: List[float],
    test_timestamps: List[float],
    window_sec: float = 60.0,
) -> Optional[Dict[str, float]]:
    """Detect clock drift between reference and test sensor timestamps."""
    if len(ref_timestamps) < 2 or len(test_timestamps) < 2:
        return None
    ref_rate = np.diff(ref_timestamps)
    test_rate = np.diff(test_timestamps)
    if len(ref_rate) == 0 or len(test_rate) == 0:
        return None
    mean_ref_rate = np.mean(ref_rate)
    mean_test_rate = np.mean(test_rate)
    if mean_ref_rate <= 0 or mean_test_rate <= 0:
        return None
    drift_ratio = mean_test_rate / mean_ref_rate
    return {
        "drift_ratio": float(drift_ratio),
        "drift_ppm": float((drift_ratio - 1.0) * 1e6),
        "mean_ref_rate_sec": float(mean_ref_rate),
        "mean_test_rate_sec": float(mean_test_rate),
    }


class Synchronizer:
    """Timestamp-based synchronization for multi-sensor data."""

    def __init__(self, config: Optional[SyncConfig] = None):
        self.config = config or SyncConfig()
        self._last_drift_correction = 0.0
        self._drift_history = deque(maxlen=100)

    def align(
        self,
        estimates: List[HRRecord],
        references: List[HRRecord],
    ) -> List[ValidationResult]:
        """Align HR estimates with reference measurements."""
        results = []
        for est in estimates:
            result = self._align_single(est, references)
            results.append(result)
        return results

    def _align_single(
        self,
        estimate: HRRecord,
        references: List[HRRecord],
    ) -> ValidationResult:
        """Align one estimate against references."""
        result = ValidationResult(
            status=ValidationStatus.PENDING,
            modality=estimate.modality,
            estimate=estimate.hr,
            estimate_timestamp=estimate.timestamp,
            sqi=estimate.sqi,
            confidence=estimate.confidence,
        )

        if estimate.timestamp is None:
            result.status = ValidationStatus.EXCLUDED
            result.exclusion_reason = ExclusionReason.MISSING_TIMESTAMP
            return result

        if np.isnan(estimate.hr) or np.isinf(estimate.hr):
            result.status = ValidationStatus.EXCLUDED
            result.exclusion_reason = ExclusionReason.NAN_VALUE
            return result

        best_ref = None
        best_delta = self.config.tolerance_sec + 1

        for ref in references:
            if ref.timestamp is None:
                continue
            delta = abs(ref.timestamp - estimate.timestamp)
            if delta < best_delta:
                best_delta = delta
                best_ref = ref

        if best_ref is None:
            result.status = ValidationStatus.EXCLUDED
            result.exclusion_reason = ExclusionReason.REFERENCE_MISSING
            result.exclusion_detail = f"No reference within {self.config.tolerance_sec}s"
            return result

        result.status = ValidationStatus.VALID
        result.reference = best_ref.hr
        result.reference_timestamp = best_ref.timestamp
        result.sync_delta_sec = best_delta
        result.pairing_tolerance_sec = self.config.tolerance_sec
        result.error = estimate.hr - best_ref.hr
        result.abs_error = abs(result.error)
        return result

    def align_rr(
        self,
        estimates: List[RRRecord],
        references: List[RRRecord],
    ) -> List[ValidationResult]:
        """Align RR estimates with reference measurements."""
        results = []
        for est in estimates:
            result = ValidationResult(status=ValidationStatus.PENDING, modality=est.modality)
            if est.timestamp is None:
                result.status = ValidationStatus.EXCLUDED
                result.exclusion_reason = ExclusionReason.MISSING_TIMESTAMP
                results.append(result)
                continue

            best_ref = None
            best_delta = self.config.tolerance_sec + 1
            for ref in references:
                if ref.timestamp is None:
                    continue
                delta = abs(ref.timestamp - est.timestamp)
                if delta < best_delta:
                    best_delta = delta
                    best_ref = ref

            if best_ref is None:
                result.status = ValidationStatus.EXCLUDED
                result.exclusion_reason = ExclusionReason.REFERENCE_MISSING
            else:
                result.status = ValidationStatus.VALID
                result.estimate = est.rr
                result.reference = best_ref.rr
                result.estimate_timestamp = est.timestamp
                result.reference_timestamp = best_ref.timestamp
                result.sync_delta_sec = best_delta
                result.error = est.rr - best_ref.rr
                result.abs_error = abs(result.error)
            results.append(result)
        return results


def align_observations(
    est_timestamps: List[float],
    est_values: List[float],
    ref_timestamps: List[float],
    ref_values: List[float],
    tolerance: float = 2.0,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """Align two observation series by timestamp."""
    if len(est_timestamps) == 0 or len(ref_timestamps) == 0:
        return np.array([]), np.array([]), {
            "n_matched": 0,
            "n_unmatched_est": len(est_timestamps),
            "n_unmatched_ref": len(ref_timestamps),
            "tolerance": tolerance,
        }

    aligned_est = []
    aligned_ref = []
    used_ref = set()

    for i, (ts, val) in enumerate(zip(est_timestamps, est_values)):
        best_j = -1
        best_delta = tolerance + 1
        for j in range(len(ref_timestamps)):
            if j in used_ref:
                continue
            delta = abs(ref_timestamps[j] - ts)
            if delta < best_delta:
                best_delta = delta
                best_j = j
        if best_j >= 0:
            aligned_est.append(val)
            aligned_ref.append(ref_values[best_j])
            used_ref.add(best_j)

    diagnostics = {
        "n_matched": len(aligned_est),
        "n_unmatched_est": len(est_timestamps) - len(aligned_est),
        "n_unmatched_ref": len(ref_timestamps) - len(used_ref),
        "tolerance": tolerance,
    }
    return np.array(aligned_est), np.array(aligned_ref), diagnostics
