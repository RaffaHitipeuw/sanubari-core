"""
Phase 9.0 — RPPG Signal Validation (DIAGNOSTIC ONLY)

Offline analysis toolkit that answers one question:

    Is a low regularity / low SQI reading caused by
      (A) a genuinely poor optical pulse signal,
      (B) a failure of the peak detector,
      (C) a preprocessing / ROI artifact,
      (D) something that cannot be decided without a reference sensor?

This package NEVER touches production behaviour. It imports production
functions (rppg_core / rppg_sqi / rppg_config) so the numbers it reports are
the numbers the live pipeline produces, but it re-implements only the
*observation* layer (signal extraction, peak timestamps, metrics) which the
production code does not expose.

Modules
-------
pipeline.py    Offline per-ROI signal extraction + production-identical
                preprocessing and detection.
metrics.py      IBI distribution, ACF periodicity, peak-vs-truth matching.
synthetic.py    Controlled synthetic signals with known ground truth.
reference.py    ECG / reference-sensor comparison helpers.
report.py       A/B/C/D classification and markdown rendering.

Typical use
------------
    from signal_validation import analyze_video_rois, render_report

    records = analyze_video_rois(
        video_path="Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi",
        roi_name="forehead",
        fps=30.0,
    )
    print(render_report(records))
"""

__version__ = "1.0.0"

from .metrics import (
    IBIStats,
    PeakMatch,
    acf_periodicity,
    ibi_stats,
    match_peaks,
    match_peaks_with_latency,
)
from .pipeline import (
    ROIAnalysis,
    analyze_roi_series,
    analyze_session_csv,
    analyze_video_rois,
    export_roi_signals,
    preprocess_like_production,
)
from .synthetic import (
    SYNTHETIC_CASES,
    SyntheticCase,
    build_case,
)
from .reference import (
    ECGCondition,
    compare_beats,
    compare_hr_traces,
    load_ecg_reference,
)
from .report import classify_roi, render_report

__all__ = [
    "IBIStats",
    "PeakMatch",
    "acf_periodicity",
    "ibi_stats",
    "match_peaks",
    "match_peaks_with_latency",
    "ROIAnalysis",
    "analyze_roi_series",
    "analyze_session_csv",
    "analyze_video_rois",
    "export_roi_signals",
    "preprocess_like_production",
    "SYNTHETIC_CASES",
    "SyntheticCase",
    "build_case",
    "ECGCondition",
    "compare_beats",
    "compare_hr_traces",
    "load_ecg_reference",
    "classify_roi",
    "render_report",
]
