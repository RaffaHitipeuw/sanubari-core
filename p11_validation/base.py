"""
Phase 11: Base Data Structures

Data contracts for multi-sensor validation.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import hashlib


class Modality(Enum):
    """Supported measurement modalities."""
    CAMERA = "camera"           # rPPG-derived measurement
    ECG = "ecg"               # Electrocardiogram
    PPG = "ppg"               # Photoplethysmography (reference)
    PULSE_OX = "pulse_ox"    # Pulse oximeter
    RESPIRATORY = "respiratory" # Respiratory effort sensor
    UNKNOWN = "unknown"


class HRVMetricType(Enum):
    """HRV metric types with compatibility info."""
    SDNN = "sdnn"           # Standard deviation of NN intervals
    RMSSD = "rmssd"         # Root mean square of successive differences
    pNN50 = "pnn50"        # Percentage of successive intervals > 50ms
    pNN20 = "pnn20"        # Percentage of successive intervals > 20ms
    HR = "hr"              # Heart rate from IBI
    HR_MAX = "hr_max"      # Maximum heart rate
    HR_MIN = "hr_min"      # Minimum heart rate


class ValidationStatus(Enum):
    """Validation result status."""
    VALID = "valid"
    INVALID = "invalid"
    INSUFFICIENT_DATA = "insufficient_data"
    SYNC_FAILED = "sync_failed"
    EXCLUDED = "excluded"
    PENDING = "pending"


class ExclusionReason(Enum):
    """Reasons for excluding measurements."""
    MISSING_TIMESTAMP = "missing_timestamp"
    INVALID_TIMESTAMP = "invalid_timestamp"
    OUT_OF_RANGE = "out_of_range"
    SYNC_TOLERANCE = "sync_tolerance_exceeded"
    QUALITY_BELOW_THRESHOLD = "quality_below_threshold"
    MOTION_REJECTED = "motion_rejected"
    LOW_SQI = "low_sqi"
    INSUFFICIENT_PAIRS = "insufficient_pairs"
    REFERENCE_MISSING = "reference_missing"
    ESTIMATE_MISSING = "estimate_missing"
    NAN_VALUE = "nan_value"
    INF_VALUE = "inf_value"
    MANUAL_EXCLUSION = "manual_exclusion"
    WINDOW_TOO_SHORT = "window_too_short"
    IBI_DETECTION_FAILED = "ibi_detection_failed"


@dataclass
class TimestampRecord:
    """Base record with timestamp."""
    timestamp: float = 0.0  # Seconds from session start
    modality: Modality = Modality.UNKNOWN
    source: str = ""  # e.g., "camera_forehead", "ecg_channel_1"
    session_id: str = ""
    subject_id: str = ""  # Pseudonymous


@dataclass
class HRRecord:
    """Heart rate measurement record."""
    timestamp: float = 0.0
    modality: Modality = Modality.CAMERA
    source: str = ""
    session_id: str = ""
    subject_id: str = ""
    hr: float = 0.0
    confidence: Optional[float] = None
    sqi: Optional[float] = None
    unit: str = "bpm"


@dataclass
class RRRecord:
    """Respiratory rate measurement record."""
    timestamp: float = 0.0
    modality: Modality = Modality.RESPIRATORY
    source: str = ""
    session_id: str = ""
    subject_id: str = ""
    rr: float = 0.0
    confidence: Optional[float] = None
    unit: str = "brpm"


@dataclass
class IBIRecord:
    """Inter-beat interval record."""
    timestamp: float = 0.0
    modality: Modality = Modality.ECG
    source: str = ""
    session_id: str = ""
    subject_id: str = ""
    ibi_ms: float = 0.0
    beat_type: str = "normal"


@dataclass
class HRVRecord:
    """HRV metric from IBI sequence."""
    timestamp: float = 0.0
    modality: Modality = Modality.UNKNOWN
    source: str = ""
    session_id: str = ""
    subject_id: str = ""
    metric_type: HRVMetricType = HRVMetricType.SDNN
    value: float = 0.0
    n_ibi: int = 0
    window_sec: Optional[float] = None
    unit: str = ""


@dataclass
class ValidationResult:
    """Result of comparing estimate against reference."""
    status: ValidationStatus = ValidationStatus.PENDING
    modality: Modality = Modality.UNKNOWN
    estimate: Optional[float] = None
    reference: Optional[float] = None
    estimate_timestamp: Optional[float] = None
    reference_timestamp: Optional[float] = None
    sync_delta_sec: Optional[float] = None
    pairing_tolerance_sec: float = 2.0
    sqi: Optional[float] = None
    confidence: Optional[float] = None
    motion_rejected: bool = False
    exclusion_reason: Optional[ExclusionReason] = None
    exclusion_detail: str = ""
    window_start: Optional[float] = None
    window_end: Optional[float] = None
    error: Optional[float] = None
    abs_error: Optional[float] = None


@dataclass
class SyncConfig:
    """Synchronization configuration."""
    tolerance_sec: float = 2.0
    use_drift_correction: bool = False
    drift_correction_window_sec: float = 60.0
    max_drift_rate_hz: float = 0.1


@dataclass
class ValidationConfig:
    """Full validation configuration."""
    sync: SyncConfig = field(default_factory=SyncConfig)
    hr_range: tuple = (40.0, 200.0)
    hr_tolerance_bpm: float = 5.0
    rr_range: tuple = (6.0, 40.0)
    min_ibi_count: int = 10
    ibi_range_ms: tuple = (300.0, 2000.0)
    min_sqi: float = 0.3
    min_confidence: float = 0.4
    report_grouped_by: List[str] = field(default_factory=lambda: ["sqi", "motion"])
    group_sqi_thresholds: List[float] = field(default_factory=lambda: [0.3, 0.5, 0.8])


def create_hr_record(
    timestamp: float,
    hr: float,
    modality: Modality = Modality.CAMERA,
    source: str = "",
    session_id: str = "",
    subject_id: str = "",
    confidence: Optional[float] = None,
    sqi: Optional[float] = None,
) -> HRRecord:
    """Create an HR record with validation."""
    return HRRecord(
        timestamp=timestamp,
        modality=modality,
        hr=hr,
        source=source,
        session_id=session_id,
        subject_id=subject_id,
        confidence=confidence,
        sqi=sqi,
    )


def create_rr_record(
    timestamp: float,
    rr: float,
    modality: Modality = Modality.RESPIRATORY,
    source: str = "",
    session_id: str = "",
    subject_id: str = "",
    confidence: Optional[float] = None,
) -> RRRecord:
    """Create an RR record with validation."""
    return RRRecord(
        timestamp=timestamp,
        modality=modality,
        rr=rr,
        source=source,
        session_id=session_id,
        subject_id=subject_id,
        confidence=confidence,
    )


def create_hrv_record(
    timestamp: float,
    metric_type: HRVMetricType,
    value: float,
    modality: Modality = Modality.ECG,
    source: str = "",
    session_id: str = "",
    subject_id: str = "",
    n_ibi: int = 0,
    window_sec: Optional[float] = None,
) -> HRVRecord:
    """Create an HRV record."""
    return HRVRecord(
        timestamp=timestamp,
        modality=modality,
        metric_type=metric_type,
        value=value,
        source=source,
        session_id=session_id,
        subject_id=subject_id,
        n_ibi=n_ibi,
        window_sec=window_sec,
    )


def create_ibi_record(
    timestamp: float,
    ibi_ms: float,
    modality: Modality = Modality.ECG,
    source: str = "",
    session_id: str = "",
    subject_id: str = "",
    beat_type: str = "normal",
) -> IBIRecord:
    """Create an IBI record with validation."""
    return IBIRecord(
        timestamp=timestamp,
        modality=modality,
        ibi_ms=ibi_ms,
        source=source,
        session_id=session_id,
        subject_id=subject_id,
        beat_type=beat_type,
    )


def validate_hr_value(hr: float, valid_range: tuple = (20.0, 250.0)) -> bool:
    """Check if HR value is in valid range."""
    return valid_range[0] <= hr <= valid_range[1]


def validate_rr_value(rr: float, valid_range: tuple = (6.0, 40.0)) -> bool:
    """Check if RR value is in valid range."""
    return valid_range[0] <= rr <= valid_range[1]


def validate_ibi_value(ibi_ms: float, valid_range: tuple = (300.0, 2000.0)) -> bool:
    """Check if IBI value is in valid range."""
    return valid_range[0] <= ibi_ms <= valid_range[1]


def generate_record_id(record: TimestampRecord) -> str:
    """Generate deterministic ID for a record."""
    content = f"{record.timestamp}|{record.modality.value}|{record.source}|{record.session_id}"
    return hashlib.md5(content.encode()).hexdigest()[:12]
