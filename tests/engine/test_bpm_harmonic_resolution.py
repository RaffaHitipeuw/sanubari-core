"""
Phase 9.1 regression tests: FFT BPM harmonic doubling.

Background
----------
`estimate_bpm_fft()` picks a rate with a windowed spectral vote and then hands
the winner to `_resolve_subharmonic()`, which may halve or double it. The
DOUBLING branch used to fire whenever the band energy at 2f was >= 40 % of the
band energy at the candidate f.

That is not evidence for doubling: a pulse whose fundamental is f has its
second harmonic at 2f, so energy at 2f is exactly the signature of f being the
fundamental. On the rPPG-10 recordings the second harmonic of a real PPG
reaches 0.37-1.00 of the fundamental (median 0.58) and 72 of 78 ROI videos
were therefore reported at exactly twice their true rate.

The fix only promotes to 2f when the double DOMINATES the candidate
(E(2f) >= E(f)), i.e. when there is positive evidence that the candidate is not
the fundamental. The halving branch is untouched: there, energy at the half
rate IS evidence for the fundamental.

These tests pin the decision, not just the number: every case asserts both the
reported BPM and the harmonic-resolution decision that produced it.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np

from rppg_core import (
    FREQ_HIGH,
    FREQ_LOW,
    _resolve_subharmonic,
    estimate_bpm_fft,
)

FPS = 30.0
DURATION_S = 20.0

# The threshold the doubling branch used to apply (pre-Phase-9.1). It is
# quoted here so the tests can assert that the old rule *would* have promoted
# on signals that the fixed rule leaves alone.
OLD_PROMO_THRESHOLD = 0.40


def _pulse(bpm, h2=0.0, h3=0.0, noise=0.0, seed=0, dur=DURATION_S, fps=FPS):
    """Synthetic pulse: fundamental at `bpm` plus optional harmonics."""
    n = int(round(dur * fps))
    t = np.arange(n) / fps
    f = bpm / 60.0
    x = np.sin(2.0 * np.pi * f * t)
    if h2:
        x = x + h2 * np.sin(2.0 * np.pi * 2.0 * f * t + 0.7)
    if h3:
        x = x + h3 * np.sin(2.0 * np.pi * 3.0 * f * t + 1.9)
    if noise:
        x = x + noise * np.random.default_rng(seed).standard_normal(n)
    return x


def _band_energy(fft_v, freqs, mask, center_hz, half_bw=0.12):
    """Same band measure the production code uses in _resolve_subharmonic()."""
    near = (freqs >= center_hz - half_bw) & (freqs <= center_hz + half_bw) & mask
    return float(fft_v[near].sum()) if np.any(near) else 0.0


def _double_ratio(fft_v, freqs, mask, hz):
    """E(2f) / E(f) for a candidate at `hz`."""
    e_cand = _band_energy(fft_v, freqs, mask, hz)
    e_double = _band_energy(fft_v, freqs, mask, hz * 2.0)
    if e_cand <= 0:
        return float("nan")
    return e_double / e_cand


def _spectrum(peaks, n=4096, fps=FPS, sigma=0.02):
    """Synthetic magnitude spectrum with narrow bumps at the given (hz, amp)."""
    freqs = np.fft.rfftfreq(n, d=1.0 / fps)
    fft_v = np.zeros_like(freqs)
    for hz, amp in peaks:
        fft_v = fft_v + amp * np.exp(-0.5 * ((freqs - hz) / sigma) ** 2)
    mask = (freqs >= FREQ_LOW) & (freqs <= FREQ_HIGH)
    return fft_v, freqs, mask


class TestEstimatorLevelHarmonicResolution(unittest.TestCase):
    """estimate_bpm_fft() on synthetic signals: BPM *and* decision."""

    def _estimate(self, signal):
        bpm, freqs, fft_v, vi = estimate_bpm_fft(signal, FPS, roi_name="")
        mask = (freqs >= FREQ_LOW) & (freqs <= FREQ_HIGH)
        return bpm, freqs, fft_v, vi, mask

    def test_slow_pulse_with_a_strong_second_harmonic_is_not_doubled(self):
        """57-60 BPM with a strong 2nd harmonic must stay at the fundamental."""
        for bpm in (57.4, 60.0):
            with self.subTest(bpm=bpm):
                signal = _pulse(bpm, h2=0.9)
                est, freqs, fft_v, vi, mask = self._estimate(signal)

                # the harmonic-resolution decision
                self.assertEqual(vi["harmonic_resolution"], "none")
                self.assertFalse(vi["subharm_corrected"])

                # the reported BPM is the fundamental, not its double
                self.assertLess(est, 90.0, msg=f"{bpm} BPM was reported as {est}")
                self.assertAlmostEqual(est, bpm, delta=8.0)

                # the evidence the old rule acted on really was present:
                # the 2nd harmonic is well above the old 0.40 promotion ratio
                ratio = _double_ratio(fft_v, freqs, mask, est / 60.0)
                self.assertGreaterEqual(
                    ratio, OLD_PROMO_THRESHOLD,
                    msg="test signal no longer reproduces the old promotion evidence",
                )

    def test_72_bpm_result_is_preserved(self):
        """The already-correct 72 BPM case must not change."""
        for h2 in (0.0, 0.5, 0.9):
            with self.subTest(h2=h2):
                signal = _pulse(72.0, h2=h2)
                est, freqs, fft_v, vi, mask = self._estimate(signal)
                self.assertAlmostEqual(est, 72.0, delta=6.0)
                self.assertEqual(vi["harmonic_resolution"], "none")
                self.assertFalse(vi["subharm_corrected"])

    def test_genuinely_fast_pulse_is_neither_halved_nor_shifted(self):
        """A truly fast pulse must not be pulled down to its sub-harmonic."""
        for bpm in (110.0, 120.0, 150.0):
            with self.subTest(bpm=bpm):
                signal = _pulse(bpm, h2=0.4)
                est, freqs, fft_v, vi, mask = self._estimate(signal)
                self.assertAlmostEqual(est, bpm, delta=8.0)
                self.assertEqual(vi["harmonic_resolution"], "none")
                self.assertFalse(vi["subharm_corrected"])

    def test_harmonic_amplitude_sweep_keeps_the_fundamental(self):
        """Every 2nd-harmonic strength below 100 % keeps the fundamental."""
        for h2 in (0.1, 0.3, 0.5, 0.7, 0.9):
            with self.subTest(h2=h2):
                signal = _pulse(60.0, h2=h2)
                est, freqs, fft_v, vi, mask = self._estimate(signal)
                self.assertEqual(vi["harmonic_resolution"], "none")
                self.assertLess(est, 90.0)
                self.assertAlmostEqual(est, 60.0, delta=8.0)

    def test_third_harmonic_does_not_trigger_doubling(self):
        """A 3rd harmonic at 3f must not be mistaken for a 2f fundamental."""
        signal = _pulse(60.0, h2=0.5, h3=0.8)
        est, freqs, fft_v, vi, mask = self._estimate(signal)
        self.assertEqual(vi["harmonic_resolution"], "none")
        self.assertAlmostEqual(est, 60.0, delta=8.0)

    def test_moderate_noise_keeps_the_fundamental(self):
        """Noise must not push the estimate onto the harmonic."""
        for seed in range(5):
            with self.subTest(seed=seed):
                signal = _pulse(60.0, h2=0.6, noise=0.15, seed=seed)
                est, freqs, fft_v, vi, mask = self._estimate(signal)
                self.assertEqual(vi["harmonic_resolution"], "none")
                self.assertLess(est, 90.0)
                self.assertAlmostEqual(est, 60.0, delta=10.0)


class TestSubharmonicDecision(unittest.TestCase):
    """The decision function itself, including the promotion boundary."""

    def test_ratio_just_below_one_is_not_promoted(self):
        """E(2f) slightly below E(f): the candidate stays the fundamental."""
        fft_v, freqs, mask = _spectrum([(1.0, 1.0), (2.0, 0.95)])
        ratio = _double_ratio(fft_v, freqs, mask, 1.0)
        self.assertGreater(ratio, 0.9)
        self.assertLess(ratio, 1.0)

        hz, changed = _resolve_subharmonic(fft_v, freqs, mask, 1.0)
        self.assertFalse(changed)
        self.assertAlmostEqual(hz, 1.0)

    def test_ratio_at_or_above_one_is_promoted(self):
        """E(2f) dominating E(f): only then is doubling defensible."""
        fft_v, freqs, mask = _spectrum([(1.0, 1.0), (2.0, 1.05)])
        ratio = _double_ratio(fft_v, freqs, mask, 1.0)
        self.assertGreaterEqual(ratio, 1.0)

        hz, changed = _resolve_subharmonic(fft_v, freqs, mask, 1.0)
        self.assertTrue(changed)
        self.assertAlmostEqual(hz, 2.0)

    def test_old_promotion_threshold_would_have_fired_on_the_same_spectrum(self):
        """Documents the regression: 0.40 promotion on a sub-dominant double."""
        fft_v, freqs, mask = _spectrum([(1.0, 1.0), (2.0, 0.5)])
        ratio = _double_ratio(fft_v, freqs, mask, 1.0)
        self.assertGreaterEqual(ratio, OLD_PROMO_THRESHOLD)
        self.assertLess(ratio, 1.0)

        hz, changed = _resolve_subharmonic(fft_v, freqs, mask, 1.0)
        self.assertFalse(changed, "a sub-dominant 2nd harmonic must not be promoted")
        self.assertAlmostEqual(hz, 1.0)

    def test_legitimate_halving_still_works(self):
        """Harmonic correction is not disabled: a 2f candidate is halved."""
        fft_v, freqs, mask = _spectrum([(1.0, 0.5), (2.0, 1.0)])
        hz, changed = _resolve_subharmonic(fft_v, freqs, mask, 2.0)
        self.assertTrue(changed)
        self.assertAlmostEqual(hz, 1.0)

    def test_candidate_is_not_halved_without_fundamental_evidence(self):
        """A lone fast peak stays where it is."""
        fft_v, freqs, mask = _spectrum([(1.0, 0.05), (2.0, 1.0)])
        hz, changed = _resolve_subharmonic(fft_v, freqs, mask, 2.0)
        self.assertFalse(changed)
        self.assertAlmostEqual(hz, 2.0)

    def test_doubling_branch_only_covers_candidates_below_75_bpm(self):
        """Above 75 BPM the candidate is never doubled (documented scope)."""
        fft_v, freqs, mask = _spectrum([(1.3, 1.0), (2.6, 2.0)])
        hz, changed = _resolve_subharmonic(fft_v, freqs, mask, 1.3)
        self.assertFalse(changed)
        self.assertAlmostEqual(hz, 1.3)

    def test_zero_candidate_is_untouched(self):
        fft_v, freqs, mask = _spectrum([(1.0, 1.0)])
        hz, changed = _resolve_subharmonic(fft_v, freqs, mask, 0.0)
        self.assertEqual(hz, 0.0)
        self.assertFalse(changed)


if __name__ == "__main__":
    unittest.main()
