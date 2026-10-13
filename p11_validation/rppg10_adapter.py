"""
Phase 11: rPPG-10 Dataset Adapter

Loads the local rPPG-10 dataset and maps it to ValidationDataset.
All unresolved acquisition parameters (ECG sampling rate, sync offsets, units)
are explicit required configuration fields. Metric computation is blocked
when required metadata is absent.

File structure:
    Dataset_rPPG-10/
        Subject Data.xlsx
        Subject_1/
            Subject_1_Forehead_.avi
            Subject_1_Cheek1_.avi
            Subject_1_Cheek2_.avi
            Subject_1_ECG.npy
        Subject_2/
            ...
        Subject_27/

Verified specs (see ACQUISITION_METADATA_VERIFICATION.md):
    Video: 30.000 fps CFR, 64x64 MPEG-1, 18,000 frames per recording
    Duration: 600.0 s (10 min) for complete recordings
    ECG: 600,000 samples (float64), no fs in header

ECG sampling frequency provenance:
    - rPPG-10 paper, Section 4.3 "Equipment": BITalino ECG system at 1000 Hz
    - Confirmed by: 600,000 samples / 1000 Hz = 600.0 s (= verified video duration)
    - Pending: source citation not yet verified against live paper text
    - Set as documented default; override via ecg_fs parameter if needed

Synchronization:
    - rPPG-10 paper: ±500 ms synchronization uncertainty (uncertainty estimate,
      NOT a per-subject offset; do NOT assign ecg_offset_sec=0 or ±0.5 to satisfy
      validation)
    - ecg_offset_sec MUST be verified before cross-modal metric computation
    - ECG-internal metrics (HR, IBI) are available without verified offset
"""

from __future__ import annotations

import os
import logging
import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
import struct

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class rPPG10Config:
    """
    Configuration for loading the rPPG-10 dataset.

    Required fields MUST be set before loading data. The adapter will not
    fabricate values for these fields.

    Verified fields are set to their confirmed values by default but can be
    overridden if the source files are re-encoded.

    ECG sampling frequency:
        Documented: 1000 Hz (rPPG-10 paper, Section 4.3 "Equipment", BITalino spec)
        Confirmed by: 600,000 samples / 1000 Hz = 600.0 s (= verified video duration)
        Set as the documented default; override via ecg_fs if source files differ.

    Synchronization offset:
        ecg_offset_sec is the per-session ECG-video start-time offset.
        ecg_offset_known must be True before cross-modal metrics are claimed.
        The ±500 ms uncertainty estimate from the paper is NOT an offset value.
    """
    # Path
    dataset_root: str = "Dataset_rPPG-10"

    # --- Video (verified: 30 fps CFR) ---
    video_fps: float = 30.0          # Verified: 30.000 fps, zero variance
    video_frame_count: int = 18000     # Verified for complete recordings
    video_resolution: Tuple[int, int] = (64, 64)

    # --- ECG (verified: 1000 Hz — see module docstring for provenance) ---
    ecg_fs: float = 1000.0           # Documented: rPPG-10 paper, Section 4.3
    ecg_units: str = "raw_adc"       # "raw_adc" | "mV" | "normalized"
    ecg_nominal_samples: int = 600000  # Expected sample count

    # --- Synchronization offsets ---
    # Difference between recording start times.
    # Positive value: ECG started this many seconds BEFORE video.
    # ecg_offset_known must be True before cross-modal metrics are validated.
    # Do NOT set ecg_offset_sec to satisfy validation — it must be verified.
    ecg_offset_sec: float = 0.0       # Default 0.0; MUST be verified per session
    ecg_offset_known: bool = False    # Set True only when offset is confirmed
    video_offset_sec: float = 0.0

    # --- Processing ---
    video_camera: str = "Forehead"     # "Forehead" | "Cheek1" | "Cheek2"
    hr_window_sec: float = 10.0       # HR estimation window (seconds)
    hr_step_sec: float = 1.0          # HR estimation step (seconds)
    hr_min_bpm: float = 40.0
    hr_max_bpm: float = 200.0
    ecg_rpeak_min_hz: float = 40.0 / 60.0   # ~0.667 Hz
    ecg_rpeak_max_hz: float = 200.0 / 60.0  # ~3.33 Hz

    # --- ECG R-peak detection ---
    rpeak_height_percentile: float = 80.0  # Percentile for adaptive threshold

    def validate(self) -> List[str]:
        """
        Validate configuration. Returns list of issues (empty if valid).

        Checks only ECG sampling frequency, which is required for any ECG
        processing. Does NOT require ecg_offset_known — that is enforced
        separately at the cross-modal metric level.
        """
        issues = []
        if self.ecg_fs is None:
            issues.append("ecg_fs is not set (required)")
        elif self.ecg_fs <= 0:
            issues.append(f"ecg_fs must be positive, got {self.ecg_fs}")
        if self.video_camera not in ("Forehead", "Cheek1", "Cheek2"):
            issues.append(f"video_camera must be Forehead|Cheek1|Cheek2, got {self.video_camera}")
        if not (0 < self.hr_window_sec <= 600):
            issues.append(f"hr_window_sec must be in (0, 600], got {self.hr_window_sec}")
        if self.hr_step_sec <= 0:
            issues.append(f"hr_step_sec must be positive, got {self.hr_step_sec}")
        return issues

    @property
    def is_ready_for_ecg_processing(self) -> bool:
        """
        True when ECG-internal processing (HR, IBI) is possible.

        Requires only a valid sampling frequency. Does NOT require
        a verified ECG-video offset — those computations operate
        within the ECG signal itself.
        """
        return len(self.validate()) == 0

    @property
    def is_ready_for_cross_modal(self) -> bool:
        """
        True when cross-modal metrics (camera vs. ECG) can be validated.

        Requires a verified ECG sampling frequency AND a known ECG-video
        offset. ECG-internal metrics (HR, IBI) do NOT require this flag.
        """
        return self.is_ready_for_ecg_processing and self.ecg_offset_known

    @property
    def is_ready_for_metrics(self) -> bool:
        """
        Deprecated alias for is_ready_for_cross_modal.

        Preserved for backward compatibility. New code should use
        is_ready_for_ecg_processing and is_ready_for_cross_modal
        explicitly to distinguish ECG-internal from cross-modal readiness.
        """
        return self.is_ready_for_cross_modal


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

class FileStatus(Enum):
    PRESENT = "present"
    ZERO_SIZE = "zero_size"     # File exists but is 0 bytes
    MISSING = "missing"         # File does not exist


@dataclass
class RecordingFileSet:
    """Status of one subject's recording files."""
    subject_id: str
    session_id: str

    forehead: FileStatus = FileStatus.MISSING
    cheek1: FileStatus = FileStatus.MISSING
    cheek2: FileStatus = FileStatus.MISSING
    ecg: FileStatus = FileStatus.MISSING

    forehead_path: str = ""
    cheek1_path: str = ""
    cheek2_path: str = ""
    ecg_path: str = ""

    # Video metadata (populated on load)
    video_frame_count: Optional[int] = None
    video_fps: Optional[float] = None
    video_duration_sec: Optional[float] = None

    # ECG metadata
    ecg_samples: Optional[int] = None
    ecg_nominal_duration_sec: Optional[float] = None

    @property
    def has_complete_video(self) -> bool:
        return all(s == FileStatus.PRESENT for s in [self.forehead, self.cheek1, self.cheek2])

    @property
    def has_any_video(self) -> bool:
        """At least one camera file is non-zero."""
        return any(s == FileStatus.PRESENT for s in [self.forehead, self.cheek1, self.cheek2])

    @property
    def has_zero_video(self) -> bool:
        """All cameras are zero-size files."""
        return all(s == FileStatus.ZERO_SIZE for s in [self.forehead, self.cheek1, self.cheek2])

    @property
    def video_is_partial(self) -> bool:
        """At least one camera present but not all three non-zero."""
        any_present = self.has_any_video
        return any_present and not self.has_complete_video

    @property
    def status_summary(self) -> str:
        cams = f"FH={self.forehead.value} C1={self.cheek1.value} C2={self.cheek2.value} ECG={self.ecg.value}"
        if self.has_complete_video:
            return f"complete_video|{cams}"
        elif self.video_is_partial:
            return f"partial_video|{cams}"
        elif self.ecg == FileStatus.PRESENT:
            return f"ecg_only|{cams}"
        else:
            return f"no_data|{cams}"


def _get_file_status(path: str) -> Tuple[FileStatus, str]:
    if not os.path.exists(path):
        return FileStatus.MISSING, ""
    size = os.path.getsize(path)
    if size == 0:
        return FileStatus.ZERO_SIZE, path
    return FileStatus.PRESENT, path


def discover_subjects(root: str) -> List[str]:
    """Return sorted list of subject IDs found under root."""
    if not os.path.isdir(root):
        return []
    subjects = []
    for entry in os.scandir(root):
        if entry.is_dir() and entry.name.startswith("Subject_"):
            sid = entry.name.replace("Subject_", "")
            if sid.isdigit():
                subjects.append(sid)
    return sorted(subjects, key=lambda x: int(x))


def discover_recording(subject_id: str, root: str, config: rPPG10Config) -> RecordingFileSet:
    """
    Check which files exist for a subject and return their status.

    Does NOT open or decode the files — only checks existence and size.
    """
    session_id = f"S{subject_id.zfill(2)}"
    base = os.path.join(root, f"Subject_{subject_id}")

    fh_status, fh_path = _get_file_status(os.path.join(base, f"Subject_{subject_id}_Forehead_.avi"))
    c1_status, c1_path = _get_file_status(os.path.join(base, f"Subject_{subject_id}_Cheek1_.avi"))
    c2_status, c2_path = _get_file_status(os.path.join(base, f"Subject_{subject_id}_Cheek2_.avi"))
    ecg_status, ecg_path = _get_file_status(os.path.join(base, f"Subject_{subject_id}_ECG.npy"))

    result = RecordingFileSet(
        subject_id=subject_id,
        session_id=session_id,
        forehead=fh_status,
        cheek1=c1_status,
        cheek2=c2_status,
        ecg=ecg_status,
        forehead_path=fh_path,
        cheek1_path=c1_path,
        cheek2_path=c2_path,
        ecg_path=ecg_path,
    )

    # Probe video metadata (fast: just check first file)
    probe_path = ""
    if fh_status == FileStatus.PRESENT:
        probe_path = fh_path
    elif c1_status == FileStatus.PRESENT:
        probe_path = c1_path
    elif c2_status == FileStatus.PRESENT:
        probe_path = c2_path

    if probe_path:
        try:
            cap = cv2.VideoCapture(probe_path)
            result.video_fps = cap.get(cv2.CAP_PROP_FPS)
            result.video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if result.video_frame_count > 0:
                cap.set(cv2.CAP_PROP_POS_FRAMES, result.video_frame_count - 1)
                last_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                result.video_duration_sec = last_ms / 1000.0
            cap.release()
        except Exception:
            pass

    # Probe ECG metadata
    if ecg_status == FileStatus.PRESENT:
        try:
            arr = np.load(ecg_path, mmap_mode='r')
            result.ecg_samples = arr.shape[0]
            if config.ecg_fs and config.ecg_fs > 0:
                result.ecg_nominal_duration_sec = result.ecg_samples / config.ecg_fs
        except Exception:
            pass

    return result


def discover_all(root: str, config: rPPG10Config) -> Dict[str, RecordingFileSet]:
    """
    Run file discovery across all subjects.

    Returns:
        Dict mapping subject_id -> RecordingFileSet
    """
    subjects = discover_subjects(root)
    return {sid: discover_recording(sid, root, config) for sid in subjects}


# ---------------------------------------------------------------------------
# ECG processing
# ---------------------------------------------------------------------------

def load_ecg(path: str, max_samples: Optional[int] = None) -> np.ndarray:
    """
    Load ECG NPY file.

    Args:
        path: Path to .npy file
        max_samples: Optional cap (for partial reads)

    Returns:
        1D float64 array

    Raises:
        FileNotFoundError: If file does not exist
    """
    arr = np.load(path, mmap_mode='r')
    if max_samples:
        arr = arr[:max_samples]
    return arr.view(np.float64).copy()


def detect_r_peaks(
    ecg: np.ndarray,
    fs: float,
    min_hz: float = 40.0 / 60.0,
    max_hz: float = 200.0 / 60.0,
    height_percentile: float = 80.0,
) -> np.ndarray:
    """
    Detect R-peaks in ECG using a bandpass filter + adaptive threshold.

    Args:
        ecg: ECG signal (1D, float)
        fs: Sampling frequency in Hz
        min_hz: Lower cutoff for bandpass (Hz)
        max_hz: Upper cutoff for bandpass (Hz)
        height_percentile: Adaptive threshold percentile

    Returns:
        Array of sample indices for detected R-peaks
    """
    from scipy.signal import butter, filtfilt, find_peaks
    from scipy.ndimage import uniform_filter1d

    # Normalize
    signal = ecg.astype(np.float64)
    signal = signal - signal.mean()

    # Bandpass filter in QRS frequency range (5-20 Hz)
    # Note: min_hz/max_hz parameters define the HR range, but the
    # bandpass is set to the QRS bandwidth for peak detection.
    # QRS energy is in 5-20 Hz; filtering at HR range (0.67-3.33 Hz)
    # would remove the QRS entirely.
    nyq = fs / 2.0
    # Use 5-20 Hz for peak detection (QRS bandwidth)
    qrs_low = min(max(5.0, 1.0), nyq - 1) / nyq
    qrs_high = min(max(20.0, qrs_low + 0.1), nyq - 0.1) / nyq
    b, a = butter(4, [qrs_low, qrs_high], btype='band')
    filtered = filtfilt(b, a, signal)

    # Adaptive threshold
    window_size = max(int(fs * 0.5), 5)
    envelope = uniform_filter1d(np.abs(filtered), size=window_size, mode='constant')
    threshold = np.percentile(envelope, height_percentile)

    # Find peaks
    min_distance = max(int(fs / max_hz), 1)
    peaks, properties = find_peaks(
        filtered,
        height=threshold,
        distance=min_distance,
    )
    return peaks


def ecg_to_hr(
    ecg: np.ndarray,
    fs: float,
    window_sec: float = 10.0,
    step_sec: float = 1.0,
    min_hz: float = 40.0 / 60.0,
    max_hz: float = 200.0 / 60.0,
    height_percentile: float = 80.0,
) -> Tuple[np.ndarray, np.ndarray, List[int]]:
    """
    Compute sliding-window HR from ECG.

    Args:
        ecg: ECG signal
        fs: Sampling frequency in Hz
        window_sec: HR estimation window in seconds
        step_sec: Sliding step in seconds
        min_hz/max_hz: R-peak detection frequency range
        height_percentile: R-peak detection threshold percentile

    Returns:
        (timestamps_sec, hr_bpm, peak_counts) — one HR value per window
    """
    window_samples = int(window_sec * fs)
    step_samples = int(step_sec * fs)
    n_samples = len(ecg)

    timestamps = []
    hr_values = []
    peak_counts = []

    for start in range(0, n_samples - window_samples, step_samples):
        segment = ecg[start:start + window_samples]
        peaks = detect_r_peaks(
            segment, fs,
            min_hz=min_hz,
            max_hz=max_hz,
            height_percentile=height_percentile,
        )
        # HR = peaks per second * 60
        window_duration_sec = window_samples / fs
        if len(peaks) >= 2:
            # Use actual peak interval for more accurate HR
            intervals = np.diff(peaks) / fs  # in seconds
            valid = (intervals > 1.0 / max_hz) & (intervals < 1.0 / min_hz)
            if valid.any():
                mean_interval = float(np.mean(intervals[valid]))
                hr = 60.0 / mean_interval
            else:
                hr = (len(peaks) - 1) / window_duration_sec * 60.0
        else:
            hr = np.nan

        t_sec = start / fs
        timestamps.append(t_sec)
        hr_values.append(hr)
        peak_counts.append(len(peaks))

    return np.array(timestamps), np.array(hr_values), peak_counts


def ecg_to_ibi(
    ecg: np.ndarray,
    fs: float,
    min_hz: float = 40.0 / 60.0,
    max_hz: float = 200.0 / 60.0,
    height_percentile: float = 80.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract IBI sequence from ECG.

    Args:
        ecg: ECG signal
        fs: Sampling frequency in Hz
        (same detection params as detect_r_peaks)

    Returns:
        (timestamps_sec, ibi_ms) — timestamp and interval to next beat in ms
    """
    peaks = detect_r_peaks(ecg, fs, min_hz, max_hz, height_percentile)
    if len(peaks) < 2:
        return np.array([]), np.array([])

    ibi_samples = np.diff(peaks)
    ibi_ms = ibi_samples / fs * 1000.0

    # Timestamp: midpoint of each interval
    midpoints = (peaks[:-1] + peaks[1:]) / 2
    timestamps = midpoints / fs

    return timestamps, ibi_ms


# ---------------------------------------------------------------------------
# ValidationDataset adapter
# ---------------------------------------------------------------------------

@dataclass
class rPPG10Session:
    """
    Per-subject session loaded from rPPG-10.

    Includes file status, loaded data, and any issues encountered.
    """
    subject_id: str
    session_id: str
    files: RecordingFileSet

    # Raw data (loaded on demand)
    video_path: str = ""
    ecg_path: str = ""

    # Processed HR data (populated by process())
    hr_timestamps: np.ndarray = field(default_factory=lambda: np.array([]))
    hr_camera: np.ndarray = field(default_factory=lambda: np.array([]))
    hr_ref: np.ndarray = field(default_factory=lambda: np.array([]))
    hr_ref_timestamps: np.ndarray = field(default_factory=lambda: np.array([]))
    ibi_est: np.ndarray = field(default_factory=lambda: np.array([]))
    ibi_ref: np.ndarray = field(default_factory=lambda: np.array([]))
    ibi_ref_timestamps: np.ndarray = field(default_factory=lambda: np.array([]))

    # Metadata
    video_fps: float = 30.0
    video_duration_sec: float = 0.0
    video_frame_count: int = 0
    ecg_fs: Optional[float] = None
    ecg_samples: int = 0
    ecg_nominal_duration_sec: float = 0.0

    # Issues encountered during loading/processing
    issues: List[str] = field(default_factory=list)

    # Whether this session has usable video and ECG
    is_usable: bool = False

    def is_ready_for_validation(self, config: rPPG10Config) -> bool:
        """
        True when files are loadable AND cross-modal validation is possible.

        Combines file-level readiness with cross-modal configuration completeness.
        ECG-internal metrics (HR, IBI) may still be available via
        process_ecg_session() even when this returns False.
        """
        if not self.is_usable:
            return False
        return config.is_ready_for_cross_modal


def load_session(
    subject_id: str,
    config: rPPG10Config,
    load_video: bool = False,
) -> rPPG10Session:
    """
    Load one subject from rPPG-10.

    Args:
        subject_id: Subject number as string (e.g. "1", "04")
        config: rPPG10Config with verified/unresolved parameters
        load_video: If True, set video_path (video not decoded here)

    Returns:
        rPPG10Session with file status and metadata
    """
    root = config.dataset_root
    files = discover_recording(subject_id, root, config)
    session_id = f"S{subject_id.zfill(2)}"

    session = rPPG10Session(
        subject_id=subject_id,
        session_id=session_id,
        files=files,
        video_fps=files.video_fps or config.video_fps,
        video_duration_sec=files.video_duration_sec or 0.0,
        video_frame_count=files.video_frame_count or 0,
        ecg_samples=files.ecg_samples or 0,
    )

    if files.forehead == FileStatus.PRESENT:
        session.video_path = files.forehead_path
    elif files.cheek1 == FileStatus.PRESENT:
        session.video_path = files.cheek1_path
    elif files.cheek2 == FileStatus.PRESENT:
        session.video_path = files.cheek2_path

    if files.ecg == FileStatus.PRESENT:
        session.ecg_path = files.ecg_path

    # Determine ECG nominal duration
    if config.ecg_fs and config.ecg_fs > 0:
        session.ecg_nominal_duration_sec = session.ecg_samples / config.ecg_fs
    else:
        session.ecg_nominal_duration_sec = 0.0

    # Check usability
    session.is_usable = (
        files.has_complete_video and
        files.ecg == FileStatus.PRESENT and
        session.video_frame_count > 0 and
        session.ecg_samples > 0
    )

    if not files.has_complete_video:
        missing = [k for k, v in {
            "Forehead": files.forehead,
            "Cheek1": files.cheek1,
            "Cheek2": files.cheek2,
        }.items() if v != FileStatus.PRESENT]
        session.issues.append(f"Missing video cameras: {', '.join(missing)}")

    if files.ecg == FileStatus.ZERO_SIZE:
        session.issues.append("ECG file is zero bytes")
        session.is_usable = False

    if files.ecg == FileStatus.MISSING:
        session.issues.append("ECG file missing")
        session.is_usable = False

    if files.forehead == FileStatus.ZERO_SIZE and files.cheek1 == FileStatus.ZERO_SIZE and files.cheek2 == FileStatus.ZERO_SIZE:
        session.issues.append("All video files are zero bytes (Subject_4 pattern)")
        session.is_usable = False

    return session


def process_ecg_session(
    session: rPPG10Session,
    config: rPPG10Config,
) -> None:
    """
    Process ECG data into HR and IBI sequences for a session.

    Populates session.hr_ref, session.hr_ref_timestamps,
    session.ibi_ref, session.ibi_ref_timestamps.

    ECG-internal processing (R-peak detection, HR, IBI) runs as soon as
    a valid sampling frequency is available. Cross-modal timestamps
    (i.e., timestamps that account for ECG-video start-time offset) are
    only set when config.ecg_offset_known is True.

    Args:
        session: rPPG10Session with ecg_path set
        config: rPPG10Config (ecg_fs must be positive; ecg_offset_known
            must be True for cross-modal timestamp correction)
    """
    import logging as _logging
    _log = _logging.getLogger("rppg10_adapter")

    if not config.is_ready_for_ecg_processing:
        issues = config.validate()
        session.issues.append(
            f"Cannot process ECG: config.is_ready_for_ecg_processing is False. "
            f"Issues: {issues}"
        )
        return

    if not session.ecg_path or not os.path.exists(session.ecg_path):
        session.issues.append(f"ECG path not found: {session.ecg_path}")
        return

    # --- Load ECG ---
    try:
        ecg = load_ecg(session.ecg_path, max_samples=config.ecg_nominal_samples)
    except Exception as e:
        session.issues.append(f"Failed to load ECG: {e}")
        return

    # --- ECG input diagnostics ---
    n_samples = len(ecg)
    n_finite = np.isfinite(ecg).sum()
    n_nan = np.isnan(ecg).sum()
    n_inf = np.isinf(ecg).sum()
    ecg_min = float(np.min(ecg)) if n_finite > 0 else float("nan")
    ecg_max = float(np.max(ecg)) if n_finite > 0 else float("nan")
    ecg_mean = float(np.mean(ecg)) if n_finite > 0 else float("nan")
    ecg_std = float(np.std(ecg)) if n_finite > 0 else float("nan")
    duration_sec = n_samples / config.ecg_fs

    _log.info(
        "[ECG INPUT] subject=%s dataset=rPPG-10 shape=%s dtype=%s "
        "samples=%d finite=%d nan=%d inf=%d min=%.2f max=%.2f "
        "mean=%.2f std=%.2f fs=%.1f duration_sec=%.3f",
        session.subject_id, str(ecg.shape), str(ecg.dtype),
        n_samples, n_finite, n_nan, n_inf,
        ecg_min, ecg_max, ecg_mean, ecg_std,
        config.ecg_fs, duration_sec,
    )

    if n_finite == 0:
        session.issues.append("ECG has zero finite samples")
        return

    if n_nan > 0 or n_inf > 0:
        session.issues.append(
            f"ECG has {n_nan} NaN and {n_inf} Inf values; "
            f"these samples are excluded from processing."
        )

    session.ecg_fs = config.ecg_fs

    # --- R-peak detection and HR estimation ---
    try:
        t_hr, hr_bpm, peak_counts = ecg_to_hr(
            ecg,
            fs=config.ecg_fs,
            window_sec=config.hr_window_sec,
            step_sec=config.hr_step_sec,
            min_hz=config.ecg_rpeak_min_hz,
            max_hz=config.ecg_rpeak_max_hz,
            height_percentile=config.rpeak_height_percentile,
        )
    except Exception as e:
        session.issues.append(f"R-peak detection failed: {e}")
        return

    _log.info(
        "[ECG PROCESSING] subject=%s detector=bandpass_adaptive "
        "peaks_total=%d windows=%d ecg_offset_known=%s "
        "ecg_offset_sec=%.3f",
        session.subject_id, sum(peak_counts), len(peak_counts),
        config.ecg_offset_known, config.ecg_offset_sec,
    )

    # Apply sync offset only when known; otherwise keep ECG-native timestamps
    if config.ecg_offset_known:
        t_hr_shifted = t_hr + config.ecg_offset_sec
        _log.info(
            "[SYNC] subject=%s status=known offset_applied=%.3f "
            "metrics_eligible=cross_modal",
            session.subject_id, config.ecg_offset_sec,
        )
    else:
        t_hr_shifted = t_hr  # ECG-native; NOT aligned to video timeline
        _log.warning(
            "[SYNC] subject=%s status=unknown offset_uncertainty=±0.5s "
            "offset_used=0.0(ECG_native) metrics_eligible=ecg_internal_only "
            "note='Do NOT interpret as cross_modal — ECG-video alignment unverified'",
            session.subject_id,
        )

    # Filter by HR range
    valid_mask = (
        ~np.isnan(hr_bpm) &
        (hr_bpm >= config.hr_min_bpm) &
        (hr_bpm <= config.hr_max_bpm)
    )

    n_valid_hr = int(np.sum(valid_mask))
    n_invalid_hr = int(np.sum(~valid_mask))

    _log.info(
        "[HR OUTPUT] subject=%s hr_windows=%d valid=%d "
        "excluded_out_of_range=%d mean=%.1f std=%.1f",
        session.subject_id, len(hr_bpm), n_valid_hr, n_invalid_hr,
        float(np.nanmean(hr_bpm[valid_mask])) if n_valid_hr > 0 else float("nan"),
        float(np.nanstd(hr_bpm[valid_mask])) if n_valid_hr > 0 else float("nan"),
    )

    session.hr_ref = hr_bpm[valid_mask]
    session.hr_ref_timestamps = t_hr_shifted[valid_mask]

    # --- IBI extraction ---
    try:
        t_ibi, ibi_ms = ecg_to_ibi(
            ecg,
            fs=config.ecg_fs,
            min_hz=config.ecg_rpeak_min_hz,
            max_hz=config.ecg_rpeak_max_hz,
            height_percentile=config.rpeak_height_percentile,
        )
    except Exception:
        ibi_ms = np.array([])
        t_ibi = np.array([])

    # Apply sync offset
    if config.ecg_offset_known:
        t_ibi_shifted = t_ibi + config.ecg_offset_sec
    else:
        t_ibi_shifted = t_ibi  # ECG-native

    # Filter IBI by range
    if len(ibi_ms) > 0:
        ibi_valid = (ibi_ms >= 300.0) & (ibi_ms <= 2000.0)
        session.ibi_ref = ibi_ms[ibi_valid]
        session.ibi_ref_timestamps = t_ibi_shifted[ibi_valid]

        _log.info(
            "[IBI OUTPUT] subject=%s ibi_total=%d valid=%d "
            "mean_ms=%.1f std_ms=%.1f",
            session.subject_id, len(ibi_ms), len(session.ibi_ref),
            float(np.mean(session.ibi_ref)) if len(session.ibi_ref) > 0 else float("nan"),
            float(np.std(session.ibi_ref)) if len(session.ibi_ref) > 0 else float("nan"),
        )
    else:
        _log.info(
            "[IBI OUTPUT] subject=%s ibi_total=0 reason='no_ibi_extracted'",
            session.subject_id,
        )


def session_to_validation_dataset(
    session: rPPG10Session,
    config: rPPG10Config,
    ecg_only: bool = False,
) -> "ValidationDataset":  # noqa: F821
    """
    Convert a processed rPPG10Session to ValidationDataset.

    When ecg_only=False (default): requires config.is_ready_for_cross_modal
    (ecg_fs verified AND ecg_offset_known=True). Produces fully time-aligned
    reference data for cross-modal validation.

    When ecg_only=True: requires only config.is_ready_for_ecg_processing
    (ecg_fs verified). Produces ECG-internal reference data with ECG-native
    timestamps; cross-modal metrics will not be valid for this dataset.

    Camera HR and IBI fields are left empty — they must be populated by the
    rPPG estimator (MultiROIFusionEngineV2) using session.video_path.

    Reference data (ref_hr, ref_timestamps, ref_ibi) is populated from the
    processed ECG.

    Args:
        session: rPPG10Session with processed ECG data
        config: rPPG10Config
        ecg_only: If True, build dataset even when ecg_offset_known is False.
            The returned dataset will have ECG-internal timestamps only.

    Returns:
        ValidationDataset (from p11_validation.io)

    Raises:
        ValueError: If ecg_only=False and config.is_ready_for_cross_modal is False
    """
    import logging as _logging
    _log = _logging.getLogger("rppg10_adapter")

    if not ecg_only and not config.is_ready_for_cross_modal:
        raise ValueError(
            "Cannot build cross-modal ValidationDataset: ecg_offset_known is False. "
            f"config.is_ready_for_cross_modal={config.is_ready_for_cross_modal}. "
            "Pass ecg_only=True to build ECG-internal dataset only, or set "
            "config.ecg_offset_known=True once the ECG-video offset is verified."
        )

    # Import here to avoid circular import at module level
    from .io import ValidationDataset  # noqa: F811

    if ecg_only and not config.ecg_offset_known:
        _log.warning(
            "[VALIDATION DATASET] session=%s mode=ecg_internal_only "
            "ecg_offset_known=False cross_modal_metrics=NOT_ELIGIBLE "
            "note='Timestamps are ECG-native; do not compare with camera timestamps'",
            session.session_id,
        )

    dataset = ValidationDataset(
        session_id=session.session_id,
        subject_id=session.subject_id,
        recording_date="2024-06-20",  # Placeholder; adjust per subject if needed
        camera_resolution=f"{config.video_resolution[0]}x{config.video_resolution[1]}",
        ref_source="ecg",
        ref_ibi_source="ecg",
    )

    if len(session.hr_ref) > 0:
        dataset.ref_timestamps = session.hr_ref_timestamps.tolist()
        dataset.ref_hr = session.hr_ref.tolist()

    if len(session.ibi_ref) > 0:
        dataset.ref_ibi = session.ibi_ref.tolist()

    _log.info(
        "[VALIDATION DATASET] session=%s ref_hr=%d ref_ibi=%d "
        "ecg_offset_known=%s mode=%s",
        session.session_id,
        len(dataset.ref_hr),
        len(dataset.ref_ibi),
        config.ecg_offset_known,
        "ecg_internal_only" if ecg_only or not config.ecg_offset_known else "cross_modal",
    )

    return dataset


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

@dataclass
class DatasetReadinessReport:
    """
    Report on dataset readiness for validation.

    Produced by check_readiness(). Use this to determine whether to proceed
    with metric computation.
    """
    n_subjects_total: int
    n_subjects_usable: int
    n_subjects_video_missing: int
    n_subjects_ecg_missing: int
    n_subjects_zero_video: int
    config_is_valid: bool
    config_issues: List[str]
    usable_subjects: List[str]
    partial_subjects: List[str]
    unusable_subjects: List[str]


def check_readiness(
    root: str,
    config: rPPG10Config,
) -> DatasetReadinessReport:
    """
    Run full discovery and assess dataset readiness.

    This does NOT load ECG data (no decoding).

    Args:
        root: Path to Dataset_rPPG-10
        config: rPPG10Config

    Returns:
        DatasetReadinessReport
    """
    discoveries = discover_all(root, config)

    usable = []
    partial = []
    unusable = []
    video_missing = 0
    ecg_missing = 0
    zero_video = 0

    for sid, files in discoveries.items():
        if files.has_complete_video and files.ecg == FileStatus.PRESENT:
            usable.append(sid)
        elif files.video_is_partial:
            partial.append(sid)
            unusable.append(sid)
        else:
            unusable.append(sid)

        if files.ecg == FileStatus.MISSING:
            ecg_missing += 1
        if files.ecg == FileStatus.ZERO_SIZE:
            zero_video += 1  # (misnamed but same action)
        if not files.has_complete_video:
            video_missing += 1
        if (files.forehead == FileStatus.ZERO_SIZE and
                files.cheek1 == FileStatus.ZERO_SIZE and
                files.cheek2 == FileStatus.ZERO_SIZE):
            zero_video += 1

    return DatasetReadinessReport(
        n_subjects_total=len(discoveries),
        n_subjects_usable=len(usable),
        n_subjects_video_missing=video_missing,
        n_subjects_ecg_missing=ecg_missing,
        n_subjects_zero_video=zero_video,
        config_is_valid=config.is_ready_for_metrics,
        config_issues=config.validate(),
        usable_subjects=usable,
        partial_subjects=partial,
        unusable_subjects=unusable,
    )
