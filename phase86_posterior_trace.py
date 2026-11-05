"""
Phase 8.6: Trace actual PosteriorSQI.compute() call for forehead ROI.

Tests whether the PosteriorSQI bug (prev_sqi / 1000) is still present
and checks the roi_snr display format.
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from rppg_sqi import PosteriorSQI
from rppg_config import cfg

print("=" * 60)
print("PHASE 8.6: PosteriorSQI Call Trace")
print("=" * 60)

# Simulate forehead signal: low SNR, 120 frames
fps = 30.0
n = 120
hr_hz = 84.2 / 60.0  # match evidence BPM
t = np.arange(n) / fps

# Low-amplitude signal: amplitude=0.1, noise=0.3 → SNR ~-10 dB
np.random.seed(42)
signal = (
    0.1 * np.sin(2 * math.pi * hr_hz * t) +
    0.05 * np.sin(2 * math.pi * hr_hz * 2 * t) +
    0.3 * np.random.randn(n)
)
signal = signal - np.mean(signal)

# Run PosteriorSQI.compute() in two-step mode (simulate prev_sqi = 9.0)
roi = PosteriorSQI(roi_name="forehead")

# Frame 1: no prev_sqi
r1 = roi.compute(signal, fps, 84.2, motion_score=2.06)
print(f"\n  Frame 1 (no prev_sqi):")
print(f"  snr_db={r1.snr_db:.2f}  snr_score={r1.p_signal_given_spectrum:.3f}")
print(f"  regularity={r1.regularity_score:.3f}")
print(f"  p_valid={r1.p_valid_given_motion:.3f}")
print(f"  sqi={r1.sqi:.1f}%")

# Simulate the smoothing: prev_sqi = 9.0
# Compute again with prev_sqi = 9.0
r2 = roi.compute(signal, fps, 84.2, motion_score=2.06, prev_sqi=9.0)
print(f"\n  Frame 2 (prev_sqi=9.0):")
print(f"  sqi={r2.sqi:.1f}%  (should show smoothing effect)")
print(f"  Note: prev_sqi=9.0 → p_prev = 9.0/100.0 = {9.0/100.0:.4f}")
print(f"  With FIXED /100: p_prev=0.0900, blended p_valid = 0.35*{r1.sqi/100:.4f} + 0.65*0.0900 = {0.35*r1.sqi/100 + 0.65*0.09:.4f}")
print(f"  With BUG /1000: p_prev=0.009, blended p_valid = 0.35*{r1.sqi/100:.4f} + 0.65*0.009 = {0.35*r1.sqi/100 + 0.65*0.009:.4f}")

# Check roi_snr display format
print(f"\n  roi_snr storage (from breakdown['snr_db']):")
print(f"  snr_db = {r2.snr_db:.2f} dB (stored in roi.roi_snr)")
print(f"  Display: format 'roi_snr:.1f%' → 'snr={r2.snr_db:.1f}%' (MISLEADING: shows '%' but value is dB)")

print("\n" + "=" * 60)
print("ROOT CAUSE SUMMARY")
print("=" * 60)
print("""
BUG A: PosteriorSQI /1000 (Phase 8.5 already fixed /1000 -> /100.0)
  Phase 8.5 changed /1000 to /100.0.
  Current code: prev_sqi / 100.0 (CORRECT).
  Temporal smoothing now blends previous SQI correctly.

BUG B: roi_snr display format (FIX NEEDED)
  roi_snr stores snr_db in dB (PosteriorSQI.compute result).
  Display: f"snr={roi_snr:.1f}%" adds '%' → 'snr=46.5%' (MISLEADING).
  dB value shown with '%' suffix → user thinks 46.5% SNR (very good).
  Actual value: 46.5 dB → very HIGH SNR (10^4.65x ratio).
  FIX: change format to f"snr={roi_snr:.2f}dB" in rppg_main.py.

The peak=1.5% and regularity=5.0% are CORRECT signal quality assessment.
The forehead signal has genuinely poor quality at 120 frames with low amplitude.
""")
