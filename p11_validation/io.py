"""
Phase 11: Data Import/Export

Dataset loading and result export for validation.
"""

import json
import csv
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


class ValidationLoadError(Exception):
    """Raised when validation data cannot be loaded."""
    pass


class ValidationExportError(Exception):
    """Raised when validation results cannot be exported."""
    pass


@dataclass
class ValidationDataset:
    """
    Container for validation dataset.

    Holds camera estimates, reference measurements, and metadata.
    """
    # Session info
    session_id: str = ""
    subject_id: str = ""  # Pseudonymous
    recording_date: str = ""
    camera_resolution: str = ""

    # Camera estimates
    camera_timestamps: List[float] = field(default_factory=list)
    camera_hr: List[float] = field(default_factory=list)
    camera_hr_confidence: List[float] = field(default_factory=list)
    camera_hr_sqi: List[float] = field(default_factory=list)
    camera_motion_rejected: List[bool] = field(default_factory=list)

    # Reference measurements
    ref_timestamps: List[float] = field(default_factory=list)
    ref_hr: List[float] = field(default_factory=list)
    ref_source: str = ""  # "ecg", "pulse_ox", etc.

    # RR (optional)
    camera_rr: List[float] = field(default_factory=list)
    ref_rr: List[float] = field(default_factory=list)
    ref_rr_source: str = ""

    # HRV / IBI sequences (optional)
    camera_ibi: List[float] = field(default_factory=list)
    ref_ibi: List[float] = field(default_factory=list)
    ref_ibi_source: str = ""   # "ecg", "ppg", etc.

    # Quality metadata
    camera_sqi_breakdown: List[Dict] = field(default_factory=list)

    # Validation results
    validation_results: Dict[str, Any] = field(default_factory=dict)


def load_validation_dataset(path: str) -> ValidationDataset:
    """
    Load validation dataset from JSON file.

    Args:
        path: Path to JSON file

    Returns:
        ValidationDataset

    Raises:
        ValidationLoadError: If file cannot be loaded
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        dataset = ValidationDataset(
            session_id=data.get('session_id', ''),
            subject_id=data.get('subject_id', ''),
            recording_date=data.get('recording_date', ''),
            camera_resolution=data.get('camera_resolution', ''),
            camera_timestamps=data.get('camera_timestamps', []),
            camera_hr=data.get('camera_hr', []),
            camera_hr_confidence=data.get('camera_hr_confidence', []),
            camera_hr_sqi=data.get('camera_hr_sqi', []),
            camera_motion_rejected=data.get('camera_motion_rejected', []),
            ref_timestamps=data.get('ref_timestamps', []),
            ref_hr=data.get('ref_hr', []),
            ref_source=data.get('ref_source', ''),
            camera_rr=data.get('camera_rr', []),
            ref_rr=data.get('ref_rr', []),
            ref_rr_source=data.get('ref_rr_source', ''),
            camera_ibi=data.get('camera_ibi', []),
            ref_ibi=data.get('ref_ibi', []),
            ref_ibi_source=data.get('ref_ibi_source', ''),
            validation_results=data.get('validation_results', {}),
        )

        return dataset

    except FileNotFoundError:
        raise ValidationLoadError(f"File not found: {path}")
    except json.JSONDecodeError as e:
        raise ValidationLoadError(f"Invalid JSON: {e}")
    except Exception as e:
        raise ValidationLoadError(f"Failed to load dataset: {e}")


def save_validation_results(
    results: Dict[str, Any],
    path: str,
    pretty: bool = True,
) -> None:
    """
    Save validation results to JSON file.

    Args:
        results: Validation results dict
        path: Output path
        pretty: Use pretty formatting

    Raises:
        ValidationExportError: If export fails
    """
    try:
        # Add metadata
        output = {
            "validation_results": results,
            "_metadata": {
                "exported_at": datetime.now().isoformat(),
                "format_version": "1.0",
            }
        }

        with open(path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(output, f, indent=2, default=str)
            else:
                json.dump(output, f, default=str)

    except PermissionError:
        raise ValidationExportError(f"Permission denied: {path}")
    except Exception as e:
        raise ValidationExportError(f"Failed to save: {e}")


def export_results_csv(
    results: Dict[str, Any],
    path: str,
) -> None:
    """
    Export results to CSV format.

    Args:
        results: Validation results dict
        path: Output CSV path

    Raises:
        ValidationExportError: If export fails
    """
    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            if not results:
                return

            # Get all keys from first result
            fieldnames = set()
            for key in results.keys():
                if isinstance(results[key], dict):
                    fieldnames.update(results[key].keys())

            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()

            for label, metrics in results.items():
                if isinstance(metrics, dict):
                    row = {"metric": label}
                    row.update(metrics)
                    writer.writerow(row)

    except PermissionError:
        raise ValidationExportError(f"Permission denied: {path}")
    except Exception as e:
        raise ValidationExportError(f"Failed to export CSV: {e}")


def import_reference_csv(
    path: str,
    timestamp_col: str = "timestamp",
    value_col: str = "value",
    source_col: Optional[str] = None,
) -> ValidationDataset:
    """
    Import reference data from CSV file.

    Args:
        path: Path to CSV file
        timestamp_col: Column name for timestamps
        value_col: Column name for values
        source_col: Optional column for source/label

    Returns:
        ValidationDataset with reference data

    Raises:
        ValidationLoadError: If import fails
    """
    dataset = ValidationDataset()

    try:
        with open(path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    ts = float(row.get(timestamp_col, 0))
                    val = float(row.get(value_col, 0))

                    dataset.ref_timestamps.append(ts)
                    dataset.ref_hr.append(val)

                    if source_col and source_col in row:
                        # Source is recorded separately per entry
                        pass

                except (ValueError, KeyError):
                    continue

    except FileNotFoundError:
        raise ValidationLoadError(f"Reference file not found: {path}")
    except Exception as e:
        raise ValidationLoadError(f"Failed to import reference: {e}")

    return dataset


def create_synthetic_fixture(
    n_samples: int = 100,
    seed: int = 42,
    hr_mean: float = 70.0,
    hr_std: float = 5.0,
    error_mean: float = 0.0,
    error_std: float = 2.0,
    timestamp_start: float = 0.0,
    timestamp_interval: float = 1.0,
) -> ValidationDataset:
    """
    Create synthetic validation fixture for software testing.

    WARNING: For testing only. Do not report as real validation.

    Args:
        n_samples: Number of samples
        seed: Random seed
        hr_mean: Mean HR value
        hr_std: HR standard deviation
        error_mean: Mean estimation error
        error_std: Estimation error standard deviation
        timestamp_start: Start timestamp
        timestamp_interval: Interval between samples

    Returns:
        ValidationDataset with perfect alignment
    """
    np.random.seed(seed)

    dataset = ValidationDataset(
        session_id="synthetic_fixture",
        subject_id="test_subject",
        recording_date=datetime.now().isoformat(),
        ref_source="synthetic",
    )

    # Generate reference HR
    ref_hr = np.random.normal(hr_mean, hr_std, n_samples).tolist()
    ref_timestamps = [
        timestamp_start + i * timestamp_interval
        for i in range(n_samples)
    ]

    # Generate camera estimates with known error
    camera_hr = [
        ref + np.random.normal(error_mean, error_std)
        for ref in ref_hr
    ]

    # Perfect synchronization (same timestamps)
    dataset.ref_timestamps = ref_timestamps
    dataset.ref_hr = ref_hr
    dataset.camera_timestamps = ref_timestamps
    dataset.camera_hr = camera_hr
    dataset.camera_hr_confidence = [0.8] * n_samples
    dataset.camera_hr_sqi = [0.8] * n_samples
    dataset.camera_motion_rejected = [False] * n_samples

    return dataset


def validate_dataset(dataset: ValidationDataset) -> List[str]:
    """
    Validate dataset integrity.

    Args:
        dataset: ValidationDataset to validate

    Returns:
        List of validation warnings/errors
    """
    issues = []

    # Check lengths match
    if dataset.camera_timestamps and dataset.camera_hr:
        if len(dataset.camera_timestamps) != len(dataset.camera_hr):
            issues.append(
                "Camera timestamps and HR have mismatched lengths"
            )

    if dataset.ref_timestamps and dataset.ref_hr:
        if len(dataset.ref_timestamps) != len(dataset.ref_hr):
            issues.append(
                "Reference timestamps and HR have mismatched lengths"
            )

    # Check for NaN/Inf
    for i, hr in enumerate(dataset.camera_hr):
        if np.isnan(hr) or np.isinf(hr):
            issues.append(f"Camera HR[{i}] is NaN or Inf: {hr}")
            break

    for i, hr in enumerate(dataset.ref_hr):
        if np.isnan(hr) or np.isinf(hr):
            issues.append(f"Reference HR[{i}] is NaN or Inf: {hr}")
            break

    # Check timestamps
    if dataset.camera_timestamps:
        if dataset.camera_timestamps != sorted(dataset.camera_timestamps):
            issues.append("Camera timestamps are not monotonically increasing")

    if dataset.ref_timestamps:
        if dataset.ref_timestamps != sorted(dataset.ref_timestamps):
            issues.append("Reference timestamps are not monotonically increasing")

    return issues
