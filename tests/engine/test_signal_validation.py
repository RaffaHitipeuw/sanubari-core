"""
Phase 9.0 - Signal Validation Tests

These tests pin down the OFFLINE validation toolkit (signal_validation/), not
the production behaviour it observes. Everything asserted here is against a
KNOWN ground truth:

  * the synthetic suite has an exactly known pulse train (case.true_peak_times_s),
  * the peak matchers are scored against that ground truth,
  * the A/B/C/D classifier is regression-tested so each synthetic case keeps
    producing the verdict its label claims.

Production code (rppg_core, rppg_sqi) is only READ by the toolkit; these
tests never assert on production thresholds, so a threshold change in
production will not fail them.
"""

import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from signal_validation import (  # noqa: E402
    SYNTHETIC_CASES,
    IBIStats,
    acf_periodicity,
    analyze_roi_series,
    analyze_session_csv,
    build_case,
    classify_roi,
    compare_beats,
    compare_hr_traces,
    ibi_stats,
    match_peaks,
    match_peaks_with_latency,
)
from signal_validation.metrics import PeakMatch  # noqa: E402
from signal_validation.pipeline import (  # noqa: E402
    detect_peaks_legacy,
    detect_peaks_posterior,
)
from signal_validation.reference import ECGCondition  # noqa: E402

FPS = 30.0
DURATION = 20.0
TOL = 0.15


def _rgb(signal, offset=(120.0, 100.0, 90.0)):
    """Turn a unit-amplitude trace into three 8-bit-ish RGB channel series."""
    return (
        np.asarray(signal, dtype=float) + offset[0],
        np.asarray(signal, dtype=float) + offset[1],
        np.asarray(signal, dtype=float) + offset[2],
    )


def _analyse(case):
    r, g, b = _rgb(case.signal)
    return analyze_roi_series(
        r, g, b, fps=case.fps,
        roi_name=f"synthetic:{case.name}",
        source=f"synthetic({case.name})",
    )


# ─── Metrics: IBI statistics ─────────────────────────────────────────────────

class TestIBIStats(unittest.TestCase):

    def test_regular_intervals_have_zero_cv(self):
        peaks = [0.0, 1.0, 2.0, 3.0, 4.0]
        st = ibi_stats(peaks)
        self.assertEqual(st.n_intervals, 4)
        self.assertAlmostEqual(st.mean_ibi, 1.0)
        self.assertAlmostEqual(st.cv, 0.0, places=9)
        self.assertAlmostEqual(st.implied_bpm, 60.0)
        self.assertAlmostEqual(st.rmssd, 0.0, places=6)
        self.assertAlmostEqual(st.pnn50, 0.0)

    def test_known_irregular_intervals(self):
        # intervals: 1.0, 1.5, 0.5  -> mean 1.0, population std 0.4082
        peaks = [0.0, 1.0, 2.5, 3.0]
        st = ibi_stats(peaks)
        self.assertEqual(st.n_intervals, 3)
        self.assertAlmostEqual(st.mean_ibi, 1.0)
        self.assertAlmostEqual(st.std_ibi, float(np.std([1.0, 1.5, 0.5])), places=9)
        self.assertAlmostEqual(st.cv, float(np.std([1.0, 1.5, 0.5])), places=6)
        self.assertAlmostEqual(st.min_ibi, 0.5)
        self.assertAlmostEqual(st.max_ibi, 1.5)

    def test_too_few_peaks_is_empty_not_an_error(self):
        for peaks in ([], [1.0]):
            st = ibi_stats(peaks)
            self.assertEqual(st.n_intervals, 0)
            self.assertTrue(np.isnan(st.cv))

    def test_duplicate_timestamps_are_ignored(self):
        st = ibi_stats([0.0, 1.0, 1.0, 2.0])
        self.assertEqual(st.n_intervals, 2)


# ─── Metrics: autocorrelation periodicity ────────────────────────────────────

class TestACFPeriodicity(unittest.TestCase):

    def test_clean_pulse_is_strongly_periodic(self):
        fps, bpm = FPS, 72.0
        t = np.arange(int(DURATION * fps)) / fps
        sig = np.sin(2 * np.pi * (bpm / 60.0) * t)
        res = acf_periodicity(sig, fps)
        self.assertGreater(res.acf_peak_value, 0.8)
        self.assertTrue(res.acf_peak_is_local)
        self.assertAlmostEqual(res.acf_peak_bpm, bpm, delta=6.0)
        self.assertGreater(res.acf_regularity, 0.8)

    def test_flat_signal_has_no_periodicity(self):
        res = acf_periodicity(np.full(600, 3.0), FPS)
        self.assertAlmostEqual(res.acf_regularity, 0.0)
        self.assertAlmostEqual(res.acf_peak_value, 0.0)

    def test_white_noise_has_weak_periodicity(self):
        rng = np.random.default_rng(7)
        res = acf_periodicity(rng.standard_normal(900), FPS)
        self.assertLess(res.acf_regularity, 0.35)

    def test_short_signal_returns_placeholder(self):
        res = acf_periodicity(np.zeros(10), FPS)
        self.assertAlmostEqual(res.acf_peak_value, 0.0)


# ─── Metrics: peak matching against ground truth ─────────────────────────────

class TestPeakMatching(unittest.TestCase):

    def test_perfect_match(self):
        truth = [1.0, 2.0, 3.0]
        m = match_peaks(truth, truth, tolerance_s=TOL)
        self.assertEqual((m.n_true, m.n_detected, m.n_matched), (3, 3, 3))
        self.assertEqual(m.n_missed, 0)
        self.assertEqual(m.n_false, 0)
        self.assertAlmostEqual(m.sensitivity, 1.0)
        self.assertAlmostEqual(m.precision, 1.0)
        self.assertAlmostEqual(m.mean_abs_interval_error_s, 0.0)

    def test_missed_and_false_peaks_are_separated(self):
        truth = [1.0, 2.0, 3.0, 4.0]
        detected = [1.0, 2.0, 3.5, 4.0]     # 3.0 missed, 3.5 is a false peak
        m = match_peaks(detected, truth, tolerance_s=TOL)
        self.assertEqual(m.n_matched, 3)
        self.assertEqual(m.n_missed, 1)
        self.assertEqual(m.n_false, 1)
        self.assertIn(3.0, [round(x, 3) for x in m.missed_times_s])
        self.assertIn(3.5, [round(x, 3) for x in m.false_times_s])
        self.assertAlmostEqual(m.sensitivity, 0.75)
        self.assertAlmostEqual(m.precision, 0.75)

    def test_one_true_peak_cannot_absorb_two_detections(self):
        truth = [1.0, 2.0]
        detected = [1.0, 1.05, 2.0]
        m = match_peaks(detected, truth, tolerance_s=TOL)
        self.assertEqual(m.n_matched, 2)
        self.assertEqual(m.n_false, 1)

    def test_interval_error_is_signed_offset(self):
        m = match_peaks([1.1, 2.1], [1.0, 2.0], tolerance_s=TOL)
        self.assertAlmostEqual(m.mean_abs_interval_error_s, 0.1, places=6)
        self.assertAlmostEqual(m.max_abs_interval_error_s, 0.1, places=6)

    def test_empty_input_is_all_missed(self):
        m = match_peaks([], [1.0, 2.0], tolerance_s=TOL)
        self.assertEqual(m.n_missed, 2)
        self.assertEqual(m.n_false, 0)
        self.assertEqual(m.n_matched, 0)
        self.assertAlmostEqual(m.sensitivity, 0.0)
        self.assertTrue(np.isnan(m.precision))

    def test_latency_compensation_recovers_a_pure_delay(self):
        truth = [1.0, 1.8, 2.6, 3.4, 4.2]
        delay = 0.25
        detected = [t + delay for t in truth]
        naive = match_peaks(detected, truth, tolerance_s=0.10)
        self.assertLess(naive.n_matched, len(truth))   # a pure delay breaks naive matching

        m, latency = match_peaks_with_latency(detected, truth, tolerance_s=0.10)
        self.assertAlmostEqual(latency, delay, delta=0.05)
        self.assertEqual(m.n_matched, len(truth))
        self.assertAlmostEqual(m.sensitivity, 1.0)

    def test_latency_search_is_robust_to_one_corrupt_region(self):
        truth = list(np.arange(1.0, 20.0, 0.8))
        detected = [t + 0.2 for t in truth]
        # Replace a chunk of the detected beats with jittered ones.
        detected[10:16] = [10.0 + 0.4 * k for k in range(6)]
        m, latency = match_peaks_with_latency(detected, truth, tolerance_s=0.10)
        self.assertAlmostEqual(latency, 0.2, delta=0.05)


# ─── Synthetic suite: ground truth itself ────────────────────────────────────

class TestSyntheticGroundTruth(unittest.TestCase):

    def test_all_cases_build(self):
        for name in SYNTHETIC_CASES:
            case = build_case(name, duration_s=DURATION, fps=FPS)
            self.assertEqual(len(case.signal), int(DURATION * FPS))
            self.assertIn(case.expected_category, ("OK", "A", "B", "C", "D"))

    def test_true_peaks_are_periodic_and_match_the_bpm(self):
        for name in SYNTHETIC_CASES:
            case = build_case(name, duration_s=DURATION, fps=FPS)
            if len(case.true_peak_times_s) < 3:
                continue
            ibis = np.diff(case.true_peak_times_s)
            self.assertLess(np.std(ibis) / np.mean(ibis), 1e-6,
                            msg=f"{name}: ground truth is not periodic")
            expected_ibi = 60.0 / case.true_bpm
            self.assertAlmostEqual(float(np.mean(ibis)), expected_ibi, delta=1e-6)

    def test_flat_and_noise_cases_have_no_ground_truth_beats(self):
        for name in ("flat", "white_noise"):
            case = build_case(name, duration_s=DURATION, fps=FPS)
            self.assertEqual(case.true_peak_times_s, [])

    def test_flat_signal_is_exactly_flat(self):
        case = build_case("flat", duration_s=DURATION, fps=FPS)
        self.assertLess(float(np.std(case.signal)), 1e-12)


# ─── Synthetic suite: detector scoring against ground truth ──────────────────

class TestDetectorAgainstGroundTruth(unittest.TestCase):

    def _match(self, case, detector="legacy"):
        analysis = _analyse(case)
        peaks = (analysis.peaks_legacy_s if detector == "legacy"
                 else analysis.peaks_posterior_s)
        return analysis, match_peaks_with_latency(peaks, case.true_peak_times_s,
                                                  tolerance_s=TOL)

    def test_clean_pulse_is_detected_perfectly(self):
        case = build_case("clean", duration_s=DURATION, fps=FPS)
        for detector in ("legacy", "posterior"):
            _analysis, (m, _lat) = self._match(case, detector)
            self.assertAlmostEqual(m.sensitivity, 1.0, delta=0.02, msg=detector)
            self.assertAlmostEqual(m.precision, 1.0, delta=0.02, msg=detector)
            self.assertLess(m.mean_abs_interval_error_s, 0.05)

    def test_flat_signal_yields_no_peaks(self):
        case = build_case("flat", duration_s=DURATION, fps=FPS)
        analysis = _analyse(case)
        self.assertEqual(len(analysis.peaks_legacy_s), 0)
        self.assertEqual(len(analysis.peaks_posterior_s), 0)

    def test_white_noise_yields_no_true_beats(self):
        case = build_case("white_noise", duration_s=DURATION, fps=FPS)
        _analysis, (m, _lat) = self._match(case)
        self.assertEqual(m.n_matched, 0)
        self.assertEqual(m.n_true, 0)

    def test_missing_peaks_case_loses_beats(self):
        case = build_case("missing_peaks", duration_s=DURATION, fps=FPS)
        _analysis, (m, _lat) = self._match(case)
        self.assertGreater(m.n_missed, 0, "burst should destroy beats")
        self.assertLess(m.sensitivity, 1.0)

    def test_extra_peaks_case_invents_beats(self):
        case = build_case("extra_peaks", duration_s=DURATION, fps=FPS)
        _analysis, (m, _lat) = self._match(case)
        self.assertGreater(m.n_false, 0, "oscillation should create false beats")
        self.assertLess(m.precision, 1.0)

    def test_production_detectors_are_replicated(self):
        # The offline detectors must stay bit-for-bit consistent with the
        # production formulations documented in rppg_core / rppg_sqi.
        case = build_case("clean", duration_s=DURATION, fps=FPS)
        analysis = _analyse(case)
        from scipy.signal import find_peaks
        from rppg_core import cfg

        sig = analysis.filtered
        z = (sig - np.mean(sig)) / np.std(sig)
        expected, _ = find_peaks(z, distance=max(int(FPS * 0.45), 5), prominence=0.35)
        self.assertEqual(list(analysis.peaks_posterior_s),
                         [float(p / FPS) for p in expected])

        from scipy.signal import detrend as scipy_detrend
        z2 = scipy_detrend(sig - np.mean(sig), type="linear")
        z2 = (z2 - np.mean(z2)) / np.std(z2)
        expected_legacy, _ = find_peaks(
            z2, distance=int(FPS * 0.50),
            prominence=cfg.PEAK_PROMINENCE_MIN, height=0.1,
        )
        self.assertEqual(list(analysis.peaks_legacy_s),
                         [float(p / FPS) for p in expected_legacy])


# ─── Offline analysis of the synthetic signals ───────────────────────────────

class TestOfflineAnalysis(unittest.TestCase):

    def test_clean_signal_scores_high_regularity(self):
        case = build_case("clean", duration_s=DURATION, fps=FPS)
        a = _analyse(case)
        self.assertGreater(a.regularity_legacy, 80.0)
        self.assertGreater(a.regularity_posterior, 80.0)
        self.assertGreater(a.sqi_posterior, 50.0)
        self.assertAlmostEqual(a.bpm_fft, case.true_bpm, delta=3.0)
        self.assertLess(a.ibi_legacy.cv, 0.10)

    def test_flat_signal_scores_zero(self):
        case = build_case("flat", duration_s=DURATION, fps=FPS)
        a = _analyse(case)
        self.assertEqual(len(a.peaks_legacy_s), 0)
        self.assertLess(a.sqi_posterior, 1.0)
        self.assertAlmostEqual(a.acf.acf_regularity, 0.0)

    def test_motion_raises_the_low_frequency_ratio(self):
        clean = _analyse(build_case("clean", duration_s=DURATION, fps=FPS))
        motion = _analyse(build_case("motion", duration_s=DURATION, fps=FPS))
        self.assertGreater(motion.lf_ratio, clean.lf_ratio)

    def test_low_frequency_ratio_is_dimensionless_and_finite(self):
        for name in SYNTHETIC_CASES:
            a = _analyse(build_case(name, duration_s=DURATION, fps=FPS))
            # NaN means "no cardiac-band power at all" (the flat case); any
            # other value must be a finite, non-negative ratio.
            self.assertTrue(np.isnan(a.lf_ratio) or np.isfinite(a.lf_ratio), msg=name)
            self.assertTrue(np.isnan(a.lf_ratio) or a.lf_ratio >= 0.0, msg=name)

    def test_analysis_does_not_mutate_production_config(self):
        from rppg_core import cfg
        before = (cfg.PEAK_PROMINENCE_MIN, cfg.REGULARITY_HARD_GATE)
        _analyse(build_case("noisy", duration_s=DURATION, fps=FPS))
        after = (cfg.PEAK_PROMINENCE_MIN, cfg.REGULARITY_HARD_GATE)
        self.assertEqual(before, after)

    def test_signal_export_writes_raw_filtered_and_peaks(self):
        from signal_validation import export_roi_signals

        case = build_case("clean", duration_s=DURATION, fps=FPS)
        analysis = _analyse(case)
        with tempfile.TemporaryDirectory() as tmp:
            paths = export_roi_signals(analysis, tmp, tag="unit")
            self.assertTrue(os.path.exists(paths["signal"]))
            self.assertTrue(os.path.exists(paths["peaks"]))
            self.assertTrue(os.path.exists(paths["meta"]))

            with open(paths["signal"], encoding="utf-8") as f:
                lines = f.read().strip().splitlines()
            self.assertEqual(lines[0].split(","),
                             ["frame_index", "t_s", "raw_r", "raw_g", "raw_b",
                              "filtered", "is_peak_legacy", "is_peak_posterior"])
            self.assertEqual(len(lines) - 1, analysis.n_samples)

            with open(paths["peaks"], encoding="utf-8") as f:
                peak_lines = f.read().strip().splitlines()[1:]
            self.assertEqual(len(peak_lines),
                             len(analysis.peaks_legacy_s) + len(analysis.peaks_posterior_s))


# ─── Classifier: A/B/C/D regression ──────────────────────────────────────────

class TestClassifier(unittest.TestCase):

    def _classify(self, name):
        case = build_case(name, duration_s=DURATION, fps=FPS)
        analysis = _analyse(case)
        peaks = analysis.peaks_legacy_s
        m, _lat = match_peaks_with_latency(peaks, case.true_peak_times_s, tolerance_s=TOL)
        cls = classify_roi(analysis, truth_match=m,
                           reference_available=bool(case.true_peak_times_s))
        return cls

    def test_each_synthetic_case_keeps_its_category(self):
        for name in SYNTHETIC_CASES:
            case = build_case(name, duration_s=DURATION, fps=FPS)
            cls = self._classify(name)
            self.assertEqual(
                cls.category, case.expected_category,
                msg=f"{name}: expected {case.expected_category}, got {cls.category} "
                    f"({'; '.join(cls.evidence)})",
            )

    def test_without_a_reference_the_verdict_is_never_optimistic(self):
        case = build_case("clean", duration_s=DURATION, fps=FPS)
        analysis = _analyse(case)
        cls = classify_roi(analysis, truth_match=None, reference_available=False)
        self.assertIn(cls.category, ("A", "B", "C", "D"))
        self.assertTrue(any("No ground truth" in cv for cv in cls.caveats))

    def test_caveat_about_heart_rhythm_is_always_present(self):
        cls = self._classify("clean")
        self.assertTrue(any("not a measured heart rhythm" in cv for cv in cls.caveats))


# ─── Reference comparison ────────────────────────────────────────────────────

class TestReferenceComparison(unittest.TestCase):

    def _ecg(self, hr_bpm=60.0, n_beats=30):
        period = 60.0 / hr_bpm
        r_peaks = [1.0 + i * period for i in range(n_beats)]
        times, hr = [], []
        for k, t in enumerate(np.arange(0.0, n_beats * period, 1.0)):
            times.append(float(t))
            # Mild respiratory-style variation so a correlation is defined.
            hr.append(float(hr_bpm + 2.0 * np.sin(k / 3.0)))
        return ECGCondition(
            path="synthetic_ecg.npy",
            r_peak_times_s=r_peaks,
            hr_times_s=times,
            hr_bpm=hr,
            offset_sec=0.0,
            offset_known=True,
        )

    def test_identical_hr_traces_match_exactly(self):
        ecg = self._ecg()
        cmp = compare_hr_traces(ecg.hr_times_s, ecg.hr_bpm, ecg, tolerance_s=1.0)
        self.assertGreater(cmp["n_pairs"], 0)
        self.assertAlmostEqual(cmp["mae_bpm"], 0.0, places=6)
        self.assertAlmostEqual(cmp["rmse_bpm"], 0.0, places=6)
        self.assertAlmostEqual(cmp["pearson_r"], 1.0, places=6)

    def test_constant_bias_is_reported(self):
        ecg = self._ecg()
        biased = [h + 10.0 for h in ecg.hr_bpm]
        cmp = compare_hr_traces(ecg.hr_times_s, biased, ecg, tolerance_s=1.0)
        self.assertAlmostEqual(cmp["mae_bpm"], 10.0, places=6)
        self.assertAlmostEqual(cmp["bias_bpm"], 10.0, places=6)

    def test_beat_comparison_with_a_known_offset(self):
        ecg = self._ecg()
        detected = list(ecg.r_peak_times_s)
        m, offset = compare_beats(detected, ecg, tolerance_s=0.1, search_offset=False)
        self.assertEqual(m.n_matched, len(detected))
        self.assertAlmostEqual(offset, 0.0)

    def test_offset_search_recovers_a_planted_delay(self):
        ecg = self._ecg()
        detected = [t + 0.4 for t in ecg.r_peak_times_s]
        m, offset = compare_beats(detected, ecg, tolerance_s=0.1, search_offset=True)
        self.assertGreater(m.n_matched, 0.8 * len(ecg.r_peak_times_s))
        self.assertAlmostEqual(offset, 0.4, delta=0.1)

    def test_ecg_ibi_cv_is_the_physiological_counterpart(self):
        ecg = self._ecg(hr_bpm=60.0)
        self.assertAlmostEqual(ecg.ibi_cv, 0.0, places=9)
        # A perfectly periodic ECG has zero IBI CV.
        irregular = ECGCondition(
            path="x.npy",
            r_peak_times_s=[0.0, 1.0, 2.0, 3.5, 4.5, 5.5],
        )
        self.assertGreater(irregular.ibi_cv, 0.05)
        self.assertTrue(np.isnan(ECGCondition(path="x.npy").ibi_cv))


# ─── Recorded-session ingestion ──────────────────────────────────────────────

class TestSessionCsv(unittest.TestCase):

    def test_session_csv_is_analysed_per_roi(self):
        case = build_case("clean", duration_s=DURATION, fps=FPS)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "raw_signals.csv")
            n = len(case.signal)
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("timestamp,roi_name,r,g,b,bpm,sqi\n")
                for i in range(n):
                    t = i / FPS
                    f.write(f"{t:.4f},forehead,{case.signal[i] + 120:.4f},"
                            f"{case.signal[i] + 100:.4f},{case.signal[i] + 90:.4f},,\n")
            out = analyze_session_csv(path, fps=FPS)
        self.assertIn("forehead", out)
        a = out["forehead"]
        self.assertEqual(a.n_samples, n)
        self.assertGreater(len(a.peaks_legacy_s), 0)
        self.assertAlmostEqual(a.fps, FPS, delta=0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
