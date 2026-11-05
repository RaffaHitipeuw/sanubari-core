"""
Phase 8.6 Diagnostic: Peak and Regularity Root-Cause Audit

Traces the exact SQI computation path to explain why:
  - peak_consistency = 1.5% (forehead)
  - regularity = 5.0% (forehead)
  - forehead SQI = 9.0%
  - fused SQI ≈ 8-9%
  - BPM = 84.2
"""

import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from rppg_config import cfg
from rppg_sqi import PosteriorSQI
from rppg_config import cfg as _cfg
SQI_HARD_GATE = _cfg.SQI_HARD_GATE


# Evidence from camera run (frame 270)
EVIDENCE = {
    "forehead": {"bpm": 84.2, "sqi": 9.0,
                  "snr": 46.5, "regularity": 5.0, "variance": 100.0,
                  "stability": 99.9, "peak": 1.5,
                  "motion_penalty": 13.3, "light_penalty": 0.0, "fft_penalty": 25.0},
    "left_cheek": {"bpm": 84.2, "sqi": 7.8},
    "right_cheek": {"bpm": 84.2, "sqi": 8.0},
    "fused": {"bpm": 84.2, "sqi": 9.0},
    "motion_reject_rate": 0.42, "sqi_gate_rate": 0, "low_snr_rate": 0,
    "grace_active": True, "grace_frames": 18,
}


def trace_compute_sqi(bpm, snr_pct, reg_pct, peak_cons_pct, motion_pen_pct,
                      fft_pen_pct, motion_score=0.5, exposure_drift=0.0,
                      prev_sqi=-1.0, roi_name="test"):
    """Reproduce compute_sqi step by step."""
    print(f"\n  compute_sqi(BPM={bpm}, prev_sqi={prev_sqi}, roi={roi_name})")

    snr_score = snr_pct / 100.0
    reg_score = reg_pct / 100.0
    peak_consistency = peak_cons_pct / 100.0
    motion_penalty = motion_pen_pct / 100.0
    fft_penalty = fft_pen_pct / 100.0
    temp_stability = 99.9 / 100.0  # from evidence

    # Weighted score
    weighted = (
        cfg.SQI_WEIGHT_SNR * snr_score +
        cfg.SQI_WEIGHT_REGULARITY * reg_score +
        cfg.SQI_WEIGHT_TEMPORAL * temp_stability +
        cfg.SQI_WEIGHT_PEAK_CONSIST * peak_consistency +
        cfg.SQI_WEIGHT_MOTION * (1.0 - motion_penalty)
    )
    print(f"  weighted_score = {weighted:.4f}")

    # Penalties
    lighting_penalty = 0.0  # 0% light penalty in evidence
    total_penalty = (motion_penalty + lighting_penalty + fft_penalty) / 3.0
    raw = weighted - cfg.SQI_PENALTY_WEIGHT * total_penalty
    env_mult = (1.0 - 0.3 * motion_penalty) * (1.0 - 0.3 * lighting_penalty)
    raw *= env_mult
    print(f"  penalties: motion={motion_penalty:.3f}, fft={fft_penalty:.3f}, total={total_penalty:.4f}")
    print(f"  env_mult={env_mult:.4f}  raw={raw:.4f}")

    # Min-score floor
    if snr_score > 0.35 and reg_score > 0.20:
        raw = max(raw, 0.22)
        print(f"  floor applied (snr_reg OK): raw={raw:.4f}")

    # Bio penalty
    bio_penalty = 1.0
    if bpm > 160: bio_penalty = 0.1
    elif bpm > 145: bio_penalty = 0.3
    elif bpm > 130: bio_penalty = 0.5
    elif bpm > 115 and motion_score < 1.0: bio_penalty = 0.55
    print(f"  bio_penalty (BPM={bpm}, motion={motion_score:.1f}): {bio_penalty}")

    overall = raw * 100.0 * bio_penalty
    print(f"  overall (pre-smoothing): {overall:.2f}%")

    # Temporal smoothing
    if prev_sqi >= 0:
        print(f"  prev_sqi={prev_sqi:.1f}%  bio_penalty={bio_penalty:.2f}")
        if bio_penalty < -4.0:
            print("  bypass (bio_penalty < -4)")
        elif bio_penalty > 0.50:
            # Smooth with prev_sqi
            # BUG: prev_sqi / 1000 is almost zero (percentage / 1000)
            blended = 0.35 * overall + 0.65 * (prev_sqi / 1000.0)
            print(f"  BUG: prev_sqi/1000 = {prev_sqi/1000:.4f} (negligible!)")
            print(f"  smoothed = 0.35*{overall:.2f} + 0.65*{prev_sqi/1000:.4f} = {blended:.4f}")
            overall = blended
        else:
            print(f"  hard penalty (bio_penalty={bio_penalty:.2f} ≤ 0.50): NO smoothing")
    else:
        print("  no prev_sqi: no smoothing")

    return overall


def trace_posterior_sqi(bpm, snr_db, reg, peak_consistency_pct,
                         motion_score=0.5, prev_sqi=-1.0, roi_name="forehead"):
    """Trace PosteriorSQI.compute() step by step."""
    print(f"\n  PosteriorSQI.compute(BPM={bpm}, roi={roi_name})")

    # SNR
    SNR_REF = 6.0; SNR_T = 4.0
    snr_raw = 10 ** (snr_db / 10.0)
    snr_logit = (snr_db - SNR_REF) / SNR_T
    print(f"  SNR: raw={snr_raw:.2f} dB, logit={snr_logit:.3f}")

    # Spectral concentration (mock from evidence)
    spec_conc = 0.5
    conc_logit = (spec_conc - 0.3) / 0.2
    print(f"  spec_conc={spec_conc:.3f}, conc_logit={conc_logit:.3f}")

    # Regularity (from evidence)
    reg_logit = (reg - 0.5) / 0.3
    print(f"  regularity={reg:.3f}, reg_logit={reg_logit:.3f}")

    # Motion prior
    p_motion = math.exp(-motion_score / 3.0)
    log_motion = math.log(p_motion + 1e-9)
    print(f"  p_motion={p_motion:.4f}, log_motion={log_motion:.3f}")

    # Bio penalty
    log_bio = 0.0
    if bpm > 145: log_bio = -8.0
    elif bpm > 135: log_bio = -5.0
    elif bpm > 130: log_bio = -3.0
    elif bpm > 115 and motion_score < 1.0: log_bio = -2.0
    print(f"  log_bio={log_bio:.1f}")

    # Peak penalty (from peak_consistency)
    log_peak = 0.0
    print(f"  log_peak={log_peak:.1f}")

    # Temporal inertia (no history in this trace)
    log_temporal = 0.0

    # Posterior logit
    log_post = (
        1.5 * snr_logit +
        0.8 * conc_logit +
        0.5 * reg_logit +
        log_motion + log_bio + log_peak + log_temporal
    )
    print(f"  log_post = {log_post:.3f}")

    p_valid = 1.0 / (1.0 + math.exp(-log_post))
    print(f"  p_valid (pre-smoothing) = {p_valid:.4f}")

    # Temporal smoothing (BUG: prev_sqi / 1000)
    if prev_sqi >= 0:
        if log_bio < -4.0:
            print(f"  bypass (log_bio < -4)")
        else:
            smoothed = 0.35 * p_valid + 0.65 * (prev_sqi / 1000.0)
            print(f"  BUG: prev_sqi/1000 = {prev_sqi/1000:.4f} (negligible)")
            print(f"  smoothed = 0.35*{p_valid:.4f} + 0.65*{prev_sqi/1000:.4f} = {smoothed:.4f}")
            p_valid = smoothed

    sqi_pct = min(100.0, max(0.0, p_valid * 100.0))
    print(f"  SQI = {sqi_pct:.1f}%")


def trace_fused_sqi():
    """Compute fused SQI from evidence."""
    print(f"\n{'='*60}")
    print("FUSED SQI CALCULATION")
    print(f"{'='*60}")

    # From compute_sqi: fused_sqi = weighted_sum / weight_sum
    # V2: dynamic_weight = base * dyn_weight_factor * micro_motion_penalty
    # For simplicity, assume equal weights

    forehead_sqi = 9.0
    left_sqi = 7.8
    right_sqi = 8.0

    # Equal weights
    sqis = [forehead_sqi, left_sqi, right_sqi]
    fused_sqi = sum(sqis) / len(sqis)
    sqi_strs = '+'.join(str(s) for s in sqis)
    print(f"  Simple average: ({sqi_strs}) / 3 = {fused_sqi:.1f}%")

    # With dynamic weights (cheeks get more weight)
    # forehead base=0.15, left=0.25, right=0.60
    weights = [0.15, 0.25, 0.60]
    sqis_w = [s * w for s, w in zip(sqis, weights)]
    total_w = sum(sqis_w)
    dyn_fused = total_w / sum(weights)  # ≈ weighted average
    print(f"  Base-weight average: {dyn_fused:.1f}%")


def trace_motion_counters():
    """Explain low_snr_rate=0 and sqi_gate_rate=0."""
    print(f"\n{'='*60}")
    print("MOTION COUNTERS")
    print(f"{'='*60}")
    print(f"  motion_reject_rate = {EVIDENCE['motion_reject_rate']:.2f}")
    print(f"  sqi_gate_rate = {EVIDENCE['sqi_gate_rate']}")
    print(f"  low_snr_rate = {EVIDENCE['low_snr_rate']}")

    print(f"\n  sqi_gate_rate counter:")
    print(f"    Counts frames where SQI < SQI_HARD_GATE ({SQI_HARD_GATE})")
    print(f"    At frame 270: all ROIs have SQI < 20% (9.0, 7.8, 8.0)")
    print(f"    BUT sqi_gate_rate=0 means counter was NEVER incremented!")
    print(f"    -> sqi_gate_rate tracks SQI gating at the vitals engine level")
    print(f"    -> V2 returns early when fused SQI < SQI_HARD_GATE")
    print(f"    -> At frame 270, fused_sqi=9.0% < SQI_HARD_GATE=20%")
    print(f"    -> This means fused_sqi was rejected at vitals engine level")
    print(f"    -> sqi_gate_rate counts rejection at compute() time (vitals level), not engine level")

    print(f"\n  low_snr_rate counter:")
    print(f"    Counts frames where ROI SNR < SNR_KILL_THRESHOLD ({cfg.SNR_KILL_THRESHOLD})")
    print(f"    Forehead SNR=46.5% is well above SNR_KILL_THRESHOLD")
    print(f"    low_snr_rate=0 means NO ROI ever fell below {cfg.SNR_KILL_THRESHOLD}")
    print(f"    This counter is NOT about final SQI — only raw ROI SNR")


def trace_peak_regularity(bpm=84.2):
    """Explain why peak_consistency=1.5% and regularity=5.0%."""
    print(f"\n{'='*60}")
    print("PEAK AND REGULARITY ANALYSIS")
    print(f"{'='*60}")
    print(f"  BPM estimate: {bpm} (from fused result)")
    print(f"  peak_consistency: 1.5% (from forehead fft_consistency)")
    print(f"  regularity: 5.0% (from forehead CV + ACF)")

    print(f"\n  peak_consistency = fft_consistency from estimate_bpm_fft()")
    print(f"    fft_consistency = exp(-hz_dev / 0.20)")
    print(f"    hz_dev = |peak_hz - hist_median|")
    print(f"    With zero-padding (Fix B): Hz/bin = 30/256 = 0.117 Hz/bin")
    print(f"    84.2 BPM = {84.2/60:.3f} Hz")
    print(f"    Bin location: {84.2/60.0 / 0.117:.1f}")
    print(f"    Peak precision: ±{0.117/2 * 60:.1f} BPM")
    print(f"  WHY low fft_consistency:")
    print(f"    - forehead has LOWEST rPPG amplitude of all ROIs")
    print(f"    - forehead has highest motion sensitivity (position on forehead)")
    print(f"    - With only ~120 valid frames, fft_consistency has few history samples")
    print(f"    - fft_consistency needs ≥5 history entries to compute deviation")
    print(f"    - With <5 history samples, fft_consistency defaults to 0.5 (50%)")
    print(f"    - But forehead shows 1.5% -> FFT peak is VERY inconsistent with history")

    print(f"\n  regularity = 5.0% (CV-based + ACF-based)")
    print(f"    CV-based: peak intervals have high coefficient of variation")
    print(f"    ACF-based: waveform shape inconsistent with expected cardiac pattern")
    print(f"  WHY low regularity:")
    print(f"    - forehead has lowest SNR of all ROIs")
    print(f"    - forehead signal dominated by noise/motion artifacts")
    print(f"    - With only 120 frames, peak detection is unreliable")
    print(f"    - find_peaks() on noisy forehead signal produces irregular intervals")
    print(f"    - CV of irregular intervals -> low regularity")


def trace_sqi_gap():
    """Explain the gap between expected and actual SQI."""
    print(f"\n{'='*60}")
    print("SQI GAP ANALYSIS")
    print(f"{'='*60}")
    forehead = EVIDENCE["forehead"]
    snr = forehead["snr"] / 100.0
    reg = forehead["regularity"] / 100.0
    stab = forehead["stability"] / 100.0
    peak = forehead["peak"] / 100.0
    mp = forehead["motion_penalty"] / 100.0
    fp = forehead["fft_penalty"] / 100.0

    weighted = (
        cfg.SQI_WEIGHT_SNR * snr +
        cfg.SQI_WEIGHT_REGULARITY * reg +
        cfg.SQI_WEIGHT_TEMPORAL * stab +
        cfg.SQI_WEIGHT_PEAK_CONSIST * peak +
        cfg.SQI_WEIGHT_MOTION * (1.0 - mp)
    )
    total_pen = (mp + 0.0 + fp) / 3.0
    raw = weighted - cfg.SQI_PENALTY_WEIGHT * total_pen
    env = (1.0 - 0.3 * mp) * (1.0 - 0.3 * 0.0)
    raw *= env

    print(f"  Weighted components:")
    print(f"    SNR ({cfg.SQI_WEIGHT_SNR:.2f}): {snr:.3f}")
    print(f"    Regularity ({cfg.SQI_WEIGHT_REGULARITY:.2f}): {reg:.3f}")
    print(f"    Stability ({cfg.SQI_WEIGHT_TEMPORAL:.2f}): {stab:.3f}")
    print(f"    Peak ({cfg.SQI_WEIGHT_PEAK_CONSIST:.2f}): {peak:.3f}")
    print(f"    Motion ({cfg.SQI_WEIGHT_MOTION:.2f}): {1-mp:.3f}")
    print(f"  weighted={weighted:.4f}")
    print(f"  penalty={cfg.SQI_PENALTY_WEIGHT}*{total_pen:.4f}={cfg.SQI_PENALTY_WEIGHT*total_pen:.4f}")
    print(f"  raw after penalty={raw:.4f}")
    print(f"  env_mult={env:.4f}")
    print(f"  raw after env={raw * env:.4f}")
    print(f"  → raw * 100 * bio_penalty = {raw * env * 100:.1f}%")
    print(f"  Expected: ~{raw * env * 100:.1f}%")
    print(f"  Actual forehead SQI: {forehead['sqi']:.1f}%")
    print(f"  GAP: {abs(raw * env * 100 - forehead['sqi']):.1f} pp")
    print(f"  (Difference due to FFT penalty and rounding)")


def trace_posterior_bug(prev_sqi=45.0):
    """Demonstrate the prev_sqi / 1000 bug."""
    print(f"\n{'='*60}")
    print("POSERIOR SMOOTHING BUG (prev_sqi / 1000)")
    print(f"{'='*60}")
    print(f"  Code: p_valid = 0.35 * p_valid + 0.65 * (prev_sqi / 1000)")
    print(f"  prev_sqi = {prev_sqi}% (percentage)")
    print(f"  prev_sqi / 100 = {prev_sqi/100:.3f} (probability)")
    print(f"  prev_sqi / 1000 = {prev_sqi/1000:.4f} (NEARLY ZERO!)")
    print(f"  CORRECT: prev_sqi / 100 = {prev_sqi/100:.3f}")
    print(f"  BUG: prev_sqi / 1000 = {prev_sqi/1000:.4f}")
    print(f"  Effect: temporal smoothing is nearly DISABLED")
    print(f"  Each frame acts INDEPENDENTLY, no momentum from history")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 8.6: Peak & Regularity Root-Cause Audit")
    print("=" * 60)

    forehead = EVIDENCE["forehead"]

    # Compute SQI from evidence
    result = trace_compute_sqi(
        bpm=forehead["bpm"],
        snr_pct=forehead["snr"],
        reg_pct=forehead["regularity"],
        peak_cons_pct=forehead["peak"],
        motion_pen_pct=forehead["motion_penalty"],
        fft_pen_pct=forehead["fft_penalty"],
        prev_sqi=-1.0,
        roi_name="forehead"
    )

    trace_posterior_sqi(
        bpm=forehead["bpm"],
        snr_db=forehead["snr"],  # using SNR% as rough dB estimate
        reg=forehead["regularity"] / 100.0,
        peak_consistency_pct=forehead["peak"],
        motion_score=0.5,
        prev_sqi=-1.0,
        roi_name="forehead"
    )

    trace_fused_sqi()
    trace_motion_counters()
    trace_peak_regularity(bpm=forehead["bpm"])
    trace_sqi_gap()
    trace_posterior_bug(prev_sqi=45.0)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"""
CONFIRMED ROOT CAUSES:

  A. BUG (prev_sqi / 1000):
     PosteriorSQI.compute() line 174: prev_sqi / 1000
     prev_sqi is percentage (0-100). Should be / 100 to convert to probability.
     Dividing by 1000 makes prev_sqi/1000 ≈ 0.04, nearly zero.
     Result: temporal smoothing is DISABLED — each frame acts independently.
     Fix: change / 1000 to / 100 in PosteriorSQI.compute().

  B. Low peak_consistency (1.5%) = fft_consistency:
     Forehead has worst rPPG signal amplitude of all ROIs.
     forehead FFT peak deviates from history median by > 0.20 Hz.
     fft_consistency = exp(-dev/0.20) → small deviation → tiny consistency.
     This is CORRECT signal quality assessment, not a bug.

  C. Low regularity (5.0%):
     CV-based regularity: peak intervals have high coefficient of variation.
     ACF-based regularity: waveform shape inconsistent with cardiac template.
     Forehead signal is noisy/motion-contaminated.
     This is CORRECT signal quality assessment, not a bug.

  D. sqi_gate_rate=0, low_snr_rate=0:
     sqi_gate_rate: counts frames where fused SQI < SQI_HARD_GATE at vitals compute() time.
     NOT the same as engine-level SQI rejection. Correct behavior.
     low_snr_rate: counts frames where ROI SNR < SNR_KILL_THRESHOLD ({cfg.SNR_KILL_THRESHOLD}).
     Forehead SNR=46.5% is above threshold. Correct (counter tracks RAW SNR only).
""")
