"""
Phase 11 Metrics — Validation Error Metrics and HRV

Implements:
- MAE, RMSE, bias, error std for estimate/reference comparisons
- Bland–Altman analysis with limits of agreement
- HRV metrics (SDNN, RMSSD, pNN50) from inter-beat intervals
- Aggregation and grouping utilities
"""

import numpy as np
from typing import List, Dict, Any, Optional


# ---------------------------------------------------------------------------
# Core error metrics
# ---------------------------------------------------------------------------

def compute_mae_rmse(
    estimates,
    references,
) -> Dict[str, float]:
    """
    Compute MAE and RMSE between estimates and references.

    Args:
        estimates: Array-like of estimate values
        references: Array-like of reference values (same length as estimates)

    Returns:
        Dict with 'mae' and 'rmse' as floats.  Returns NaN if either input
        is empty or if lengths mismatch.
    """
    est = np.asarray(estimates)
    ref = np.asarray(references)
    if est.size == 0 or ref.size == 0 or est.shape != ref.shape:
        return {"mae": float("nan"), "rmse": float("nan")}
    errors = est - ref
    mae  = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(np.power(errors, 2.0))))
    return {"mae": mae, "rmse": rmse}


def compute_bland_altman(
    estimates,
    references,
) -> Dict[str, Any]:
    """
    Bland–Altman analysis for method comparison.

    Computes mean difference (bias) and limits of agreement
    (mean ± 1.96 × SD) using the standard clinical convention.

    Args:
        estimates: Array-like of estimate values
        references: Array-like of reference values (same length as estimates)

    Returns:
        Dict with 'mean_diff', 'std_diff', 'loa_upper', 'loa_lower', 'n'.
        Returns NaN fields if fewer than 3 paired observations are available.
    """
    est = np.asarray(estimates)
    ref = np.asarray(references)
    n = est.size
    if n < 3 or est.shape != ref.shape:
        return {
            "mean_diff": float("nan"),
            "std_diff":  float("nan"),
            "loa_upper": float("nan"),
            "loa_lower": float("nan"),
            "n": 0,
        }
    diffs     = est - ref
    mean_diff = float(np.mean(diffs))
    std_diff  = float(np.std(diffs, ddof=1))   # sample SD (ddof=1)
    loa_upper = mean_diff + 1.96 * std_diff
    loa_lower = mean_diff - 1.96 * std_diff
    return {
        "mean_diff":  mean_diff,
        "std_diff":   std_diff,
        "loa_upper":  float(loa_upper),
        "loa_lower":  float(loa_lower),
        "n":          n,
    }


# ---------------------------------------------------------------------------
# HR validation metrics
# ---------------------------------------------------------------------------

def compute_hr_metrics(
    results: List[Any],
    hr_range: tuple = (40.0, 200.0),
) -> Dict[str, Any]:
    """
    Compute HR validation metrics from a list of ValidationResult objects.

    Args:
        results: List of ValidationResult instances (or dicts with the same fields)
        hr_range: Valid HR range as (min, max) in BPM

    Returns:
        Dict with n_total, n_valid, n_excluded, mae, rmse, bias, std_error.
        All numeric fields are NaN when insufficient data is available.
    """
    if not results:
        return _empty_hr_metrics()

    # Support both ValidationResult objects and plain dicts
    valid = []
    excluded = 0
    for r in results:
        status = r.status if hasattr(r, "status") else r.get("status", None)
        if status is None:
            excluded += 1
            continue
        if status.value == "valid":
            est = r.estimate if hasattr(r, "estimate") else r.get("estimate")
            ref = r.reference if hasattr(r, "reference") else r.get("reference")
            if est is None or ref is None:
                excluded += 1
                continue
            # Range filter
            if not (hr_range[0] <= est <= hr_range[1] and hr_range[0] <= ref <= hr_range[1]):
                excluded += 1
                continue
            valid.append((est, ref))
        else:
            excluded += 1

    n_total   = len(results)
    n_valid   = len(valid)
    n_excluded = excluded

    if n_valid == 0:
        d = _empty_hr_metrics()
        d["n_total"]    = n_total
        d["n_valid"]    = n_valid
        d["n_excluded"] = n_excluded
        return d

    est_arr = np.array([v[0] for v in valid])
    ref_arr = np.array([v[1] for v in valid])
    errors  = est_arr - ref_arr

    return {
        "n_total":     n_total,
        "n_valid":     n_valid,
        "n_excluded":  n_excluded,
        "mae":         float(np.mean(np.abs(errors))),
        "rmse":        float(np.sqrt(np.mean(np.power(errors, 2.0)))),
        "bias":        float(np.mean(errors)),
        "std_error":   float(np.std(errors, ddof=1)),
    }


def _empty_hr_metrics() -> Dict[str, float]:
    """Return a metrics dict with all numerics set to NaN."""
    return {
        "n_total":    0,
        "n_valid":    0,
        "n_excluded": 0,
        "mae":        float("nan"),
        "rmse":       float("nan"),
        "bias":       float("nan"),
        "std_error":  float("nan"),
    }


# ---------------------------------------------------------------------------
# RR validation metrics
# ---------------------------------------------------------------------------

def compute_rr_metrics(
    results: List[Any],
    rr_range: tuple = (6.0, 40.0),
) -> Dict[str, Any]:
    """
    Compute RR validation metrics from a list of ValidationResult objects.

    Args:
        results: List of ValidationResult instances (or dicts)
        rr_range: Valid RR range as (min, max) in BRPM

    Returns:
        Dict with n_total, n_valid, n_excluded, mae, rmse, bias.
    """
    if not results:
        return {"n_total": 0, "n_valid": 0, "n_excluded": 0,
                "mae": float("nan"), "rmse": float("nan"), "bias": float("nan")}

    valid = []
    excluded = 0
    for r in results:
        status = r.status if hasattr(r, "status") else r.get("status", None)
        if status is None:
            excluded += 1
            continue
        if status.value == "valid":
            est = r.estimate if hasattr(r, "estimate") else r.get("estimate")
            ref = r.reference if hasattr(r, "reference") else r.get("reference")
            if est is None or ref is None:
                excluded += 1
                continue
            if not (rr_range[0] <= est <= rr_range[1] and rr_range[0] <= ref <= rr_range[1]):
                excluded += 1
                continue
            valid.append((est, ref))
        else:
            excluded += 1

    n_total    = len(results)
    n_valid    = len(valid)
    n_excluded = excluded

    if n_valid == 0:
        d = {"n_total": n_total, "n_valid": n_valid, "n_excluded": n_excluded,
             "mae": float("nan"), "rmse": float("nan"), "bias": float("nan")}
        return d

    est_arr = np.array([v[0] for v in valid])
    ref_arr = np.array([v[1] for v in valid])
    errors  = est_arr - ref_arr

    return {
        "n_total":    n_total,
        "n_valid":    n_valid,
        "n_excluded": n_excluded,
        "mae":        float(np.mean(np.abs(errors))),
        "rmse":       float(np.sqrt(np.mean(np.power(errors, 2.0)))),
        "bias":       float(np.mean(errors)),
    }


# ---------------------------------------------------------------------------
# HRV metrics from inter-beat intervals
# ---------------------------------------------------------------------------

def compute_sdnn(ibi_ms: np.ndarray) -> Optional[float]:
    """
    Standard deviation of NN (normal-to-normal) inter-beat intervals.

    SDNN = sqrt( sum((IBI_i - mean)^2) / (n - 1) )
           units: milliseconds

    Args:
        ibi_ms: Array of IBI values in milliseconds

    Returns:
        SDNN in ms, or None if fewer than 2 valid intervals.
    """
    ibi = np.asarray(ibi_ms, dtype=np.float64)
    if ibi.size < 2:
        return None
    # Filter physiologically implausible values before computing
    ibi = ibi[(ibi >= 300.0) & (ibi <= 2000.0)]
    if ibi.size < 2:
        return None
    return float(np.std(ibi, ddof=1))


def compute_rmssd(ibi_ms: np.ndarray) -> Optional[float]:
    """
    Root mean square of successive differences of NN intervals.

    RMSSD = sqrt( mean( (IBI_{i+1} - IBI_i)^2 ) )
            units: milliseconds

    Args:
        ibi_ms: Array of IBI values in milliseconds

    Returns:
        RMSSD in ms, or None if fewer than 2 valid intervals.
    """
    ibi = np.asarray(ibi_ms, dtype=np.float64)
    if ibi.size < 2:
        return None
    ibi = ibi[(ibi >= 300.0) & (ibi <= 2000.0)]
    if ibi.size < 2:
        return None
    diffs = np.diff(ibi)
    return float(np.sqrt(np.mean(np.power(diffs, 2.0))))


def compute_pnn50(ibi_ms: np.ndarray) -> Optional[float]:
    """
    Percentage of successive NN intervals differing by more than 50 ms.

    pNN50 = 100 × ( count(|IBI_{i+1} - IBI_i| > 50) ) / (n - 1)
            units: percent

    The ≥50 ms threshold is used (borderline differences count).

    Args:
        ibi_ms: Array of IBI values in milliseconds

    Returns:
        pNN50 as a percentage (0–100), or None if fewer than 2 intervals.
    """
    ibi = np.asarray(ibi_ms, dtype=np.float64)
    if ibi.size < 2:
        return None
    ibi = ibi[(ibi >= 300.0) & (ibi <= 2000.0)]
    if ibi.size < 2:
        return None
    diffs = np.diff(ibi)
    count = int(np.sum(np.abs(diffs) > 50.0))   # >50, borderline counts
    return float(100.0 * count / len(diffs))


def compute_hrv_metrics(
    ibi_estimates: np.ndarray,
    ibi_references: np.ndarray,
    min_ibi_count: int = 10,
) -> Dict[str, Any]:
    """
    Compute HRV metrics from camera-derived and reference IBI sequences.

    Produces SDNN and RMSSD for both sequences and flags whether the number
    of valid intervals is sufficient for meaningful HRV analysis.

    Args:
        ibi_estimates:   Camera-derived IBI values in ms
        ibi_references:  Reference IBI values in ms
        min_ibi_count:   Minimum valid IBI count for 'valid' flag

    Returns:
        Dict with 'valid', 'n_est', 'n_ref', 'sdnn_est', 'sdnn_ref',
        'rmssd_est', 'rmssd_ref', 'pnn50_est', 'pnn50_ref'.
        'valid' is True only when both sequences have ≥ min_ibi_count
        valid intervals.  All numeric fields are NaN when insufficient data.
    """
    est_ibi = np.asarray(ibi_estimates, dtype=np.float64)
    ref_ibi = np.asarray(ibi_references, dtype=np.float64)

    def _filter(ibi):
        """Keep physiologically plausible intervals."""
        return ibi[(ibi >= 300.0) & (ibi <= 2000.0)]

    est_f = _filter(est_ibi)
    ref_f = _filter(ref_ibi)
    n_est = len(est_f)
    n_ref = len(ref_f)

    sufficient = n_est >= min_ibi_count and n_ref >= min_ibi_count

    def _sdnn(ibi):
        if ibi.size < 2:
            return float("nan")
        return float(np.std(ibi, ddof=1))

    def _rmssd(ibi):
        if ibi.size < 2:
            return float("nan")
        diffs = np.diff(ibi)
        return float(np.sqrt(np.mean(np.power(diffs, 2.0))))

    def _pnn50(ibi):
        if ibi.size < 2:
            return float("nan")
        diffs = np.diff(ibi)
        return float(100.0 * np.sum(np.abs(diffs) > 50.0) / len(diffs))

    return {
        "valid":     sufficient,
        "n_est":     n_est,
        "n_ref":     n_ref,
        "sdnn_est":  _sdnn(est_f),
        "sdnn_ref":  _sdnn(ref_f),
        "rmssd_est": _rmssd(est_f),
        "rmssd_ref": _rmssd(ref_f),
        "pnn50_est": _pnn50(est_f),
        "pnn50_ref": _pnn50(ref_f),
    }


# ---------------------------------------------------------------------------
# Aggregation utilities
# ---------------------------------------------------------------------------

def aggregate_validation_results(results: List[Any]) -> Dict[str, Any]:
    """
    Aggregate counts from a list of ValidationResult objects.

    Args:
        results: List of ValidationResult instances (or dicts)

    Returns:
        Dict with n_total, n_valid, n_excluded.
    """
    if not results:
        return {"n_total": 0, "n_valid": 0, "n_excluded": 0}
    n_total = len(results)
    n_valid = 0
    for r in results:
        status = r.status if hasattr(r, "status") else r.get("status", None)
        if status is not None and status.value == "valid":
            n_valid += 1
    return {
        "n_total":    n_total,
        "n_valid":    n_valid,
        "n_excluded": n_total - n_valid,
    }


def group_results_by_condition(
    results: List[Any],
    sqi_thresholds: List[float] = None,
) -> Dict[str, List]:
    """
    Group validation results by signal-quality band.

    Args:
        results: List of ValidationResult instances (or dicts)
        sqi_thresholds: Sorted list of SQI cutpoints, e.g. [0.3, 0.5, 0.8].
                       Default: [0.3, 0.5, 0.8].

    Returns:
        Dict mapping band labels to sub-lists of results.
        Labels: 'sqi_<0.3', 'sqi_0.3-0.5', 'sqi_0.5-0.8', 'sqi_>=0.8', 'sqi_unknown'.
    """
    if sqi_thresholds is None:
        sqi_thresholds = [0.3, 0.5, 0.8]

    bands = {
        f"sqi_<{sqi_thresholds[0]}":        [],
        f"sqi_{sqi_thresholds[0]}-{sqi_thresholds[1]}": [],
        f"sqi_{sqi_thresholds[1]}-{sqi_thresholds[2]}": [],
        f"sqi_>={sqi_thresholds[2]}":         [],
        "sqi_unknown":                        [],
    }

    for r in results:
        sqi = r.sqi if hasattr(r, "sqi") else r.get("sqi", None)
        if sqi is None:
            bands["sqi_unknown"].append(r)
        elif sqi < sqi_thresholds[0]:
            bands[f"sqi_<{sqi_thresholds[0]}"].append(r)
        elif sqi < sqi_thresholds[1]:
            bands[f"sqi_{sqi_thresholds[0]}-{sqi_thresholds[1]}"].append(r)
        elif sqi < sqi_thresholds[2]:
            bands[f"sqi_{sqi_thresholds[1]}-{sqi_thresholds[2]}"].append(r)
        else:
            bands[f"sqi_>={sqi_thresholds[2]}"].append(r)

    return bands
