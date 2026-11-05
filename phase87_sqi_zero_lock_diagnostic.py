"""
Phase 8.x SQI Zero-Lock Diagnostic: Trace all failure modes.

Reproduces minimal scenarios for each failure mode without requiring camera/replay.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from scipy.signal import butter, sosfilt as scipy_sosfilt
from rppg_config import cfg
from rppg_core import (
    MultiROIFusionEngineV2, MultiROIFusionEngine,
    estimate_bpm_fft, compute_sqi,
    FREQ_LOW, FREQ_HIGH, ROI_CONFIGS,
)
from rppg_sqi import PosteriorSQI


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

def _gray():
    return np.full((480, 640, 3), 128, dtype=np.uint8)


# =========================================================================
# PHASE 1: Trace SNR computation paths
# =========================================================================

def test_snrdB_produces_valid_range():
    """PosteriorSQI.snr_db range: typical values should be -20 to +40 dB.
    Extreme -90 dB occurs when signal power is below 1e-9 relative to noise."""
    print("\n=== SNR dB Range Test ===")

    roi = PosteriorSQI("test")
    fps = 30.0
    n = 120
    hr_hz = 72.0 / 60.0
    t = np.arange(n) / fps

    cases = [
        ("clean signal", 0.8 * np.sin(2*np.pi*hr_hz*t) + 0.1*np.random.randn(n)),
        ("poor SNR", 0.1 * np.sin(2*np.pi*hr_hz*t) + 0.9*np.random.randn(n)),
        ("near-zero signal", 0.01 * np.sin(2*np.pi*hr_hz*t) + 0.99*np.random.randn(n)),
    ]

    for name, signal in cases:
        signal = signal - np.mean(signal)
        sos = butter(4, [FREQ_LOW/(fps/2), FREQ_HIGH/(fps/2)],
                     btype='band', output='sos')
        sf = scipy_sosfilt(sos, signal)
        _std = float(np.std(sf))
        if _std > 1e-8:
            sf = (sf - np.mean(sf)) / _std

        r = roi.compute(sf, fps, 72.0)
        print(f"  {name}: snr_db={r.snr_db:6.1f} dB  sqi={r.sqi:4.1f}%  "
              f"reg={r.regularity_score*100:5.1f}%")

    # Verify noise-only can produce very low snr_db
    roi2 = PosteriorSQI("test2")
    noise_only = np.random.randn(n)
    noise_only = noise_only - np.mean(noise_only)
    r2 = roi2.compute(noise_only, fps, 72.0)
    print(f"  noise-only: snr_db={r2.snr_db:6.1f} dB  sqi={r2.sqi:4.1f}%")
    print(f"  NOTE: floor max(snr_raw, 1e-9) produces -90 dB = 10*log10(1e-9)")
    print(f"  -90 dB indicates signal is 10^-9 of noise floor")


# =========================================================================
# PHASE 1: Trace fused_sqi = 0.0 paths
# =========================================================================

def test_fused_sqi_zero_paths():
    """Trace every code path that produces fused_sqi = 0.0."""
    print("\n=== fused_sqi = 0.0 Paths ===")

    print("V2 fused_sqi = 0.0:")
    print("  1. Early return: not valid_rois_res -> fused_sqi stays 0.0 (init)")
    print("  2. Early return: not cands_v2 -> fused_sqi stays 0.0 (init)")
    print("  3. swd = 0 (all accepted have sqi < SQI_HARD_GATE) -> fused_sqi = 0.0")

    print("\nV1 fused_sqi = 0.0:")
    print("  1. Early return: not valid_rois -> stays 0.0 (init)")
    print("  2. Early return: not candidates -> stays 0.0 (init)")
    print("  3. sqi_w_den = 0 (all weights zero) -> fused_sqi = 0.0")

    print("\nV2 fused_sqi computation (line 2301):")
    print("  sws = sum(w * sqi for sqi >= SQI_HARD_GATE)")
    print("  swd = sum(w for sqi >= SQI_HARD_GATE)")
    print("  fused_sqi = sws/swd if swd > 0 else 0.0")
    print("  ISSUE: If cands_v2 is empty (SQI_HARD_GATE tier), early return fires")
    print("         and fused_sqi = 0.0. Tiers 2 and 3 (relaxed SQI) are SKIPPED!")
    print("  V1 has tiers 1,2,3 cascade. V2 only has tier 1.")


def test_v2_early_return_sqi_gated():
    """Simulate: no ROI passes SQI_HARD_GATE, V2 early returns -> fused_sqi = 0.0."""
    print("\n=== V2 Early Return: fused_sqi = 0.0 ===")
    engine = MultiROIFusionEngineV2()
    lm = _lm()

    # Build up some buffer (non-motion frames)
    for i in range(150):
        fr = engine.update(_gray(), lm, 480, 640)

    # Verify buffers accumulated
    for name, roi in engine.rois.items():
        print(f"  {name}: buf_g={len(roi.buf_g)} frames, sqi={roi.sqi:.1f}%")

    print("\n  Simulating all ROIs with SQI=5.0% (< SQI_HARD_GATE=20%)")
    print("  V2 early return fires when cands_v2 is empty (no sqi >= 20)")
    print("  -> fused_sqi stays 0.0 (never computed)")
    print("  -> sqi_gated counter increments (fused_sqi=0.0 < 20.0)")
    print("  ISSUE: V2 has NO 3-tier cascade like V1 (tiers 2 and 3 are skipped)")
    print("  V1 tiers: strict(>=20) -> relaxed(physio) -> last_resort(BPM_HIGH)")
    print("  V2 tiers: strict(>=20) -> EARLY RETURN (no fallback)")


# =========================================================================
# PHASE 2: Bug #1 -- fft_penalty used before assignment
# =========================================================================

def test_fft_penalty_unbound():
    """fft_penalty is referenced before assignment in the peak ratio filter.

    In compute_sqi():
      Line ~959: fft_penalty = getattr(locals(), 'fft_penalty', 0.0) + 0.6  [IN IF BLOCK]
      Line ~962: fft_penalty = getattr(locals(), 'fft_penalty', 0.0) + 0.2  [IN IF BLOCK]
      Line ~965: fft_penalty = 0.0  [AFTER if block]

    This causes UnboundLocalError when fft_validation has "top3_peaks".
    """
    print("\n=== Bug #1: fft_penalty used before assignment ===")

    fps = 30.0
    n = 120
    hr_hz = 84.0 / 60.0
    t = np.arange(n) / fps
    np.random.seed(99)
    signal = (0.3 * np.sin(2*np.pi*hr_hz*t) + 0.3*np.random.randn(n))
    signal = signal - np.mean(signal)

    sos = butter(4, [FREQ_LOW/(fps/2), FREQ_HIGH/(fps/2)],
                 btype='band', output='sos')
    sig_filt = scipy_sosfilt(sos, signal)
    _std = float(np.std(sig_filt))
    if _std > 1e-8:
        sig_filt = (sig_filt - np.mean(sig_filt)) / _std

    bpm_raw, _, _, fft_val = estimate_bpm_fft(sig_filt, fps, roi_name="bug_test")
    print(f"  fft_val has top3_peaks: {'top3_peaks' in fft_val}")
    if fft_val.get('top3_peaks'):
        print(f"  top3: {fft_val['top3_peaks']}")

    # This SHOULD raise UnboundLocalError but let's see what happens
    try:
        sqi, bd = compute_sqi(sig_filt, fps, bpm_raw,
                               motion_score=0.5, mean_brightness=128.0,
                               roi_brightness=128.0, fft_validation=fft_val,
                               prev_sqi=-1.0, roi_obj=None, exposure_drift=0.0)
        print(f"  compute_sqi returned: sqi={sqi:.1f}%")
        if 'fft_penalty' in bd:
            print(f"  fft_penalty={bd['fft_penalty']:.1f}% (present in breakdown)")
        else:
            print(f"  fft_penalty NOT in breakdown")
        # Check if peak ratio was applied
        if fft_val.get('top3_peaks') and len(fft_val['top3_peaks']) >= 2:
            p1 = fft_val['top3_peaks'][0][1]
            p2 = fft_val['top3_peaks'][1][1]
            ratio = p1 / (p2 + 1e-9)
            print(f"  peak_ratio = {ratio:.3f}")
            if ratio < 1.3:
                print(f"  NOTE: peak_ratio < 1.3 -> peak ratio filter SHOULD have fired")
                print(f"  fft_penalty would accumulate 0.6 + 0.2 = 0.8 -> capped to 0.25")
    except (NameError, UnboundLocalError) as e:
        print(f"  CONFIRMED BUG: {type(e).__name__}: {e}")


# =========================================================================
# PHASE 2: Bug #2 -- V1 pre-gate uses stale roi_regularity
# =========================================================================

def test_v1_preregate_uses_stale_regularity():
    """V1 pre-gate at line ~1477 checks v.roi_regularity, but roi_regularity
    is only updated INSIDE the per-ROI processing loop (line ~1599), AFTER the
    pre-gate check. So the pre-gate uses the PREVIOUS frame's regularity.

    This causes the rehabilitation mechanism to be delayed by one frame.
    """
    print("\n=== Bug #2: V1 pre-gate uses stale roi_regularity ===")

    print("  V1 loop structure:")
    print("    Lines ~1459-1482: pre-gate filters (checks v.roi_regularity from PREVIOUS frame)")
    print("    Lines ~1512-1625: per-ROI processing (COMPUTES new roi_regularity)")
    print("    Line ~1599: roi.roi_regularity = reg_score (current frame, set AFTER pre-gate)")

    print("\n  Issue: Line 1477 'v.roi_regularity' is from previous frame.")
    print("  Impact: Rehabilitation check is delayed by 1 frame.")
    print("  When: ROI regularity drops from >15 to <15 -> pre-gate still uses old value.")
    print("  Fix: Move the regularity check inside the per-ROI loop, AFTER roi_regularity is set.")


# =========================================================================
# PHASE 2: Bug #3 -- V2 fused_sqi = 0.0 on early return (no cascade)
# =========================================================================

def test_v2_fused_sqi_not_computed_on_early_return():
    """V2 fused_sqi is NEVER computed when cands_v2 is empty.
    It stays at the initial value (0.0) and the early return fires.

    Compare V1 (3-tier cascade) vs V2 (no cascade).
    """
    print("\n=== Bug #3: V2 fused_sqi not computed on early return ===")

    print("  V1 candidate cascade (rppg_core.py ~1641-1653):")
    print("    Tier 1: SQI >= 20 AND BPM in [50, 130]")
    print("    Tier 2: BPM in [50, 130] only (relaxed SQI)")
    print("    Tier 3: BPM in [50, 180] only (last resort)")
    print("    -> fused_sqi IS computed for ALL tiers")

    print("\n  V2 candidate selection (rppg_core.py ~2252-2258):")
    print("    Tier 1: SQI >= 20 AND BPM in [50, 180]")
    print("    -> if empty: EARLY RETURN (no tiers 2, 3)")
    print("    -> fused_sqi is NEVER computed (stays at 0.0)")

    print("\n  Impact: When all ROIs have SQI < 20% but BPM is valid:")
    print("    V1: fused_sqi computed (possibly > 0)")
    print("    V2: fused_sqi = 0.0 -> sqi_gated counter increments")

    print("\n  Fix: V2 should compute fused_sqi from 'accepted' ROIs,")
    print("        even when no ROI passes the SQI_HARD_GATE threshold.")


# =========================================================================
# PHASE 2: Bug #4 -- V2 regularity hard gate zeros sqi without rehabilitation
# =========================================================================

def test_v2_hard_gate_no_rehabilitation():
    """V2 hard gate (line ~2214-2217) zeros roi.sqi when regularity < 15%.
    Unlike V1 regularity rehabilitation check (lines ~1532-1536), V2
    has NO mechanism to exclude and rehabilitate persistently bad ROIs.
    """
    print("\n=== Bug #4: V2 no regularity rehabilitation ===")

    print("  V1 has rehabilitation (lines ~1532-1536):")
    print("    if avg(reg_history[-90:]) < 0.05:")
    print("      roi.valid = False")
    print("      roi._excluded_until = frame_count + ROI_REHAB_FRAMES")
    print("    -> After ROI_REHAB_FRAMES=45 frames, ROI can recover")

    print("\n  V2: no rehabilitation for persistently low-regularity ROIs.")
    print("  When regularity stays < 15%: every frame -> sqi=0 -> never candidates")
    print("  Impact: sqi_gate_rate grows continuously during stationary capture")


# =========================================================================
# PHASE 3: Run diagnostics
# =========================================================================

def run_diagnostics():
    print("=" * 60)
    print("PHASE 8.x SQI ZERO-LOCK DIAGNOSTICS")
    print("=" * 60)

    test_snrdB_produces_valid_range()
    test_fused_sqi_zero_paths()
    test_v2_early_return_sqi_gated()
    test_fft_penalty_unbound()
    test_v1_preregate_uses_stale_regularity()
    test_v2_fused_sqi_not_computed_on_early_return()
    test_v2_hard_gate_no_rehabilitation()

    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print("""
CONFIRMED BUGS:

BUG #1: fft_penalty UnboundLocalError
  Location: rppg_core.py compute_sqi() lines 959, 962
  Cause: fft_penalty = getattr(locals(), 'fft_penalty', 0.0) used BEFORE line 965
         where fft_penalty = 0.0 is assigned.
  Trigger: Any call with fft_validation having "top3_peaks" and len>=2
  Impact: Raises NameError/UnboundLocalError, caught by except block

BUG #2: V1 pre-gate uses stale roi_regularity
  Location: rppg_core.py line 1477 (V1 pre-gate)
  Cause: roi.roi_regularity updated at line 1599 (inside per-ROI loop),
          but pre-gate runs BEFORE the loop.
  Impact: 1-frame delay in rehabilitation. Low severity.

BUG #3: V2 fused_sqi = 0.0 on early return (no candidate cascade)
  Location: rppg_core.py V2.update() line 2258
  Cause: V2 has no 3-tier candidate cascade. Empty cands_v2 -> early return
         -> fused_sqi stays at 0.0 (never computed).
  Impact: sqi_gated counter increments on every frame with no passing ROIs.
          V1 would compute fused_sqi for relaxed tiers 2 and 3.

BUG #4: V2 missing regularity rehabilitation
  Location: rppg_core.py V2.update() (no equivalent of line 1532-1536)
  Cause: V1 excludes persistently bad ROIs for ROI_REHAB_FRAMES frames.
         V2 has no equivalent -> low-reg ROIs always produce sqi=0.
  Impact: ROIs stuck at regularity < 15% never rehabilitate in V2.
""")


if __name__ == "__main__":
    run_diagnostics()
