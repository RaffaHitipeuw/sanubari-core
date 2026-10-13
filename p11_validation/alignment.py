"""
Phase 11: Alignment and Pairing

Explicit pairing policies for aligning camera estimates with reference measurements.
"""

import numpy as np
from enum import Enum
from typing import List, Tuple, Dict, Any, Optional, Callable

from .base import ValidationResult, ValidationStatus, ExclusionReason


class PairingPolicy(Enum):
    """Pairing policies for alignment."""
    NEAREST = "nearest"  # Match to nearest reference
    FIRST_WITHIN_TOLERANCE = "first_within_tolerance"  # Match to first within tolerance
    MEAN_WITHIN_WINDOW = "mean_within_window"  # Average all references within window
    STRICT_TOLERANCE = "strict_tolerance"  # Only accept if within tolerance


def align_modalities(
    estimate_timestamps: List[float],
    estimate_values: List[float],
    ref_timestamps: List[float],
    ref_values: List[float],
    tolerance: float,
    policy: PairingPolicy = PairingPolicy.NEAREST,
) -> Tuple[(List[Optional[float]], List[Optional[float]], Dict[str, Any])]:
    """
    Align two modality series with specified pairing policy.

    Args:
        estimate_timestamps: Timestamps of camera estimates
        estimate_values: Camera estimate values
        ref_timestamps: Reference timestamps
        ref_values: Reference values
        tolerance: Maximum time difference for valid pairing (seconds)
        policy: Pairing policy to use

    Returns:
        Tuple of (aligned_estimates, aligned_references, diagnostics)
    """
    if len(estimate_timestamps) == 0 or len(ref_timestamps) == 0:
        return [], [], {
            "n_matched": 0,
            "n_unmatched_est": len(estimate_timestamps),
            "n_unmatched_ref": len(ref_timestamps),
        }

    if policy == PairingPolicy.NEAREST:
        return _align_nearest(
            estimate_timestamps, estimate_values,
            ref_timestamps, ref_values, tolerance
        )
    elif policy == PairingPolicy.FIRST_WITHIN_TOLERANCE:
        return _align_first_within(
            estimate_timestamps, estimate_values,
            ref_timestamps, ref_values, tolerance
        )
    elif policy == PairingPolicy.MEAN_WITHIN_WINDOW:
        return _align_mean_window(
            estimate_timestamps, estimate_values,
            ref_timestamps, ref_values, tolerance
        )
    elif policy == PairingPolicy.STRICT_TOLERANCE:
        return _align_strict(
            estimate_timestamps, estimate_values,
            ref_timestamps, ref_values, tolerance
        )
    else:
        raise ValueError(f"Unknown pairing policy: {policy}")


def _align_nearest(
    est_ts: List[float],
    est_vals: List[float],
    ref_ts: List[float],
    ref_vals: List[float],
    tolerance: float,
) -> Tuple[(List[Optional[float]], List[Optional[float]], Dict[str, Any])]:
    """Align using nearest reference within tolerance."""
    aligned_est = []
    aligned_ref = []
    used_ref = set()

    for i, (ts, val) in enumerate(zip(est_ts, est_vals)):
        best_j = -1
        best_delta = tolerance + 1

        for j in range(len(ref_ts)):
            if j in used_ref:
                continue
            delta = abs(ref_ts[j] - ts)
            if delta < best_delta:
                best_delta = delta
                best_j = j

        if best_j >= 0:
            aligned_est.append(val)
            aligned_ref.append(ref_vals[best_j])
            used_ref.add(best_j)
        else:
            aligned_est.append(None)
            aligned_ref.append(None)

    return aligned_est, aligned_ref, {
        "n_matched": len([v for v in aligned_est if v is not None]),
        "n_unmatched_est": len([v for v in aligned_est if v is None]),
        "n_unmatched_ref": len(ref_ts) - len(used_ref),
        "policy": "nearest",
    }


def _align_first_within(
    est_ts: List[float],
    est_vals: List[float],
    ref_ts: List[float],
    ref_vals: List[float],
    tolerance: float,
) -> Tuple[(List[Optional[float]], List[Optional[float]], Dict[str, Any])]:
    """Align using first reference within tolerance."""
    aligned_est = []
    aligned_ref = []
    used_ref = set()

    for ts, val in zip(est_ts, est_vals):
        matched = False
        for j in range(len(ref_ts)):
            if j in used_ref:
                continue
            if abs(ref_ts[j] - ts) <= tolerance:
                aligned_est.append(val)
                aligned_ref.append(ref_vals[j])
                used_ref.add(j)
                matched = True
                break

        if not matched:
            aligned_est.append(None)
            aligned_ref.append(None)

    return aligned_est, aligned_ref, {
        "n_matched": len([v for v in aligned_est if v is not None]),
        "n_unmatched_est": len([v for v in aligned_est if v is None]),
        "n_unmatched_ref": len(ref_ts) - len(used_ref),
        "policy": "first_within_tolerance",
    }


def _align_mean_window(
    est_ts: List[float],
    est_vals: List[float],
    ref_ts: List[float],
    ref_vals: List[float],
    tolerance: float,
) -> Tuple[(List[Optional[float]], List[Optional[float]], Dict[str, Any])]:
    """Align using mean of references within tolerance window."""
    aligned_est = []
    aligned_ref = []
    used_ref_global = set()

    for ts, val in zip(est_ts, est_vals):
        window_refs = []
        window_inds = []

        for j in range(len(ref_ts)):
            if j in used_ref_global:
                continue
            if abs(ref_ts[j] - ts) <= tolerance:
                window_refs.append(ref_vals[j])
                window_inds.append(j)

        if window_refs:
            aligned_est.append(val)
            aligned_ref.append(float(np.mean(window_refs)))
            for j in window_inds:
                used_ref_global.add(j)
        else:
            aligned_est.append(None)
            aligned_ref.append(None)

    return aligned_est, aligned_ref, {
        "n_matched": len([v for v in aligned_est if v is not None]),
        "n_unmatched_est": len([v for v in aligned_est if v is None]),
        "n_unmatched_ref": len(ref_ts) - len(used_ref_global),
        "policy": "mean_within_window",
    }


def _align_strict(
    est_ts: List[float],
    est_vals: List[float],
    ref_ts: List[float],
    ref_vals: List[float],
    tolerance: float,
) -> Tuple[(List[Optional[float]], List[Optional[float]], Dict[str, Any])]:
    """Align only if within strict tolerance."""
    aligned_est = []
    aligned_ref = []

    for ts, val in zip(est_ts, est_vals):
        deltas = [abs(rt - ts) for rt in ref_ts]
        min_delta = min(deltas)
        min_idx = deltas.index(min_delta)

        if min_delta <= tolerance:
            aligned_est.append(val)
            aligned_ref.append(ref_vals[min_idx])
        else:
            aligned_est.append(None)
            aligned_ref.append(None)

    return aligned_est, aligned_ref, {
        "n_matched": len([v for v in aligned_est if v is not None]),
        "n_unmatched_est": len([v for v in aligned_est if v is None]),
        "n_unmatched_ref": len(ref_ts),
        "policy": "strict_tolerance",
    }


def find_nearest_match(
    query_ts: float,
    reference_timestamps: List[float],
    tolerance: float,
) -> Tuple[Optional[int], Optional[float], float]:
    """
    Find nearest reference match for a query timestamp.

    Args:
        query_ts: Query timestamp
        reference_timestamps: Available reference timestamps
        tolerance: Maximum allowed time difference

    Returns:
        Tuple of (reference_index, reference_timestamp, delta) or (None, None, inf)
    """
    if len(reference_timestamps) == 0:
        return None, None, float('inf')

    deltas = [abs(ts - query_ts) for ts in reference_timestamps]
    min_delta = min(deltas)
    min_idx = deltas.index(min_delta)

    if min_delta <= tolerance:
        return min_idx, reference_timestamps[min_idx], min_delta
    return None, None, min_delta


def validate_pairing(
    paired_est: List[float],
    paired_ref: List[float],
    min_pairs: int = 5,
    error_threshold: Optional[float] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate that pairing produced valid results.

    Args:
        paired_est: Paired estimates
        paired_ref: Paired references
        min_pairs: Minimum required pairs
        error_threshold: Optional max allowed error

    Returns:
        Tuple of (is_valid, diagnostics)
    """
    valid_pairs = [
        (e, r) for e, r in zip(paired_est, paired_ref)
        if e is not None and r is not None
    ]

    diagnostics = {
        "n_valid_pairs": len(valid_pairs),
        "sufficient_pairs": len(valid_pairs) >= min_pairs,
    }

    if error_threshold is not None and valid_pairs:
        errors = [e - r for e, r in valid_pairs]
        max_error = max(abs(err) for err in errors)
        diagnostics["max_error"] = max_error
        diagnostics["within_threshold"] = max_error <= error_threshold

    return diagnostics["sufficient_pairs"], diagnostics


def compute_alignment_diagnostics(
    est_timestamps: List[float],
    ref_timestamps: List[float],
    tolerance: float,
) -> Dict[str, Any]:
    """
    Compute diagnostics for an alignment operation.

    Args:
        est_timestamps: Estimate timestamps
        ref_timestamps: Reference timestamps
        tolerance: Pairing tolerance

    Returns:
        Dict with alignment diagnostics
    """
    diagnostics = {
        "n_estimates": len(est_timestamps),
        "n_references": len(ref_timestamps),
        "tolerance": tolerance,
    }

    if len(est_timestamps) == 0 or len(ref_timestamps) == 0:
        diagnostics.update({
            "min_timestamp_diff": float('inf'),
            "max_timestamp_diff": float('inf'),
            "mean_timestamp_diff": float('inf'),
            "coverage_fraction": 0.0,
        })
        return diagnostics

    # Compute all pairwise deltas
    all_deltas = []
    for ts in est_timestamps:
        for rts in ref_timestamps:
            all_deltas.append(abs(ts - rts))

    if not all_deltas:
        diagnostics.update({
            "min_timestamp_diff": float('inf'),
            "max_timestamp_diff": float('inf'),
            "mean_timestamp_diff": float('inf'),
            "coverage_fraction": 0.0,
        })
        return diagnostics

    diagnostics.update({
        "min_timestamp_diff": float(np.min(all_deltas)),
        "max_timestamp_diff": float(np.max(all_deltas)),
        "mean_timestamp_diff": float(np.mean(all_deltas)),
        "coverage_fraction": float(np.mean([d <= tolerance for d in all_deltas])),
    })

    return diagnostics
