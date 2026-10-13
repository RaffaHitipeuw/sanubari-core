"""
Phase 11: Multi-Sensor Validation Pipeline

Validation framework for comparing Sanubari rPPG outputs with synchronized
reference measurements from independent sensors.

Supports:
    - Heart rate (HR) validation
    - Respiratory rate (RR) validation
    - Heart rate variability (HRV) metrics validation
    - Explicit timestamp-based synchronization
    - Configurable pairing tolerance
    - Failure and exclusion accounting
    - Session/subject separation

Note: This module provides infrastructure for validation. Actual sensor
validation requires real synchronized data with known ground truth.
Synthetic fixtures are provided for software testing only.
"""

__version__ = "1.0.0"

from .base import (
    # Enums
    Modality,
    HRVMetricType,
    ValidationStatus,
    ExclusionReason,
    # Data classes
    TimestampRecord,
    HRRecord,
    RRRecord,
    HRVRecord,
    IBIRecord,
    ValidationResult,
    SyncConfig,
    ValidationConfig,
    # Helpers
    create_hr_record,
    create_rr_record,
    create_hrv_record,
    create_ibi_record,
    validate_hr_value,
    validate_rr_value,
    validate_ibi_value,
)

from .sync import (
    Synchronizer,
    align_observations,
    compute_time_delta,
    detect_clock_drift,
    validate_timestamp_sequence,
)

from .metrics import (
    # HR metrics
    compute_hr_metrics,
    compute_bland_altman,
    compute_mae_rmse,
    # RR metrics
    compute_rr_metrics,
    # HRV metrics
    compute_hrv_metrics,
    compute_sdnn,
    compute_rmssd,
    compute_pnn50,
    # Aggregation
    aggregate_validation_results,
    group_results_by_condition,
)

from .alignment import (
    PairingPolicy,
    align_modalities,
    find_nearest_match,
    validate_pairing,
    compute_alignment_diagnostics,
)

from .failure import (
    ExclusionTracker,
    record_exclusion,
    get_exclusion_summary,
    track_missing_data,
    track_sync_failure,
    track_quality_failure,
)

from .io import (
    ValidationDataset,
    load_validation_dataset,
    save_validation_results,
    export_results_csv,
    import_reference_csv,
    create_synthetic_fixture,
    validate_dataset,
    ValidationLoadError,
    ValidationExportError,
)

from .pipeline import (
    ValidationPipeline,
    run_hr_validation,
    run_rr_validation,
    run_hrv_validation,
    run_full_validation,
    generate_validation_report,
)

from .rppg10_adapter import (
    rPPG10Config,
    rPPG10Session,
    RecordingFileSet,
    FileStatus,
    DatasetReadinessReport,
    discover_subjects,
    discover_recording,
    discover_all,
    load_session,
    process_ecg_session,
    session_to_validation_dataset,
    check_readiness,
    load_ecg,
    detect_r_peaks,
    ecg_to_hr,
    ecg_to_ibi,
)

__all__ = [
    "__version__",
    # Enums
    "Modality",
    "HRVMetricType",
    "ValidationStatus",
    "ExclusionReason",
    # Base
    "TimestampRecord",
    "HRRecord",
    "RRRecord",
    "HRVRecord",
    "IBIRecord",
    "ValidationResult",
    "SyncConfig",
    "ValidationConfig",
    "create_hr_record",
    "create_rr_record",
    "create_hrv_record",
    "create_ibi_record",
    "validate_hr_value",
    "validate_rr_value",
    "validate_ibi_value",
    # Sync
    "Synchronizer",
    "align_observations",
    "compute_time_delta",
    "detect_clock_drift",
    "validate_timestamp_sequence",
    # Metrics
    "compute_hr_metrics",
    "compute_bland_altman",
    "compute_mae_rmse",
    "compute_rr_metrics",
    "compute_hrv_metrics",
    "compute_sdnn",
    "compute_rmssd",
    "compute_pnn50",
    "aggregate_validation_results",
    "group_results_by_condition",
    # Alignment
    "PairingPolicy",
    "align_modalities",
    "find_nearest_match",
    "validate_pairing",
    "compute_alignment_diagnostics",
    # Failure
    "ExclusionTracker",
    "record_exclusion",
    "get_exclusion_summary",
    "track_missing_data",
    "track_sync_failure",
    "track_quality_failure",
    # IO
    "ValidationDataset",
    "load_validation_dataset",
    "save_validation_results",
    "export_results_csv",
    "import_reference_csv",
    "create_synthetic_fixture",
    "validate_dataset",
    "ValidationLoadError",
    "ValidationExportError",
    # Pipeline
    "ValidationPipeline",
    "run_hr_validation",
    "run_rr_validation",
    "run_hrv_validation",
    "run_full_validation",
    "generate_validation_report",
]
