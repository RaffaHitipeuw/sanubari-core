"""
Phase 11: Validation Pipeline

High-level validation workflow combining sync, metrics, and reporting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import numpy as np

from .base import (
    ValidationConfig,
    SyncConfig,
    ValidationResult,
    ValidationStatus,
    HRRecord,
    RRRecord,
)
from .sync import Synchronizer
from .metrics import (
    compute_hr_metrics,
    compute_rr_metrics,
    compute_hrv_metrics,
    compute_bland_altman,
    aggregate_validation_results,
    group_results_by_condition,
)
from .failure import ExclusionTracker
from .alignment import align_modalities, PairingPolicy


# ---------------------------------------------------------------------------
# ValidationPipeline class
# ---------------------------------------------------------------------------

@dataclass
class ValidationPipeline:
    """
    High-level validation pipeline.

    Combines synchronization, pairing, metrics, and failure tracking
    into a single workflow.
    """

    config: ValidationConfig = field(default_factory=ValidationConfig)

    # Internal state
    _synchronizer: Optional[Synchronizer] = None
    _exclusion_tracker: ExclusionTracker = field(default_factory=ExclusionTracker)
    _results: Dict[str, List[ValidationResult]] = field(default_factory=dict)

    def __post_init__(self):
        sync_cfg = self.config.sync if isinstance(self.config, ValidationConfig) else self.config
        self._synchronizer = Synchronizer(sync_cfg)

    def _hr_range(self) -> tuple:
        return getattr(self.config, "hr_range", (40.0, 200.0))

    def _rr_range(self) -> tuple:
        return getattr(self.config, "rr_range", (6.0, 40.0))

    def run_hr_validation(
        self,
        camera_estimates: List[HRRecord],
        reference: List[HRRecord],
    ) -> Dict[str, Any]:
        """
        Run HR validation workflow.

        Args:
            camera_estimates: Camera-derived HR records
            reference: Reference HR records

        Returns:
            Dict with validation results, metrics, and Bland-Altman analysis
        """
        # Align estimates with references
        results = self._synchronizer.align(camera_estimates, reference)

        # Track exclusions
        for result in results:
            if result.status != ValidationStatus.VALID:
                self._exclusion_tracker.record(
                    reason=result.exclusion_reason or "unknown",
                    timestamp=result.estimate_timestamp or 0,
                    detail=result.exclusion_detail,
                )

        # Compute metrics from ValidationResult list
        metrics = compute_hr_metrics(results, self._hr_range())

        # Bland-Altman on the valid pairs
        valid_pairs = [
            (r.estimate, r.reference)
            for r in results
            if r.status == ValidationStatus.VALID
            and r.estimate is not None
            and r.reference is not None
        ]
        bland_altman = {}
        if len(valid_pairs) >= 3:
            est_arr = np.array([p[0] for p in valid_pairs])
            ref_arr = np.array([p[1] for p in valid_pairs])
            bland_altman = compute_bland_altman(est_arr, ref_arr)

        # Store
        self._results["hr"] = results

        return {
            "metrics": metrics,
            "bland_altman": bland_altman,
            "n_results": len(results),
            "exclusions": self._exclusion_tracker.get_summary(),
        }

    def run_rr_validation(
        self,
        camera_estimates: List[RRRecord],
        reference: List[RRRecord],
    ) -> Dict[str, Any]:
        """
        Run RR validation workflow.

        Args:
            camera_estimates: Camera-derived RR records
            reference: Reference RR records

        Returns:
            Dict with validation results and metrics
        """
        results = self._synchronizer.align_rr(camera_estimates, reference)

        for result in results:
            if result.status != ValidationStatus.VALID:
                self._exclusion_tracker.record(
                    reason=result.exclusion_reason or "unknown",
                    timestamp=result.estimate_timestamp or 0,
                    detail=result.exclusion_detail,
                )

        metrics = compute_rr_metrics(results, self._rr_range())

        self._results["rr"] = results

        return {
            "metrics": metrics,
            "n_results": len(results),
            "exclusions": self._exclusion_tracker.get_summary(),
        }

    def get_exclusion_report(self) -> str:
        """Get human-readable exclusion report."""
        summary = self._exclusion_tracker.get_summary()

        lines = [
            "Validation Exclusion Report",
            "=" * 50,
            f"Total: {summary['total_recorded']}",
            f"Excluded: {summary['total_excluded']}",
            f"Rate: {summary['exclusion_rate']:.1%}",
            "",
            "By Reason:",
            "-" * 30,
        ]

        for reason, count in sorted(summary['counts'].items(), key=lambda x: -x[1]):
            lines.append(f"  {reason}: {count}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Standalone array-based validation functions
# ---------------------------------------------------------------------------

def run_hr_validation(
    estimates: np.ndarray,
    estimate_timestamps: np.ndarray,
    references: np.ndarray,
    reference_timestamps: np.ndarray,
    tolerance: float = 2.0,
    hr_range: tuple = (40.0, 200.0),
    sqi_values: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """
    Run HR validation on arrays.

    Aligns camera HR estimates with reference measurements, filters by range,
    computes MAE/RMSE/bias/std-error, and produces Bland-Altman analysis.

    Args:
        estimates: Camera HR estimates (BPM)
        estimate_timestamps: Timestamps for estimates (seconds from session start)
        references: Reference HR values (BPM)
        reference_timestamps: Timestamps for references
        tolerance: Maximum time difference for pairing (seconds)
        hr_range: Valid HR range as (min, max) in BPM
        sqi_values: Optional SQI values per estimate (for reporting)

    Returns:
        Dict with n_pairs, mae, rmse, bias, std_error, bland_altman,
        alignment_diagnostics. Returns an 'error' key if pairing fails.
    """
    # Align
    aligned_est, aligned_ref, diag = align_modalities(
        estimate_timestamps.tolist(),
        estimates.tolist(),
        reference_timestamps.tolist(),
        references.tolist(),
        tolerance=tolerance,
        policy=PairingPolicy.NEAREST,
    )

    # Filter valid (matched) pairs
    valid_est = [v for v in aligned_est if v is not None]
    valid_ref = [v for v in aligned_ref if v is not None]

    if len(valid_est) < 5:
        return {
            "error": "insufficient_pairs",
            "n_pairs": len(valid_est),
            "n_estimate": len(estimates),
            "n_reference": len(references),
        }

    est_arr = np.array(valid_est)
    ref_arr = np.array(valid_ref)

    # Filter by physiological range
    mask = (
        (est_arr >= hr_range[0]) &
        (est_arr <= hr_range[1]) &
        (ref_arr >= hr_range[0]) &
        (ref_arr <= hr_range[1])
    )
    est_arr = est_arr[mask]
    ref_arr = ref_arr[mask]

    if len(est_arr) < 3:
        return {
            "error": "insufficient_valid_pairs",
            "n_pairs": len(est_arr),
            "alignment_diagnostics": diag,
        }

    errors    = est_arr - ref_arr
    abs_errors = np.abs(errors)

    result = {
        "n_pairs": int(len(est_arr)),
        "mae":        float(np.mean(abs_errors)),
        "rmse":       float(np.sqrt(np.mean(np.power(errors, 2.0)))),
        "bias":       float(np.mean(errors)),
        "std_error":  float(np.std(errors, ddof=1)),
        "alignment_diagnostics": diag,
    }

    # Bland-Altman analysis
    ba = compute_bland_altman(est_arr, ref_arr)
    result["bland_altman"] = ba

    return result


def run_rr_validation(
    estimates: np.ndarray,
    estimate_timestamps: np.ndarray,
    references: np.ndarray,
    reference_timestamps: np.ndarray,
    tolerance: float = 2.0,
    rr_range: tuple = (6.0, 40.0),
) -> Dict[str, Any]:
    """
    Run RR validation on arrays.

    Aligns camera RR estimates with reference measurements, filters by range,
    and computes MAE/RMSE/bias.

    Args:
        estimates: Camera RR estimates (BRPM)
        estimate_timestamps: Timestamps for estimates
        references: Reference RR values (BRPM)
        reference_timestamps: Timestamps for references
        tolerance: Maximum time difference for pairing (seconds)
        rr_range: Valid RR range as (min, max) in BRPM

    Returns:
        Dict with n_pairs, mae, rmse, bias, alignment_diagnostics.
    """
    aligned_est, aligned_ref, diag = align_modalities(
        estimate_timestamps.tolist(),
        estimates.tolist(),
        reference_timestamps.tolist(),
        references.tolist(),
        tolerance=tolerance,
        policy=PairingPolicy.NEAREST,
    )

    valid_est = [v for v in aligned_est if v is not None]
    valid_ref = [v for v in aligned_ref if v is not None]

    if len(valid_est) < 3:
        return {
            "error": "insufficient_pairs",
            "n_pairs": len(valid_est),
        }

    est_arr = np.array(valid_est)
    ref_arr = np.array(valid_ref)

    # Range filter
    mask = (
        (est_arr >= rr_range[0]) &
        (est_arr <= rr_range[1]) &
        (ref_arr >= rr_range[0]) &
        (ref_arr <= rr_range[1])
    )
    est_arr = est_arr[mask]
    ref_arr = ref_arr[mask]

    if len(est_arr) < 3:
        return {
            "error": "insufficient_valid_pairs",
            "n_pairs": len(est_arr),
            "alignment_diagnostics": diag,
        }

    errors = est_arr - ref_arr

    return {
        "n_pairs":           int(len(est_arr)),
        "mae":               float(np.mean(np.abs(errors))),
        "rmse":              float(np.sqrt(np.mean(np.power(errors, 2.0)))),
        "bias":              float(np.mean(errors)),
        "std_error":         float(np.std(errors, ddof=1)),
        "alignment_diagnostics": diag,
    }


def run_hrv_validation(
    ibi_estimates: np.ndarray,
    ibi_references: np.ndarray,
    min_ibi_count: int = 10,
) -> Dict[str, Any]:
    """
    Run HRV validation on IBI sequences.

    Computes SDNN, RMSSD, and pNN50 for both camera-derived and reference
    IBI sequences, and computes MAE/RMSE between matched pairs.

    Args:
        ibi_estimates: Camera-derived IBI values in ms
        ibi_references: Reference IBI values in ms
        min_ibi_count: Minimum valid IBI count for 'valid' flag

    Returns:
        Dict with 'valid', 'n_est', 'n_ref', 'sdnn_est', 'sdnn_ref',
        'rmssd_est', 'rmssd_ref', 'pnn50_est', 'pnn50_ref',
        'ibi_mae', 'ibi_rmse'.  All numeric fields are NaN when insufficient
        data is available.
    """
    # Delegate to the full compute_hrv_metrics
    result = compute_hrv_metrics(ibi_estimates, ibi_references, min_ibi_count)

    # Add pairwise IBI agreement metrics if both sequences have data
    est_ibi = np.asarray(ibi_estimates, dtype=np.float64)
    ref_ibi = np.asarray(ibi_references, dtype=np.float64)

    # Use the shorter length for pairwise comparison (aligned by index)
    n_compare = min(len(est_ibi), len(ref_ibi))
    if n_compare >= 3:
        e = est_ibi[:n_compare]
        r = ref_ibi[:n_compare]
        # IBI range filter (physiological)
        mask = (e >= 300.0) & (e <= 2000.0) & (r >= 300.0) & (r <= 2000.0)
        e = e[mask]
        r = r[mask]
        if len(e) >= 3:
            ibi_errors = e - r
            result["ibi_mae"]  = float(np.mean(np.abs(ibi_errors)))
            result["ibi_rmse"] = float(np.sqrt(np.mean(np.power(ibi_errors, 2.0))))
        else:
            result["ibi_mae"]  = float("nan")
            result["ibi_rmse"] = float("nan")
    else:
        result["ibi_mae"]  = float("nan")
        result["ibi_rmse"] = float("nan")

    return result


def run_full_validation(
    dataset,
    sync_config: Optional[SyncConfig] = None,
) -> Dict[str, Any]:
    """
    Run full validation on a ValidationDataset.

    Produces HR, RR, and HRV results from a ValidationDataset, including
    Bland-Altman analysis for HR and condition-grouped summaries.

    Args:
        dataset: ValidationDataset with camera and reference data
        sync_config: Optional synchronization config

    Returns:
        Dict with session metadata, HR/RR/HRV results, quality summaries,
        and condition-grouped results.
    """
    config = sync_config or SyncConfig()

    results: Dict[str, Any] = {
        "session_id":   dataset.session_id,
        "subject_id":   dataset.subject_id,
        "date":         dataset.recording_date,
    }

    # HR validation
    if dataset.camera_hr and dataset.ref_hr:
        hr_results = run_hr_validation(
            estimates=np.array(dataset.camera_hr),
            estimate_timestamps=np.array(dataset.camera_timestamps),
            references=np.array(dataset.ref_hr),
            reference_timestamps=np.array(dataset.ref_timestamps),
            tolerance=config.tolerance_sec,
        )
        results["hr"] = hr_results

    # RR validation
    if dataset.camera_rr and dataset.ref_rr:
        rr_results = run_rr_validation(
            estimates=np.array(dataset.camera_rr),
            estimate_timestamps=np.array(dataset.camera_timestamps),
            references=np.array(dataset.ref_rr),
            reference_timestamps=np.array(dataset.ref_timestamps),
            tolerance=config.tolerance_sec,
        )
        results["rr"] = rr_results

    # HRV validation (requires IBI sequences)
    if hasattr(dataset, 'camera_ibi') and dataset.camera_ibi and \
       hasattr(dataset, 'ref_ibi') and dataset.ref_ibi:
        hrv_results = run_hrv_validation(
            ibi_estimates=np.array(dataset.camera_ibi),
            ibi_references=np.array(dataset.ref_ibi),
        )
        results["hrv"] = hrv_results

    # Quality summaries
    if dataset.camera_hr_sqi:
        sqi_arr = np.array(dataset.camera_hr_sqi)
        results["sqi_summary"] = {
            "mean": float(np.mean(sqi_arr)),
            "min":  float(np.min(sqi_arr)),
            "max":  float(np.max(sqi_arr)),
            "n":    len(sqi_arr),
        }

    if dataset.camera_motion_rejected:
        motion_arr = np.array(dataset.camera_motion_rejected)
        results["motion_summary"] = {
            "rejected_rate": float(np.mean(motion_arr)),
            "n_total":       len(motion_arr),
        }

    return results


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_validation_report(
    results: Dict[str, Any],
    format: str = "markdown",
) -> str:
    """
    Generate a human-readable validation report.

    Args:
        results: Output from run_full_validation or run_hr_validation
        format: 'markdown' or 'plain'

    Returns:
        Formatted report string
    """
    if format not in ("markdown", "plain"):
        raise ValueError(f"Unsupported format: {format}")
    sep = "=" * 60 if format == "plain" else "---\n"

    lines = []
    if format == "markdown":
        lines.append("# Validation Report\n")

    # Session info
    if "session_id" in results:
        lines.append(f"**Session:** {results['session_id']}")
    if "subject_id" in results:
        lines.append(f"**Subject:** {results['subject_id']}")
    if "date" in results:
        lines.append(f"**Date:** {results['date']}")
    if format == "markdown":
        lines.append("")

    # HR results
    if "hr" in results:
        hr = results["hr"]
        if format == "markdown":
            lines.append("## Heart Rate Validation\n")
        else:
            lines.append("HEART RATE VALIDATION")

        if "error" in hr:
            lines.append(f"  Error: {hr['error']}")
        else:
            for key in ("n_pairs", "mae", "rmse", "bias", "std_error"):
                if key in hr:
                    val = hr[key]
                    lines.append(f"  {key}: {val:.4f}" if isinstance(val, float) else f"  {key}: {val}")

            ba = hr.get("bland_altman", {})
            if ba:
                if format == "markdown":
                    lines.append("\n**Bland-Altman**\n")
                else:
                    lines.append("  Bland-Altman:")
                for key in ("mean_diff", "std_diff", "loa_upper", "loa_lower", "n"):
                    if key in ba:
                        val = ba[key]
                        lines.append(f"    {key}: {val:.4f}" if isinstance(val, float) else f"    {key}: {val}")

        if format == "markdown":
            lines.append("")

    # RR results
    if "rr" in results:
        rr = results["rr"]
        if format == "markdown":
            lines.append("## Respiratory Rate Validation\n")
        else:
            lines.append("RESPIRATORY RATE VALIDATION")

        if "error" in rr:
            lines.append(f"  Error: {rr['error']}")
        else:
            for key in ("n_pairs", "mae", "rmse", "bias", "std_error"):
                if key in rr:
                    val = rr[key]
                    lines.append(f"  {key}: {val:.4f}" if isinstance(val, float) else f"  {key}: {val}")
        if format == "markdown":
            lines.append("")

    # HRV results
    if "hrv" in results:
        hrv = results["hrv"]
        if format == "markdown":
            lines.append("## HRV Validation\n")
        else:
            lines.append("HRV VALIDATION")

        for key in ("valid", "n_est", "n_ref", "sdnn_est", "sdnn_ref",
                    "rmssd_est", "rmssd_ref", "pnn50_est", "pnn50_ref",
                    "ibi_mae", "ibi_rmse"):
            if key in hrv and hrv[key] is not None:
                val = hrv[key]
                if isinstance(val, bool):
                    lines.append(f"  {key}: {val}")
                else:
                    lines.append(f"  {key}: {val:.4f}" if isinstance(val, float) else f"  {key}: {val}")
        if format == "markdown":
            lines.append("")

    # Quality summaries
    if "sqi_summary" in results:
        sq = results["sqi_summary"]
        if format == "markdown":
            lines.append("## Signal Quality\n")
        else:
            lines.append("SIGNAL QUALITY")
        for key, val in sq.items():
            lines.append(f"  {key}: {val}")
        if format == "markdown":
            lines.append("")

    if "motion_summary" in results:
        ms = results["motion_summary"]
        if format == "markdown":
            lines.append("## Motion\n")
        else:
            lines.append("MOTION")
        for key, val in ms.items():
            lines.append(f"  {key}: {val}")
        if format == "markdown":
            lines.append("")

    return "\n".join(lines)
