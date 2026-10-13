"""
Phase 11 Validation Tests

Tests for multi-sensor validation pipeline.
"""

import pytest
import numpy as np
import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from p11_validation import (
    # Base
    Modality, HRVMetricType, ValidationStatus, ExclusionReason,
    ValidationResult, ValidationConfig, SyncConfig,
    create_hr_record, create_rr_record, create_hrv_record, create_ibi_record,
    validate_hr_value, validate_rr_value, validate_ibi_value,
    # Sync
    Synchronizer, align_observations, compute_time_delta, validate_timestamp_sequence,
    # Metrics
    compute_mae_rmse, compute_bland_altman, compute_hr_metrics,
    compute_sdnn, compute_rmssd, compute_pnn50, compute_hrv_metrics,
    # Alignment
    PairingPolicy, align_modalities, find_nearest_match, validate_pairing,
    # Failure
    ExclusionTracker, record_exclusion, get_exclusion_summary,
    track_missing_data, track_sync_failure, track_quality_failure,
    # IO
    ValidationDataset, load_validation_dataset, save_validation_results,
    create_synthetic_fixture, validate_dataset, import_reference_csv,
    ValidationLoadError, ValidationExportError,
    # Pipeline
    ValidationPipeline, run_hr_validation, run_rr_validation, run_hrv_validation,
    run_full_validation, generate_validation_report,
)


# ---------------------------------------------------------------------------
# Sync Config
# ---------------------------------------------------------------------------

class TestSyncConfig:
    """Test synchronization configuration."""

    def test_sync_config_defaults(self):
        """Verify sync config defaults."""
        config = SyncConfig()
        assert config.tolerance_sec == 2.0
        assert config.use_drift_correction is False

    def test_custom_tolerance(self):
        """Test custom tolerance."""
        config = SyncConfig(tolerance_sec=5.0)
        assert config.tolerance_sec == 5.0


# ---------------------------------------------------------------------------
# Pairing
# ---------------------------------------------------------------------------

class TestPairing:
    """Test pairing policies."""

    def test_nearest_policy(self):
        """Test nearest pairing policy."""
        est_ts = [1.0, 2.0, 3.0]
        est_vals = [70.0, 72.0, 74.0]
        ref_ts = [1.1, 2.9]
        ref_vals = [71.0, 73.0]

        aligned_est, aligned_ref, diag = align_modalities(
            est_ts, est_vals, ref_ts, ref_vals,
            tolerance=1.0,
            policy=PairingPolicy.NEAREST,
        )

        assert len(aligned_est) == 3
        assert diag["n_matched"] >= 2

    def test_find_nearest_match(self):
        """Test find_nearest_match function."""
        ref_ts = [1.0, 2.0, 3.0]
        idx, ts, delta = find_nearest_match(2.1, ref_ts, tolerance=0.5)
        assert idx == 1
        assert abs(delta - 0.1) < 0.01


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

class TestMetrics:
    """Test metric calculations."""

    def test_mae_rmse(self):
        """Test MAE/RMSE computation."""
        estimates = np.array([72.0, 74.0, 70.0])
        references = np.array([70.0, 72.0, 72.0])

        metrics = compute_mae_rmse(estimates, references)

        assert "mae" in metrics
        assert "rmse" in metrics
        assert metrics["mae"] == pytest.approx(2.0)
        # RMSE = sqrt(mean([4, 4, 4]) = 2.0
        assert metrics["rmse"] == pytest.approx(2.0)

    def test_mae_rmse_empty(self):
        """MAE/RMSE returns NaN for empty inputs."""
        m = compute_mae_rmse([], [])
        assert np.isnan(m["mae"])
        assert np.isnan(m["rmse"])

    def test_mae_rmse_mismatch(self):
        """MAE/RMSE returns NaN for mismatched lengths."""
        m = compute_mae_rmse([1, 2], [1])
        assert np.isnan(m["mae"])
        assert np.isnan(m["rmse"])

    def test_bland_altman(self):
        """Test Bland-Altman computation."""
        estimates = np.array([72.0, 74.0, 70.0, 76.0, 68.0])
        references = np.array([70.0, 72.0, 72.0, 74.0, 70.0])

        ba = compute_bland_altman(estimates, references)

        assert "mean_diff" in ba
        assert "loa_upper" in ba
        assert "loa_lower" in ba
        assert ba["n"] == 5

        # Verify LoA formula: loa = mean ± 1.96 * std
        diffs = estimates - references
        mean_diff = float(np.mean(diffs))
        std_diff  = float(np.std(diffs, ddof=1))
        assert ba["mean_diff"] == pytest.approx(mean_diff)
        assert ba["std_diff"]  == pytest.approx(std_diff)
        assert ba["loa_upper"] == pytest.approx(mean_diff + 1.96 * std_diff)
        assert ba["loa_lower"] == pytest.approx(mean_diff - 1.96 * std_diff)

    def test_bland_altman_insufficient(self):
        """Bland-Altman returns NaN for n < 3."""
        ba = compute_bland_altman([1.0], [1.0])
        assert np.isnan(ba["mean_diff"])
        assert np.isnan(ba["loa_upper"])

    def test_sdnn(self):
        """Test SDNN computation."""
        ibi = np.array([800.0, 820.0, 780.0, 810.0, 790.0])
        sdnn = compute_sdnn(ibi)
        assert sdnn is not None
        assert sdnn > 0

    def test_sdnn_filtering(self):
        """SDNN filters physiologically implausible IBI values."""
        ibi = np.array([250.0, 800.0, 820.0, 2100.0, 780.0])
        sdnn = compute_sdnn(ibi)
        # 250 and 2100 ms are filtered; result from [800, 820, 780]
        ibi_f = np.array([800.0, 820.0, 780.0])
        assert sdnn == pytest.approx(float(np.std(ibi_f, ddof=1)))

    def test_sdnn_insufficient(self):
        """SDNN returns None for fewer than 2 valid IBI."""
        assert compute_sdnn(np.array([])) is None
        assert compute_sdnn(np.array([800.0])) is None
        # All implausible
        assert compute_sdnn(np.array([250.0, 2100.0])) is None

    def test_rmssd(self):
        """Test RMSSD computation."""
        ibi = np.array([800.0, 820.0, 780.0, 810.0, 790.0])
        rmssd = compute_rmssd(ibi)
        assert rmssd is not None
        assert rmssd >= 0

    def test_rmssd_insufficient(self):
        """RMSSD returns None for fewer than 2 valid IBI."""
        assert compute_rmssd(np.array([])) is None
        assert compute_rmssd(np.array([800.0])) is None

    def test_pnn50(self):
        """Test pNN50 computation."""
        ibi = np.array([800.0, 850.0, 780.0, 900.0, 790.0])
        pnn50 = compute_pnn50(ibi)
        # diffs: 50, 70, 120, 110 -> 3 out of 4 exceed 50 ms
        assert pnn50 is not None
        assert pnn50 == pytest.approx(75.0)

    def test_pnn50_no_exceedances(self):
        """pNN50 is 0 when no successive difference exceeds 50 ms."""
        ibi = np.array([800.0, 820.0, 780.0, 810.0, 790.0])  # max diff < 50
        pnn = compute_pnn50(ibi)
        assert pnn == pytest.approx(0.0)

    def test_pnn50_insufficient(self):
        """pNN50 returns None for fewer than 2 IBI values."""
        assert compute_pnn50(np.array([])) is None
        assert compute_pnn50(np.array([800.0])) is None

    def test_hr_metrics(self):
        """Test HR metrics computation from ValidationResult list."""
        results = [
            ValidationResult(
                status=ValidationStatus.VALID,
                modality=Modality.CAMERA,
                estimate=72.0,
                reference=70.0,
            ),
            ValidationResult(
                status=ValidationStatus.VALID,
                modality=Modality.CAMERA,
                estimate=74.0,
                reference=72.0,
            ),
        ]

        metrics = compute_hr_metrics(results, hr_range=(40.0, 200.0))
        assert metrics["n_valid"] == 2
        assert "mae" in metrics
        assert "bias" in metrics
        assert "std_error" in metrics

    def test_hr_metrics_excludes_out_of_range(self):
        """HR metrics excludes estimates/references outside the valid range."""
        results = [
            ValidationResult(status=ValidationStatus.VALID,
                            estimate=300.0, reference=70.0),  # out of range
            ValidationResult(status=ValidationStatus.VALID,
                            estimate=72.0, reference=70.0),
        ]
        metrics = compute_hr_metrics(results, hr_range=(40.0, 200.0))
        assert metrics["n_valid"] == 1
        assert metrics["n_excluded"] == 1

    def test_hr_metrics_empty(self):
        """HR metrics handles empty result list."""
        m = compute_hr_metrics([], hr_range=(40.0, 200.0))
        assert m["n_valid"] == 0
        assert np.isnan(m["mae"])


# ---------------------------------------------------------------------------
# HRV Metrics
# ---------------------------------------------------------------------------

class TestHRVMetrics:
    """Test HRV metric computation."""

    def test_compute_hrv_metrics_full(self):
        """Test compute_hrv_metrics returns all expected fields."""
        np.random.seed(42)
        ibi_est = np.random.normal(800.0, 20.0, 30)
        ibi_ref = ibi_est + np.random.normal(0.0, 5.0, 30)

        result = compute_hrv_metrics(ibi_est, ibi_ref, min_ibi_count=10)

        assert result["valid"] is True
        assert "sdnn_est" in result
        assert "sdnn_ref" in result
        assert "rmssd_est" in result
        assert "rmssd_ref" in result
        assert "pnn50_est" in result
        assert "pnn50_ref" in result
        assert result["n_est"] == 30
        assert result["n_ref"] == 30

    def test_compute_hrv_metrics_insufficient(self):
        """compute_hrv_metrics flags invalid when IBI count is too low."""
        ibi_est = np.array([800.0, 810.0, 820.0])
        ibi_ref = np.array([805.0, 815.0, 825.0])

        result = compute_hrv_metrics(ibi_est, ibi_ref, min_ibi_count=10)
        assert result["valid"] is False
        assert result["n_est"] == 3

    def test_compute_hrv_metrics_implausible_filtered(self):
        """compute_hrv_metrics filters implausible IBI values."""
        ibi_est = np.array([250.0, 800.0, 820.0, 2100.0, 780.0])
        ibi_ref = np.array([260.0, 810.0, 830.0, 2050.0, 790.0])

        result = compute_hrv_metrics(ibi_est, ibi_ref, min_ibi_count=2)
        # 250 and 2100 filtered; 3 valid remain
        assert result["n_est"] == 3
        assert result["n_ref"] == 3


# ---------------------------------------------------------------------------
# Failure Tracking
# ---------------------------------------------------------------------------

class TestFailureTracking:
    """Test failure tracking."""

    def test_exclusion_tracker(self):
        """Test exclusion tracker."""
        tracker = ExclusionTracker()

        tracker.record(ExclusionReason.LOW_SQI, 1.0, "SQI below threshold")
        tracker.record(ExclusionReason.SYNC_TOLERANCE, 2.0, "Tolerance exceeded")

        summary = tracker.get_summary()
        assert summary["total_recorded"] == 2
        assert summary["total_excluded"] == 2

    def test_track_sync_failure(self):
        """Test sync failure tracking."""
        tracker = ExclusionTracker()
        track_sync_failure(tracker, delta_sec=5.0, tolerance_sec=2.0, timestamp=1.0)

        summary = tracker.get_summary()
        assert summary["total_recorded"] == 1

    def test_track_quality_failure(self):
        """Test quality failure tracking."""
        tracker = ExclusionTracker()
        track_quality_failure(tracker, sqi=0.2, threshold=0.3)

        summary = tracker.get_summary()
        assert summary["total_recorded"] == 1


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

class TestIO:
    """Test data import/export."""

    def test_create_synthetic_fixture(self):
        """Test synthetic fixture creation."""
        fixture = create_synthetic_fixture(
            n_samples=50,
            hr_mean=70.0,
            error_mean=0.0,
            error_std=1.0,
        )

        assert len(fixture.camera_hr) == 50
        assert len(fixture.ref_hr) == 50
        assert fixture.ref_source == "synthetic"

    def test_synthetic_fixture_alignment(self):
        """Test synthetic fixture has aligned timestamps."""
        fixture = create_synthetic_fixture(n_samples=10)

        # Timestamps should match
        assert fixture.camera_timestamps == fixture.ref_timestamps

    def test_validate_dataset(self):
        """Test dataset validation."""
        dataset = ValidationDataset(
            session_id="test",
            camera_hr=[70.0, 72.0],
            camera_timestamps=[1.0, 2.0],
            ref_hr=[71.0, 73.0],
            ref_timestamps=[1.0, 2.0],
        )

        issues = validate_dataset(dataset)
        # Should have no issues
        assert len(issues) == 0

    def test_validate_mismatched_lengths(self):
        """Test validation detects mismatched lengths."""
        dataset = ValidationDataset(
            camera_hr=[70.0, 72.0],
            camera_timestamps=[1.0],  # Mismatched
            ref_hr=[71.0],
            ref_timestamps=[1.0],
        )

        issues = validate_dataset(dataset)
        assert any("mismatch" in i.lower() for i in issues)

    def test_validation_dataset_ibi_fields(self):
        """ValidationDataset accepts IBI fields."""
        dataset = ValidationDataset(
            session_id="ibi_test",
            camera_ibi=[800.0, 820.0, 810.0, 790.0],
            ref_ibi=[805.0, 825.0, 815.0, 795.0],
            ref_ibi_source="ecg",
        )
        assert len(dataset.camera_ibi) == 4
        assert len(dataset.ref_ibi) == 4
        assert dataset.ref_ibi_source == "ecg"

    def test_save_and_load_with_ibi(self):
        """ValidationDataset IBI fields round-trip through JSON."""
        dataset = ValidationDataset(
            session_id="roundtrip",
            camera_ibi=[800.0, 820.0, 810.0],
            ref_ibi=[805.0, 825.0, 815.0],
            ref_ibi_source="ecg",
        )

        # Serialize ValidationDataset fields directly to JSON and reload
        data = {
            "session_id": dataset.session_id,
            "camera_ibi": dataset.camera_ibi,
            "ref_ibi": dataset.ref_ibi,
            "ref_ibi_source": dataset.ref_ibi_source,
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name

        try:
            json.dump(data, open(json_path, 'w'))
            loaded = load_validation_dataset(json_path)
            assert loaded.session_id == "roundtrip"
            assert loaded.camera_ibi == [800.0, 820.0, 810.0]
            assert loaded.ref_ibi == [805.0, 825.0, 815.0]
            assert loaded.ref_ibi_source == "ecg"
        finally:
            os.unlink(json_path)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class TestPipeline:
    """Test validation pipeline."""

    def test_pipeline_initialization(self):
        """Test pipeline initializes correctly."""
        pipeline = ValidationPipeline()
        assert pipeline.config is not None
        assert pipeline._synchronizer is not None

    def test_pipeline_with_sync_config(self):
        """Pipeline accepts bare SyncConfig."""
        pipeline = ValidationPipeline(SyncConfig(tolerance_sec=5.0))
        assert pipeline._synchronizer is not None

    def test_run_hr_validation_class(self):
        """Test HR validation workflow via ValidationPipeline."""
        from p11_validation.base import HRRecord

        camera = [
            HRRecord(timestamp=1.0, hr=72.0, modality=Modality.CAMERA),
            HRRecord(timestamp=2.0, hr=74.0, modality=Modality.CAMERA),
            HRRecord(timestamp=3.0, hr=70.0, modality=Modality.CAMERA),
        ]
        reference = [
            HRRecord(timestamp=1.0, hr=70.0, modality=Modality.ECG),
            HRRecord(timestamp=2.0, hr=72.0, modality=Modality.ECG),
            HRRecord(timestamp=3.0, hr=70.0, modality=Modality.ECG),
        ]

        pipeline = ValidationPipeline(SyncConfig(tolerance_sec=1.0))
        result = pipeline.run_hr_validation(camera, reference)

        assert "metrics" in result
        assert "bland_altman" in result
        assert "n_results" in result
        assert result["n_results"] == 3
        assert result["bland_altman"]["n"] == 3

    def test_run_hr_validation_no_reference(self):
        """Test HR validation with no reference."""
        from p11_validation.base import HRRecord

        camera = [
            HRRecord(timestamp=1.0, hr=72.0, modality=Modality.CAMERA),
        ]

        pipeline = ValidationPipeline()
        result = pipeline.run_hr_validation(camera, [])

        # Should handle empty reference gracefully
        assert "metrics" in result

    def test_run_hr_validation_array_bland_altman(self):
        """run_hr_validation (array version) returns Bland-Altman fields."""
        np.random.seed(0)
        n = 20
        est  = np.random.normal(72.0, 3.0, n)
        ref  = np.array([72.0] * n)
        ts   = np.arange(n, dtype=float)

        result = run_hr_validation(est, ts, ref, ts, tolerance=10.0)

        assert "error" not in result
        assert "bland_altman" in result
        assert "n_pairs" in result
        assert "mae" in result
        assert "bias" in result
        assert "std_error" in result
        ba = result["bland_altman"]
        assert "mean_diff" in ba
        assert "loa_upper" in ba
        assert "loa_lower" in ba

    def test_run_rr_validation_array(self):
        """run_rr_validation (array version) returns MAE/RMSE."""
        np.random.seed(0)
        n = 15
        est = np.random.normal(16.0, 1.0, n)
        ref = np.array([16.0] * n)
        ts  = np.arange(n, dtype=float)

        result = run_rr_validation(est, ts, ref, ts, tolerance=10.0)

        assert "error" not in result
        assert "mae" in result
        assert "rmse" in result
        assert "bias" in result
        assert result["n_pairs"] == 15

    def test_run_hrv_validation_full(self):
        """run_hrv_validation returns all HRV metrics."""
        np.random.seed(42)
        ibi_est = np.random.normal(800.0, 20.0, 30)
        ibi_ref = ibi_est + np.random.normal(0.0, 3.0, 30)

        result = run_hrv_validation(ibi_est, ibi_ref, min_ibi_count=10)

        assert result["valid"] is True
        assert "sdnn_est" in result
        assert "sdnn_ref" in result
        assert "rmssd_est" in result
        assert "rmssd_ref" in result
        assert "pnn50_est" in result
        assert "pnn50_ref" in result
        assert "ibi_mae" in result
        assert "ibi_rmse" in result

    def test_run_hrv_validation_insufficient(self):
        """run_hrv_validation handles insufficient IBI."""
        result = run_hrv_validation(
            np.array([800.0, 810.0]),
            np.array([805.0, 815.0]),
            min_ibi_count=10,
        )
        assert result["valid"] is False
        assert result["n_est"] == 2


# ---------------------------------------------------------------------------
# Full Pipeline
# ---------------------------------------------------------------------------

class TestFullPipeline:
    """Test run_full_validation end-to-end."""

    def test_run_full_validation_hr_only(self):
        """run_full_validation processes HR data."""
        dataset = ValidationDataset(
            session_id="full_test",
            subject_id="subj_01",
            recording_date="2025-01-01",
            camera_timestamps=list(range(20)),
            camera_hr=[72.0 + i * 0.1 for i in range(20)],
            ref_timestamps=list(range(20)),
            ref_hr=[72.0] * 20,
        )

        result = run_full_validation(dataset, SyncConfig(tolerance_sec=2.0))

        assert result["session_id"] == "full_test"
        assert result["subject_id"] == "subj_01"
        assert "hr" in result
        assert "mae" in result["hr"]

    def test_run_full_validation_with_ibi(self):
        """run_full_validation computes HRV when IBI data is present."""
        dataset = ValidationDataset(
            session_id="hrv_test",
            camera_ibi=[800.0, 820.0, 810.0, 790.0, 780.0,
                        800.0, 810.0, 820.0, 830.0, 800.0,
                        810.0, 820.0, 810.0, 800.0, 790.0],
            ref_ibi=[805.0, 825.0, 815.0, 795.0, 785.0,
                      805.0, 815.0, 825.0, 835.0, 805.0,
                      815.0, 825.0, 815.0, 805.0, 795.0],
            ref_ibi_source="ecg",
        )

        result = run_full_validation(dataset)

        assert "hrv" in result
        assert "sdnn_est" in result["hrv"]
        assert result["hrv"]["n_est"] == 15

    def test_run_full_validation_sqi_summary(self):
        """run_full_validation produces SQI summary when data present."""
        dataset = ValidationDataset(
            session_id="sqi_test",
            camera_hr=[72.0, 74.0, 70.0],
            camera_timestamps=[1.0, 2.0, 3.0],
            ref_hr=[71.0, 73.0, 71.0],
            ref_timestamps=[1.0, 2.0, 3.0],
            camera_hr_sqi=[0.9, 0.5, 0.3],
        )

        result = run_full_validation(dataset)
        assert "sqi_summary" in result
        assert result["sqi_summary"]["mean"] == pytest.approx(0.5667, abs=0.01)
        assert result["sqi_summary"]["n"] == 3

    def test_run_full_validation_motion_summary(self):
        """run_full_validation produces motion summary."""
        dataset = ValidationDataset(
            session_id="motion_test",
            camera_hr=[72.0, 74.0],
            camera_timestamps=[1.0, 2.0],
            ref_hr=[71.0, 73.0],
            ref_timestamps=[1.0, 2.0],
            camera_motion_rejected=[False, True],
        )

        result = run_full_validation(dataset)
        assert "motion_summary" in result
        assert result["motion_summary"]["rejected_rate"] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

class TestReportGeneration:
    """Test validation report generation."""

    def test_generate_report_markdown(self):
        """generate_validation_report produces markdown output."""
        results = {
            "session_id": "test_session",
            "subject_id": "subj_01",
            "date": "2025-01-01",
            "hr": {
                "n_pairs": 20,
                "mae": 2.5,
                "rmse": 3.1,
                "bias": 0.5,
                "std_error": 3.1,
                "bland_altman": {
                    "mean_diff": 0.5,
                    "std_diff": 3.1,
                    "loa_upper": 6.58,
                    "loa_lower": -5.58,
                    "n": 20,
                },
            },
        }

        report = generate_validation_report(results, format="markdown")

        assert "# Validation Report" in report
        assert "test_session" in report
        assert "2.5000" in report or "2.5" in report
        assert "mean_diff" in report
        assert "loa_upper" in report

    def test_generate_report_plain(self):
        """generate_validation_report produces plain text output."""
        results = {"session_id": "plain_test", "hr": {"mae": 1.0, "n_pairs": 5}}
        report = generate_validation_report(results, format="plain")
        assert "plain_test" in report
        assert "mae" in report

    def test_generate_report_unknown_format(self):
        """generate_validation_report rejects unknown format."""
        with pytest.raises(ValueError):
            generate_validation_report({}, format="html")


# ---------------------------------------------------------------------------
# Synthetic Only
# ---------------------------------------------------------------------------

class TestSyntheticOnly:
    """Test synthetic fixtures are labeled as such."""

    def test_synthetic_fixture_warning(self):
        """Verify synthetic fixtures report source correctly."""
        fixture = create_synthetic_fixture(n_samples=10)
        assert fixture.ref_source == "synthetic"
        assert fixture.session_id == "synthetic_fixture"


# ---------------------------------------------------------------------------
# Self-contained runner
# ---------------------------------------------------------------------------

def run_all_tests():
    """Run all tests."""
    test_classes = [
        TestSyncConfig,
        TestPairing,
        TestMetrics,
        TestHRVMetrics,
        TestFailureTracking,
        TestIO,
        TestPipeline,
        TestFullPipeline,
        TestReportGeneration,
        TestSyntheticOnly,
    ]

    total_passed = 0
    total_failed = 0

    for cls in test_classes:
        print(f"\n{cls.__name__}")
        instance = cls()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    getattr(instance, method_name)()
                    print(f"  {method_name}... PASS")
                    total_passed += 1
                except Exception as e:
                    print(f"  {method_name}... FAIL: {e}")
                    total_failed += 1

    print(f"\n{'='*50}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
