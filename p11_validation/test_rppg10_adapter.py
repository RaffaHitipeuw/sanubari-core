"""
Tests for rPPG-10 Dataset Adapter

Covers:
- File discovery (all subjects, all cameras)
- Zero-size and missing file detection
- Configuration validation
- ECG loading
- R-peak detection
- rPPG10Session population
- DatasetReadinessReport
- Blocking behavior when config is incomplete
"""

import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from p11_validation.rppg10_adapter import (
    rPPG10Config,
    rPPG10Session,
    RecordingFileSet,
    FileStatus,
    discover_subjects,
    discover_recording,
    discover_all,
    load_ecg,
    detect_r_peaks,
    ecg_to_hr,
    ecg_to_ibi,
    load_session,
    process_ecg_session,
    session_to_validation_dataset,
    check_readiness,
    DatasetReadinessReport,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

DATASET_ROOT = "Dataset_rPPG-10"


@pytest.fixture
def cfg_minimal() -> rPPG10Config:
    """Config with only the verified video params set."""
    return rPPG10Config(
        dataset_root=DATASET_ROOT,
        video_fps=30.0,
    )


@pytest.fixture
def cfg_complete() -> rPPG10Config:
    """Config with all required fields set, including verified sync offset."""
    return rPPG10Config(
        dataset_root=DATASET_ROOT,
        video_fps=30.0,
        ecg_fs=1000.0,
        ecg_offset_sec=0.0,
        ecg_offset_known=True,
        video_offset_sec=0.0,
        ecg_units="raw_adc",
    )


@pytest.fixture
def cfg_no_offset_verified() -> rPPG10Config:
    """Config with ecg_fs set but ecg_offset_known=False (ECG-internal only)."""
    return rPPG10Config(
        dataset_root=DATASET_ROOT,
        video_fps=30.0,
        ecg_fs=1000.0,
        ecg_offset_sec=0.0,      # Default; offset is unverified
        ecg_offset_known=False,  # NOT verified — cross-modal blocked
        video_offset_sec=0.0,
    )


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

class TestFileDiscovery:
    """Test file discovery across the dataset."""

    def test_discovers_all_27_subjects(self, cfg_minimal):
        """All 27 subject directories are found."""
        subjects = discover_subjects(cfg_minimal.dataset_root)
        assert len(subjects) == 27
        assert set(subjects) == {str(i) for i in range(1, 28)}

    def test_discovers_subject_4(self, cfg_minimal):
        """Subject_4 is found (video is zero-size but dir exists)."""
        subjects = discover_subjects(cfg_minimal.dataset_root)
        assert "4" in subjects

    def test_all_cameras_present_for_s1(self, cfg_minimal):
        """Subject_1 has all 3 cameras and ECG."""
        files = discover_recording("1", cfg_minimal.dataset_root, cfg_minimal)
        assert files.forehead == FileStatus.PRESENT
        assert files.cheek1 == FileStatus.PRESENT
        assert files.cheek2 == FileStatus.PRESENT
        assert files.ecg == FileStatus.PRESENT
        assert files.has_complete_video
        assert files.status_summary.startswith("complete_video")

    def test_subject_4_zero_size_detected(self, cfg_minimal):
        """Subject_4 video files are correctly identified as zero-size."""
        files = discover_recording("4", cfg_minimal.dataset_root, cfg_minimal)
        assert files.forehead == FileStatus.ZERO_SIZE
        assert files.cheek1 == FileStatus.ZERO_SIZE
        assert files.cheek2 == FileStatus.ZERO_SIZE
        assert files.ecg == FileStatus.PRESENT  # ECG is intact
        assert not files.has_complete_video
        assert files.has_zero_video  # All zero-size
        assert not files.has_any_video  # No non-zero cameras

    def test_subject_4_ecg_intact(self, cfg_minimal):
        """Subject_4 ECG is present and usable even though video is lost."""
        files = discover_recording("4", cfg_minimal.dataset_root, cfg_minimal)
        assert files.ecg == FileStatus.PRESENT
        assert files.ecg_path.endswith("Subject_4_ECG.npy")

    def test_discover_all_returns_all_27(self, cfg_minimal):
        """discover_all returns 27 RecordingFileSets."""
        results = discover_all(cfg_minimal.dataset_root, cfg_minimal)
        assert len(results) == 27
        assert all(isinstance(v, RecordingFileSet) for v in results.values())

    def test_video_metadata_probe(self, cfg_minimal):
        """Video metadata is populated from the probe."""
        files = discover_recording("1", cfg_minimal.dataset_root, cfg_minimal)
        assert files.video_frame_count == 18000
        assert files.video_fps == 30.0
        assert files.video_duration_sec is not None
        assert 599.0 < files.video_duration_sec < 601.0  # ~600s

    def test_subject_13_partial_frames(self, cfg_minimal):
        """Subject_13 has 17996 frames (4 missing)."""
        files = discover_recording("13", cfg_minimal.dataset_root, cfg_minimal)
        assert files.video_frame_count == 17996
        assert files.video_fps == 30.0

    def test_invalid_subject_id_returns_missing(self, cfg_minimal):
        """Non-existent subject has all files missing."""
        files = discover_recording("99", cfg_minimal.dataset_root, cfg_minimal)
        assert files.forehead == FileStatus.MISSING
        assert files.cheek1 == FileStatus.MISSING
        assert files.cheek2 == FileStatus.MISSING
        assert files.ecg == FileStatus.MISSING
        assert not files.has_complete_video

    def test_ecg_nominal_duration_propagates(self, cfg_complete):
        """ecg_nominal_duration_sec is computed when ecg_fs is set."""
        files = discover_recording("1", cfg_complete.dataset_root, cfg_complete)
        assert files.ecg_nominal_duration_sec == 600.0  # 600000 / 1000


# ---------------------------------------------------------------------------
# Configuration validation
# ---------------------------------------------------------------------------

class TestConfigValidation:
    """Test rPPG10Config validation."""

    def test_valid_config_returns_empty_issues(self, cfg_complete):
        """Complete config passes validation and cross-modal readiness."""
        assert cfg_complete.validate() == []
        assert cfg_complete.is_ready_for_metrics is True
        assert cfg_complete.is_ready_for_cross_modal is True
        assert cfg_complete.is_ready_for_ecg_processing is True

    def test_default_ecg_fs_is_1000(self):
        """rPPG10Config defaults to documented ecg_fs=1000 Hz."""
        cfg = rPPG10Config(dataset_root=DATASET_ROOT)
        assert cfg.ecg_fs == 1000.0

    def test_ecg_fs_must_be_positive(self):
        """Zero or negative ecg_fs is rejected."""
        cfg = rPPG10Config(dataset_root=DATASET_ROOT, ecg_fs=0.0)
        issues = cfg.validate()
        assert any("positive" in i for i in issues)

    def test_ecg_offset_known_required_for_cross_modal(self):
        """ecg_offset_known=False blocks cross-modal readiness."""
        cfg = rPPG10Config(
            dataset_root=DATASET_ROOT,
            ecg_fs=1000.0,
            ecg_offset_known=False,
        )
        assert cfg.is_ready_for_ecg_processing is True
        assert cfg.is_ready_for_cross_modal is False
        assert cfg.is_ready_for_metrics is False

    def test_ecg_offset_known_enables_cross_modal(self):
        """ecg_offset_known=True enables cross-modal readiness."""
        cfg = rPPG10Config(
            dataset_root=DATASET_ROOT,
            ecg_fs=1000.0,
            ecg_offset_known=True,
        )
        assert cfg.is_ready_for_ecg_processing is True
        assert cfg.is_ready_for_cross_modal is True
        assert cfg.is_ready_for_metrics is True

    def test_unknown_camera_rejected(self):
        """Unknown camera name is rejected."""
        cfg = rPPG10Config(dataset_root=DATASET_ROOT, video_camera="Nose")
        issues = cfg.validate()
        assert any("video_camera" in i for i in issues)

    def test_window_too_large_rejected(self):
        """hr_window_sec > 600 is rejected."""
        cfg = rPPG10Config(dataset_root=DATASET_ROOT, hr_window_sec=700.0)
        issues = cfg.validate()
        assert any("hr_window" in i for i in issues)


# ---------------------------------------------------------------------------
# ECG loading
# ---------------------------------------------------------------------------

class TestECGLoading:
    """Test ECG NPY loading."""

    def test_load_ecg_s1(self, cfg_complete):
        """Subject_1 ECG loads correctly."""
        path = os.path.join(DATASET_ROOT, "Subject_1", "Subject_1_ECG.npy")
        ecg = load_ecg(path)
        assert ecg.shape == (600000,)
        assert ecg.dtype == np.float64
        assert np.isfinite(ecg).all()
        assert ecg.min() >= 0
        assert ecg.max() <= 1024

    def test_load_ecg_s4_intact(self, cfg_complete):
        """Subject_4 ECG is intact even though video is lost."""
        path = os.path.join(DATASET_ROOT, "Subject_4", "Subject_4_ECG.npy")
        ecg = load_ecg(path)
        assert ecg.shape == (600000,)
        assert np.isfinite(ecg).all()

    def test_load_ecg_raises_on_missing(self):
        """Missing ECG raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_ecg(os.path.join(DATASET_ROOT, "Subject_99", "Subject_99_ECG.npy"))

    def test_load_ecg_with_max_samples(self, cfg_complete):
        """max_samples truncates the array."""
        path = os.path.join(DATASET_ROOT, "Subject_1", "Subject_1_ECG.npy")
        ecg = load_ecg(path, max_samples=1000)
        assert len(ecg) == 1000


# ---------------------------------------------------------------------------
# R-peak detection
# ---------------------------------------------------------------------------

class TestRPeakDetection:
    """Test R-peak detection and HR extraction from synthetic ECG."""

    def _synthetic_ecg(self, fs: float, hr_bpm: float, duration_sec: float) -> np.ndarray:
        """
        Generate a synthetic ECG with realistic QRS morphology.

        Uses a clean R-peak spike embedded in low-frequency baseline
        and physiological noise. The QRS complex is modelled as a high-frequency
        impulse (dominant energy at 10-20 Hz) distinct from the HR band
        (0.67-3.33 Hz) used for filtering R-peaks.
        """
        n = int(fs * duration_sec)
        t = np.arange(n) / fs
        beat_period = 60.0 / hr_bpm  # seconds per beat

        signal = np.zeros(n, dtype=np.float64)

        # Baseline wander (low frequency)
        baseline = 0.5 * np.sin(2 * np.pi * 0.1 * t)
        signal += baseline

        # QRS complex: high-frequency sharp spike at each R-peak
        for k in range(int(duration_sec / beat_period) + 1):
            r_peak_t = k * beat_period
            r_peak_sample = int(r_peak_t * fs)
            if r_peak_sample >= n:
                break
            # R-peak: narrow positive spike (QRS energy in 10-20 Hz range)
            spike_width = max(int(0.015 * fs), 3)  # ~15ms
            for j in range(max(0, r_peak_sample - spike_width),
                           min(n, r_peak_sample + spike_width + 1)):
                signal[j] += np.exp(-((j - r_peak_sample) / (spike_width / 3)) ** 2) * 2.0

            # S-wave: small negative deflection
            s_peak_sample = int((r_peak_t + 0.04) * fs)
            if s_peak_sample < n:
                sw = max(int(0.01 * fs), 2)
                for j in range(max(0, s_peak_sample - sw), min(n, s_peak_sample + sw + 1)):
                    signal[j] -= np.exp(-((j - s_peak_sample) / (sw / 2)) ** 2) * 0.8

            # T-wave: broad positive deflection after R-peak
            t_peak_t = r_peak_t + 0.25
            t_peak_sample = int(t_peak_t * fs)
            if t_peak_sample < n:
                tw = int(0.12 * fs)
                for j in range(max(0, t_peak_sample - tw), min(n, t_peak_sample + tw + 1)):
                    signal[j] += np.exp(-((j - t_peak_sample) / (tw / 3)) ** 2) * 0.4

        # Physiological noise: respiratory modulation at ~0.3 Hz
        signal += 0.15 * np.sin(2 * np.pi * 0.3 * t)
        # EMG-like high-frequency noise
        np.random.seed(42 + int(hr_bpm))
        signal += np.random.normal(0, 0.08, n)

        return signal.astype(np.float64)

    def test_detect_r_peaks_finds_beats(self):
        """R-peak detection finds beats in synthetic ECG at known HR."""
        fs = 1000.0
        hr_bpm = 60.0
        ecg = self._synthetic_ecg(fs, hr_bpm, duration_sec=30.0)
        peaks = detect_r_peaks(
            ecg, fs,
            min_hz=40/60,
            max_hz=200/60,
            height_percentile=50.0,
        )
        # At 60 BPM for 30s, expect ~30 beats
        assert len(peaks) >= 25
        assert len(peaks) <= 35

    def test_detect_r_peaks_high_hr(self):
        """R-peak detection works at elevated HR."""
        fs = 1000.0
        hr_bpm = 120.0
        ecg = self._synthetic_ecg(fs, hr_bpm, duration_sec=10.0)
        peaks = detect_r_peaks(
            ecg, fs,
            min_hz=40/60,
            max_hz=200/60,
        )
        # At 120 BPM for 10s, expect ~20 beats
        assert len(peaks) >= 15
        assert len(peaks) <= 25

    def test_ecg_to_hr_output_shape(self):
        """ecg_to_hr returns arrays of consistent length."""
        fs = 1000.0
        hr_bpm = 72.0
        ecg = self._synthetic_ecg(fs, hr_bpm, duration_sec=60.0)
        t, hr, peaks = ecg_to_hr(
            ecg, fs,
            window_sec=10.0,
            step_sec=1.0,
            min_hz=40/60,
            max_hz=200/60,
        )
        assert len(t) == len(hr)
        assert len(t) == len(peaks)
        # 60s window at 1s step: expect ~50 windows
        assert 45 <= len(t) <= 60

    def test_ecg_to_hr_within_range(self):
        """ecg_to_hr produces HR values in plausible range."""
        fs = 1000.0
        ecg = self._synthetic_ecg(fs, hr_bpm=75.0, duration_sec=30.0)
        t, hr, _ = ecg_to_hr(
            ecg, fs,
            window_sec=10.0,
            step_sec=1.0,
            min_hz=40/60,
            max_hz=200/60,
        )
        valid = hr[~np.isnan(hr)]
        assert valid.min() >= 30  # Some tolerance due to window edge effects
        assert valid.max() <= 120

    def test_ecg_to_ibi_output(self):
        """ecg_to_ibi returns timestamp and IBI arrays."""
        fs = 1000.0
        ecg = self._synthetic_ecg(fs, hr_bpm=70.0, duration_sec=20.0)
        t, ibi = ecg_to_ibi(ecg, fs, min_hz=40/60, max_hz=200/60)
        assert len(t) == len(ibi)
        assert (ibi >= 300).all()  # All IBIs > 300ms
        assert (ibi <= 2000).all()  # All IBIs < 2000ms


# ---------------------------------------------------------------------------
# rPPG10Session loading
# ---------------------------------------------------------------------------

class TestSessionLoading:
    """Test rPPG10Session creation and processing."""

    def test_session_s1_usable(self, cfg_complete):
        """Subject_1 is marked as usable."""
        session = load_session("1", cfg_complete)
        assert session.is_usable
        assert session.files.has_complete_video
        assert session.files.ecg == FileStatus.PRESENT
        assert session.video_frame_count == 18000
        assert session.ecg_samples == 600000
        assert session.video_fps == 30.0

    def test_session_s4_not_usable(self, cfg_complete):
        """Subject_4 is NOT usable due to zero-size video."""
        session = load_session("4", cfg_complete)
        assert not session.is_usable
        assert session.files.forehead == FileStatus.ZERO_SIZE
        assert "Missing video cameras" in session.issues[0]

    def test_session_s4_ecg_still_loadable(self, cfg_complete):
        """Subject_4 ECG is loadable even though video is lost."""
        session = load_session("4", cfg_complete)
        assert session.ecg_path.endswith("Subject_4_ECG.npy")
        assert os.path.exists(session.ecg_path)

    def test_session_with_video_path(self, cfg_complete):
        """Session.video_path is set for usable subjects."""
        session = load_session("1", cfg_complete)
        assert session.video_path.endswith("Subject_1_Forehead_.avi")
        assert os.path.exists(session.video_path)

    def test_session_ecg_nominal_duration(self, cfg_complete):
        """ECG nominal duration is computed when ecg_fs is set."""
        session = load_session("1", cfg_complete)
        assert session.ecg_nominal_duration_sec == 600.0

    def test_session_blocks_cross_modal_without_offset(self, cfg_no_offset_verified):
        """Session files are fine but config blocks is_ready_for_validation (offset unknown)."""
        session = load_session("1", cfg_no_offset_verified)
        assert session.is_usable  # Files are fine
        assert not session.is_ready_for_validation(cfg_no_offset_verified)  # Offset unknown


# ---------------------------------------------------------------------------
# ECG processing
# ---------------------------------------------------------------------------

class TestECGProcessing:
    """Test ECG processing into HR and IBI sequences."""

    def test_process_ecg_proceeds_without_offset_known(self, cfg_no_offset_verified):
        """process_ecg_session succeeds when ecg_fs is set but offset is unverified."""
        session = load_session("1", cfg_no_offset_verified)
        process_ecg_session(session, cfg_no_offset_verified)
        assert len(session.hr_ref) > 0

    def test_process_ecg_unknown_offset_uses_native_timestamps(self, cfg_no_offset_verified):
        """When ecg_offset_known=False, timestamps remain ECG-native (no shift applied)."""
        cfg = cfg_no_offset_verified
        session = load_session("1", cfg)
        process_ecg_session(session, cfg)
        if len(session.hr_ref_timestamps) > 0:
            # First timestamp is near 0 (ECG-native, not shifted)
            assert session.hr_ref_timestamps[0] < 5.0

    def test_process_ecg_produces_ref_hr(self, cfg_complete):
        """process_ecg_session populates ref_hr from ECG."""
        session = load_session("1", cfg_complete)
        process_ecg_session(session, cfg_complete)

        assert len(session.hr_ref) > 0
        assert len(session.hr_ref_timestamps) > 0
        assert len(session.hr_ref) == len(session.hr_ref_timestamps)
        # HR values should be in physiological range (with tolerance)
        valid = session.hr_ref[(session.hr_ref >= 30) & (session.hr_ref <= 220)]
        assert len(valid) > 0

    def test_process_ecg_known_offset_applies_shift(self):
        """When ecg_offset_known=True, the offset is applied to timestamps."""
        cfg = rPPG10Config(
            dataset_root=DATASET_ROOT,
            ecg_fs=1000.0,
            ecg_offset_sec=5.0,
            ecg_offset_known=True,
            video_offset_sec=0.0,
        )
        session = load_session("1", cfg)
        process_ecg_session(session, cfg)

        if len(session.hr_ref_timestamps) > 0:
            # Timestamps should be shifted by 5 seconds
            assert session.hr_ref_timestamps[0] >= 5.0

    def test_process_ecg_produces_ibi(self, cfg_complete):
        """process_ecg_session populates ref_ibi from ECG."""
        session = load_session("1", cfg_complete)
        process_ecg_session(session, cfg_complete)

        if len(session.ibi_ref) > 0:
            assert len(session.ibi_ref_timestamps) == len(session.ibi_ref)
            assert (session.ibi_ref >= 300).all()
            assert (session.ibi_ref <= 2000).all()


# ---------------------------------------------------------------------------
# ValidationDataset conversion
# ---------------------------------------------------------------------------

class TestValidationDatasetConversion:
    """Test conversion from rPPG10Session to ValidationDataset."""

    def test_blocks_without_offset_known(self, cfg_no_offset_verified):
        """session_to_validation_dataset raises when ecg_offset_known is False."""
        session = load_session("1", cfg_no_offset_verified)
        process_ecg_session(session, cfg_no_offset_verified)
        with pytest.raises(ValueError, match="ecg_offset_known"):
            session_to_validation_dataset(session, cfg_no_offset_verified)

    def test_ecg_only_builds_without_offset_known(self, cfg_no_offset_verified):
        """session_to_validation_dataset(ecg_only=True) succeeds without verified offset."""
        session = load_session("1", cfg_no_offset_verified)
        process_ecg_session(session, cfg_no_offset_verified)
        dataset = session_to_validation_dataset(session, cfg_no_offset_verified, ecg_only=True)
        assert len(dataset.ref_hr) > 0
        assert dataset.ref_source == "ecg"

    def test_produces_ref_hr_fields(self, cfg_complete):
        """ValidationDataset has ref_hr and ref_timestamps."""
        session = load_session("1", cfg_complete)
        process_ecg_session(session, cfg_complete)
        dataset = session_to_validation_dataset(session, cfg_complete)

        assert dataset.session_id == "S01"
        assert dataset.subject_id == "1"
        assert len(dataset.ref_hr) > 0
        assert len(dataset.ref_timestamps) > 0
        assert len(dataset.ref_hr) == len(dataset.ref_timestamps)
        assert dataset.ref_source == "ecg"
        assert dataset.ref_ibi_source == "ecg"


# ---------------------------------------------------------------------------
# Readiness report
# ---------------------------------------------------------------------------

class TestReadinessReport:
    """Test DatasetReadinessReport."""

    def test_report_counts(self, cfg_complete):
        """Report counts match expected values."""
        report = check_readiness(DATASET_ROOT, cfg_complete)
        assert isinstance(report, DatasetReadinessReport)
        assert report.n_subjects_total == 27
        # All except S04 are usable (S04 has zero-size video)
        assert report.n_subjects_usable == 26
        assert "4" in report.unusable_subjects
        assert "4" not in report.usable_subjects

    def test_report_with_default_config_has_valid_fs(self):
        """Default config (ecg_fs=1000.0) passes config validation."""
        cfg = rPPG10Config(dataset_root=DATASET_ROOT)
        report = check_readiness(DATASET_ROOT, cfg)
        # ecg_fs is set (1000.0) but ecg_offset_known=False
        assert cfg.is_ready_for_ecg_processing is True
        assert cfg.is_ready_for_cross_modal is False
        # config_is_valid reflects is_ready_for_metrics (cross_modal)
        assert report.config_is_valid is False

    def test_report_without_offset_known_blocks_cross_modal(self):
        """Config with ecg_offset_known=False is not ready for cross-modal metrics."""
        cfg = rPPG10Config(
            dataset_root=DATASET_ROOT,
            ecg_fs=1000.0,
            ecg_offset_known=False,
        )
        report = check_readiness(DATASET_ROOT, cfg)
        # Config passes basic validation (fs is set)
        assert cfg.is_ready_for_ecg_processing is True
        # But is_ready_for_cross_modal is False (offset unknown)
        assert cfg.is_ready_for_cross_modal is False

    def test_report_includes_all_subjects(self, cfg_complete):
        """All 27 subjects appear in the report."""
        report = check_readiness(DATASET_ROOT, cfg_complete)
        all_ids = set(report.usable_subjects) | set(report.partial_subjects) | set(report.unusable_subjects)
        assert len(all_ids) == 27


# ---------------------------------------------------------------------------
# Blocking behavior
# ---------------------------------------------------------------------------

class TestBlockingBehavior:
    """Test that the adapter blocks metric computation without required config."""

    def test_default_ecg_fs_enables_ecg_processing(self):
        """Default config (ecg_fs=1000.0) enables ECG-internal processing."""
        cfg = rPPG10Config(dataset_root=DATASET_ROOT)
        assert cfg.is_ready_for_ecg_processing is True
        assert cfg.is_ready_for_cross_modal is False  # offset unknown

    def test_zero_ecg_fs_blocks_ecg_processing(self):
        """ecg_fs=0.0 blocks ECG-internal processing."""
        cfg = rPPG10Config(dataset_root=DATASET_ROOT, ecg_fs=0.0)
        assert cfg.is_ready_for_ecg_processing is False

    def test_session_blocks_cross_modal_without_offset_known(self, cfg_no_offset_verified):
        """Session.is_ready_for_validation is False when offset is unverified."""
        session = load_session("1", cfg_no_offset_verified)
        assert session.is_ready_for_validation(cfg_no_offset_verified) is False

    def test_session_ecg_processing_available_without_offset_known(self, cfg_no_offset_verified):
        """Session ECG data is loadable and processable without verified offset."""
        session = load_session("1", cfg_no_offset_verified)
        assert session.is_usable is True  # Files are fine
        # ECG-internal processing should work
        process_ecg_session(session, cfg_no_offset_verified)
        assert len(session.hr_ref) > 0

    def test_synthetic_fixture_still_synthetic(self):
        """create_synthetic_fixture from io.py still produces synthetic data."""
        from p11_validation.io import create_synthetic_fixture
        fixture = create_synthetic_fixture(n_samples=10)
        assert fixture.ref_source == "synthetic"
        assert fixture.session_id == "synthetic_fixture"


# ---------------------------------------------------------------------------
# Self-contained runner
# ---------------------------------------------------------------------------

def run_all_tests():
    """Run all tests without pytest."""
    test_classes = [
        TestFileDiscovery,
        TestConfigValidation,
        TestECGLoading,
        TestRPeakDetection,
        TestSessionLoading,
        TestECGProcessing,
        TestValidationDatasetConversion,
        TestReadinessReport,
        TestBlockingBehavior,
    ]
    total_passed = 0
    total_failed = 0

    for cls in test_classes:
        print(f"\n{cls.__name__}")
        instance = cls()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    # Supply fixtures manually
                    kwargs = {}
                    if "cfg_complete" in method_name:
                        kwargs = {"cfg_complete": cfg_complete_fixture()}
                    elif "cfg_minimal" in method_name:
                        kwargs = {"cfg_minimal": cfg_minimal_fixture()}
                    elif "cfg_no_offset_verified" in method_name:
                        kwargs = {"cfg_no_offset_verified": cfg_no_offset_verified_fixture()}
                    getattr(instance, method_name)(**kwargs)
                    print(f"  {method_name}... PASS")
                    total_passed += 1
                except Exception as e:
                    print(f"  {method_name}... FAIL: {e}")
                    total_failed += 1

    print(f"\n{'='*50}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    return total_failed == 0


def cfg_complete_fixture():
    return rPPG10Config(
        dataset_root="Dataset_rPPG-10",
        video_fps=30.0,
        ecg_fs=1000.0,
        ecg_offset_sec=0.0,
        ecg_offset_known=True,
        video_offset_sec=0.0,
    )

def cfg_minimal_fixture():
    return rPPG10Config(
        dataset_root="Dataset_rPPG-10",
        video_fps=30.0,
    )

def cfg_no_offset_verified_fixture():
    return rPPG10Config(
        dataset_root="Dataset_rPPG-10",
        video_fps=30.0,
        ecg_fs=1000.0,
        ecg_offset_sec=0.0,
        ecg_offset_known=False,
        video_offset_sec=0.0,
    )


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
