"""
Phase 8.5 Diagnostic: SQI Recovery Root-Cause Analysis

Traces the complete signal path from raw ROI buffers through FFT/BPM
estimation to SQI computation, identifying exactly why SQI components are
zero and why the 144.3 BPM estimate is unreliable.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from scipy.signal import butter as scipy_butter, sosfilt as scipy_sosfilt
from rppg_config import cfg
from rppg_core import (
    MultiROIFusionEngineV2, estimate_bpm_fft, compute_sqi,
    FREQ_LOW, FREQ_HIGH,
)


class _DummyPoint:
    __slots__ = ('x', 'y', 'z')
    def __init__(self, x, y, z=0.0):
        self.x = x; self.y = y; self.z = z

class _DummyLandmarks:
    def __init__(self, pts): self._pts = pts
    @property
    def landmark(self): return self
    def __len__(self): return len(self._pts)
    def __getitem__(self, k): return self._pts[k]

def _lm(x=0.5, y=0.5, count=478):
    return _DummyLandmarks([_DummyPoint(x, y) for _ in range(count)])


def test_fft_resolution():
    """Show that 120 frames gives ~15 BPM/bin, making 72 vs 144 ambiguous."""
    fps = 30.0
    n = 120
    bin_hz = fps / n
    print(f"\nFFT RESOLUTION (n={n} @ {fps} fps)")
    print(f"  Hz/bin: {bin_hz:.4f}")
    print(f"  BPM/bin: {bin_hz*60:.1f}")
    print(f"  True 72 BPM at bin: {72/60.0/bin_hz:.1f}")
    print(f"  True 144 BPM at bin: {144/60.0/bin_hz:.1f}")


def test_signal_simulation():
    """Generate synthetic rPPG signal at 72 BPM and check what FFT returns."""
    import math
    fps = 30.0
    n = 120
    hr_hz = 72.0 / 60.0
    t = np.arange(n) / fps
    signal = (
        0.70 * np.sin(2 * math.pi * hr_hz * t) +
        0.20 * np.sin(2 * math.pi * hr_hz * 2 * t) +
        0.30 * np.random.randn(n)
    )
    signal = signal - np.mean(signal)

    sos = scipy_butter(4, [FREQ_LOW / (fps/2), FREQ_HIGH / (fps/2)],
                      btype='band', output='sos')
    sig_filt = scipy_sosfilt(sos, signal)
    std2 = float(np.std(sig_filt))
    if std2 > 1e-8:
        sig_filt = (sig_filt - np.mean(sig_filt)) / std2

    win_signal = sig_filt * np.hanning(n)
    fft_v = np.abs(np.fft.rfft(win_signal))
    freqs = np.fft.rfftfreq(n, d=1.0/fps)
    mask = (freqs >= FREQ_LOW) & (freqs <= FREQ_HIGH)
    peak_idx = np.argmax(fft_v[mask])
    peak_hz = freqs[mask][peak_idx]
    peak_power = fft_v[mask][peak_idx]
    sorted_bins = np.argsort(fft_v[mask])[::-1]
    top3 = [(freqs[mask][i] * 60, fft_v[mask][i]) for i in sorted_bins[:3]]

    bpm_raw, _, _, fft_val = estimate_bpm_fft(sig_filt, fps, roi_name="sim_test")
    print(f"\nSIGNAL SIM: 72 BPM ground truth, n={n} frames")
    print(f"  FFT peak: {bpm_raw:.1f} BPM  dominance: {fft_val.get('dominance', 'N/A'):.3f}")
    for bpm_v, pw in top3:
        bar = '#' * int(pw / peak_power * 20)
        print(f"    {bpm_v:6.1f} BPM  power={pw:.2f}  {bar}")

    sqi, bd = compute_sqi(sig_filt, fps, bpm_raw, motion_score=0.5,
                           mean_brightness=128.0, roi_brightness=128.0,
                           fft_validation=fft_val, prev_sqi=-1.0,
                           roi_obj=None, exposure_drift=0.0, roi_name="cheek_right")
    sqi_at_72, _ = compute_sqi(sig_filt, fps, 72.0, motion_score=0.5,
                                  mean_brightness=128.0, roi_brightness=128.0,
                                  fft_validation=fft_val, prev_sqi=-1.0,
                                  roi_obj=None, exposure_drift=0.0, roi_name="cheek_right")
    print(f"  SQI at {bpm_raw:.1f} BPM: {sqi:.1f}%")
    print(f"  SQI at 72.0 BPM: {sqi_at_72:.1f}%")


def test_sqi_breakdown_early_return():
    print(f"\nSQI_BREAKDOWN EARLY RETURN: All ROIs < SQI_HARD_GATE={cfg.SQI_HARD_GATE}")
    print("  When all ROI SQI < SQI_HARD_GATE:")
    print("  -> V2 early-return (line ~2189)")
    print("  FIX A: result.sqi_breakdown = _best_sqi_breakdown (tracked during ROI loop)")


def test_compute_sqi_short_signal():
    import math
    fps = 30.0
    n = 120
    hr_hz = 72.0 / 60.0
    t = np.arange(n) / fps
    signal = (
        1.0 * np.sin(2 * math.pi * hr_hz * t) +
        0.5 * np.sin(2 * math.pi * hr_hz * 2 * t) +
        0.3 * np.random.randn(n)
    )
    signal = signal - np.mean(signal)

    sos = scipy_butter(4, [FREQ_LOW / (fps/2), FREQ_HIGH / (fps/2)],
                      btype='band', output='sos')
    sig_filt = scipy_sosfilt(sos, signal)
    std2 = float(np.std(sig_filt))
    if std2 > 1e-8:
        sig_filt = (sig_filt - np.mean(sig_filt)) / std2

    bpm_raw, _, _, fft_val = estimate_bpm_fft(sig_filt, fps, roi_name="test")
    sqi, bd = compute_sqi(sig_filt, fps, bpm_raw, motion_score=0.5,
                           mean_brightness=128.0, roi_brightness=128.0,
                           fft_validation=fft_val, prev_sqi=-1.0,
                           roi_obj=None, exposure_drift=0.0, roi_name="cheek_right")
    print(f"\nCOMPUTE_SQI: n={n} frames, BPM={bpm_raw:.1f}")
    print(f"  SQI: {sqi:.1f}%  breakdown: {bd}")


def test_motion_borderline():
    from rppg_core import MotionArtifactDetector
    det = MotionArtifactDetector()
    print(f"\nMOTION DETECTOR: Borderline score analysis")
    print(f"  ENTER={det.enter_threshold}  EXIT={det.exit_threshold}  grace={cfg.MOTION_GRACE_FRAMES}")
    print(f"  Score 2.06 > EXIT({det.exit_threshold}): {2.06 > det.exit_threshold}")
    print(f"  Score 2.06 < ENTER({det.enter_threshold}): {2.06 < det.enter_threshold}")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 8.5: SQI Recovery -- Diagnostic")
    print("=" * 60)
    test_fft_resolution()
    test_signal_simulation()
    test_sqi_breakdown_early_return()
    test_compute_sqi_short_signal()
    test_motion_borderline()
    print("\n" + "=" * 60)
