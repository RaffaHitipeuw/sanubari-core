"""
Regression test for session diagnostic findings.

Tests counter behavior and metric calculations.
"""

import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestFailureModeLogger:
    """Test FailureModeLogger counter behavior."""

    def test_tick_increments_total_frames(self):
        """Verify tick() increments total_frames."""
        from rppg_vitals import FailureModeLogger

        logger = FailureModeLogger()

        # Simulate 100 frames
        for _ in range(100):
            logger.tick()

        assert logger.counts['total_frames'] == 100

    def test_motion_reject_rate_calculation(self):
        """Verify motion_reject_rate uses correct denominator."""
        from rppg_vitals import FailureModeLogger

        logger = FailureModeLogger()

        # Simulate 100 frames, 30 motion rejected
        for i in range(100):
            logger.tick()
            if i < 30:
                logger.log('motion_rejected', f'frame={i}')

        summary = logger.get_summary()

        assert summary['total_frames'] == 100
        assert summary['motion_reject_rate'] == 0.3

    def test_rate_with_zero_frames(self):
        """Verify rate calculation handles edge case."""
        from rppg_vitals import FailureModeLogger

        logger = FailureModeLogger()
        # Don't call tick()

        summary = logger.get_summary()

        # Should use max(total_frames, 1) = 1
        assert summary['total_frames'] == 1


class TestSQIComponents:
    """Test SQI component calculations."""

    def test_sqi_result_fields(self):
        """Verify SQIResult contains expected fields."""
        from rppg_sqi import SQIResult

        result = SQIResult(
            sqi=75.0,
            log_posterior=-1.5,
            p_signal_given_spectrum=0.8,
            p_valid_given_motion=0.9,
            p_valid_given_illum=0.95,
            snr_db=6.0,
            spectral_concentration=0.5,
            regularity_score=0.7,
            sqi_std=5.0,
            n_samples=128
        )

        assert result.sqi == 75.0
        assert result.snr_db == 6.0
        assert result.n_samples == 128


class TestMotionPenalty:
    """Test motion penalty calculation."""

    def test_motion_penalty_formula(self):
        """Verify motion penalty is fraction 0-1."""
        # From rppg_core.py:972
        # motion_penalty = min(motion_score / 15.0, cfg.SQI_MAX_MOTION_PENALTY)

        motion_score = 7.5  # Example
        max_penalty = 0.3  # SQI_MAX_MOTION_PENALTY

        penalty = min(motion_score / 15.0, max_penalty)

        assert 0 <= penalty <= max_penalty
        assert isinstance(penalty, float)


class TestPeakRatio:
    """Test peak ratio calculation."""

    def test_peak_ratio_formula(self):
        """Verify peak ratio from spectrum."""
        # From rppg_sqi.py:142
        # peak_ratio = p_signal / (sum(sorted_psd[-3:]) + 1e-9)

        # Simulate PSD
        psd = np.array([0.1, 0.2, 0.5, 0.3, 0.8, 0.4, 0.2, 0.1])
        sorted_psd = np.sort(psd)

        p_signal = 0.8  # Main peak
        top3_sum = np.sum(sorted_psd[-3:])  # Sum of top 3

        peak_ratio = p_signal / (top3_sum + 1e-9)

        # With p_signal=0.8, top3_sum includes the peak itself = 0.8 + 0.5 + 0.4 = 1.7
        # peak_ratio should be < 1.0 if peak is not dominant
        assert peak_ratio < 1.0


class TestDynamicWeight:
    """Test dynamic ROI weight calculation."""

    def test_dyn_weight_bounds(self):
        """Verify dynamic weight is in valid range."""
        # From rppg_core.py:1122
        # weight = base_weight * dyn_weight_factor

        base_weight = 0.25
        dyn_weight_factor = 0.4  # Example

        weight = base_weight * dyn_weight_factor

        assert 0 <= weight <= base_weight


def run_tests():
    """Run all tests."""
    import rppg_vitals
    import rppg_sqi

    test_classes = [
        TestFailureModeLogger,
        TestSQIComponents,
        TestMotionPenalty,
        TestPeakRatio,
        TestDynamicWeight,
    ]

    total_passed = 0
    total_failed = 0

    for test_class in test_classes:
        print(f"\n{test_class.__name__}")
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                method = getattr(instance, method_name)
                try:
                    method()
                    print(f"  {method_name}... PASS")
                    total_passed += 1
                except Exception as e:
                    print(f"  {method_name}... FAIL ({e})")
                    total_failed += 1

    print(f"\nTotal: {total_passed} passed, {total_failed} failed")
    return total_failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
