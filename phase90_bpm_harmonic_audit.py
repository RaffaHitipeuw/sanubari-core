#!/usr/bin/env python3
"""
Phase 9.0 - BPM harmonic audit (diagnostic only)

Why this exists
---------------
On every rPPG-10 ROI video the production FFT estimator reports 120-144 BPM
while the subject's ECG says 57-75 BPM, and the detector's own beat stream
implies ~70 BPM. The windowed vote inside `estimate_bpm_fft()` agrees with the
ECG; the final answer does not. This script isolates where the discrepancy is
introduced.

It reproduces, step by step:
  1. the per-window spectral votes of rppg_core.estimate_bpm_fft(),
  2. the value the vote stage selects,
  3. the value after rppg_core._resolve_subharmonic(),
  4. the band energies that drive the harmonic decision,
  5. the ECG reference rate and inter-beat CV for the same subject.

Nothing here modifies production code; it only calls it.

Usage
-----
    python phase90_bpm_harmonic_audit.py \
        --video Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi \
        --ecg  Dataset_rPPG-10/Subject_1/Subject_1_ECG.npy
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from typing import List, Optional

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rppg_core import (  # noqa: E402
    FREQ_HIGH,
    FREQ_LOW,
    _pick_one_peak,
    _resolve_subharmonic,
    apply_windowing,
    cfg,
    estimate_bpm_fft,
)
from signal_validation.pipeline import analyze_video_rois  # noqa: E402
from signal_validation.reference import load_ecg_reference  # noqa: E402


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="BPM harmonic audit")
    ap.add_argument("--video", required=True)
    ap.add_argument("--ecg", default=None)
    ap.add_argument("--fps", type=float, default=None)
    args = ap.parse_args(argv)

    analysis = analyze_video_rois(args.video, roi_name="roi", fps=args.fps)
    sig = analysis.filtered
    fps = analysis.fps
    n = len(sig)

    print(f"video          : {args.video}")
    print(f"samples        : {n}  fps {fps}  duration {n / fps:.1f} s")
    print(f"estimator BPM  : {estimate_bpm_fft(sig, fps, roi_name='audit')[0]:.1f}")
    print(f"beat-implied   : {analysis.ibi_legacy.implied_bpm:.1f} BPM "
          f"(legacy detector, IBI CV {analysis.ibi_legacy.cv:.3f})")

    # --- 1-2: windowed voting, exactly as estimate_bpm_fft does it -----------
    fft_n = max(256, n)
    signal = np.pad(sig, (0, fft_n - n), mode="constant") if fft_n > n else sig
    full_fft = np.abs(np.fft.rfft(apply_windowing(signal, window_type="hann")))
    full_freqs = np.fft.rfftfreq(fft_n, d=1.0 / fps)
    mask = (full_freqs >= FREQ_LOW) & (full_freqs <= FREQ_HIGH)

    win = max(int(fps * cfg.FFT_WINDOW_SEC), 30)
    hop = win // 2
    votes = []
    for start in range(0, n - win + 1, hop):
        seg = apply_windowing(signal[start:start + win], window_type="hann")
        sv = np.abs(np.fft.rfft(seg))
        sf = np.fft.rfftfreq(win, d=1.0 / fps)
        sm = (sf >= FREQ_LOW) & (sf <= FREQ_HIGH)
        hz = _pick_one_peak(sv, sf, sm)
        if hz is not None:
            votes.append(hz)

    arr = np.asarray(votes, dtype=float)
    best, best_n = None, 0
    for hz in arr:
        cluster = arr[np.abs(arr - hz) < cfg.FFT_WINDOW_VOTE_TOL]
        if len(cluster) > best_n:
            best_n, best = len(cluster), float(hz)
    voted = best if best is not None else float(np.median(arr))

    hist = Counter(int(round(hz * 60 / 5.0) * 5) for hz in arr)
    print(f"\nwindow votes   : {len(arr)} windows of {cfg.FFT_WINDOW_SEC:.0f} s")
    print("  BPM histogram: " + ", ".join(f"{k}:{v}" for k, v in sorted(hist.items())))
    print(f"voted peak     : {voted:.4f} Hz = {voted * 60:.1f} BPM "
          f"(cluster {best_n}/{len(arr)} votes)")

    # --- 3-4: the harmonic decision ------------------------------------------
    resolved, was_subharm = _resolve_subharmonic(full_fft, full_freqs, mask, voted)

    def band_energy(center_hz: float, half_bw: float = 0.12) -> float:
        near = ((full_freqs >= center_hz - half_bw)
                & (full_freqs <= center_hz + half_bw) & mask)
        return float(full_fft[near].sum()) if np.any(near) else 0.0

    e_cand = band_energy(voted)
    e_half = band_energy(voted / 2.0)
    e_double = band_energy(voted * 2.0)
    print(f"\nafter _resolve_subharmonic: {resolved:.4f} Hz = {resolved * 60:.1f} BPM "
          f"(changed={was_subharm})")
    print(f"  band energy at candidate {voted:.3f} Hz : {e_cand:.4g}")
    print(f"  band energy at half     {voted/2:.3f} Hz : {e_half:.4g} "
          f"(ratio {e_half / e_cand if e_cand else float('nan'):.3f}, "
          f"threshold {cfg.HARMONIC_SNR_RATIO})")
    print(f"  band energy at double   {voted*2:.3f} Hz : {e_double:.4g} "
          f"(ratio {e_double / e_cand if e_cand else float('nan'):.3f}, "
          f"threshold 0.40)")

    if was_subharm and resolved > voted:
        print("\n  => The DOUBLE branch of _resolve_subharmonic() fired: a harmonic that is "
              ">= 40 % of the fundamental is promoted over the fundamental itself. "
              "In a noisy PPG the 2nd harmonic routinely reaches that level, so the "
              "reported BPM is exactly twice the real one.")

    # --- 5: the reference ----------------------------------------------------
    if args.ecg:
        ecg = load_ecg_reference(args.ecg, ecg_fs=1000.0)
        print(f"\nECG reference  : {os.path.basename(args.ecg)}")
        print(f"  R-peaks      : {len(ecg.r_peak_times_s)}")
        print(f"  mean HR      : {ecg.mean_hr_bpm:.1f} BPM")
        print(f"  SDNN         : {ecg.sdnn_ms:.1f} ms")
        print(f"  inter-beat CV: {ecg.ibi_cv:.3f}  <- physiological irregularity")
        print(f"  detector CV  : {analysis.ibi_legacy.cv:.3f}  <- what the detector reports")
        print("  (a detector CV far above the ECG CV means the irregular intervals are "
              "produced by the detector, not by the recorded heart rhythm)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
