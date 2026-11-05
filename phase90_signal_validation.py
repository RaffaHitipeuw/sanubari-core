#!/usr/bin/env python3
"""
Phase 9.0 — RPPG Signal Validation (offline diagnostic CLI)

Runs the offline signal audit over:

  * synthetic signals with known ground truth,
  * prerecorded videos (including the rPPG-10 ROI videos),
  * recorded-session CSV exports,
  * optionally an ECG reference from the rPPG-10 dataset.

This script is DIAGNOSTIC. It does not modify production behaviour, does not
change any quality threshold, and does not write into the production tree
other than the report file the user asks for.

Examples
--------
    # Synthetic ground-truth sweep
    python phase90_signal_validation.py synthetic

    # One rPPG-10 ROI video, compared against that subject's ECG
    python phase90_signal_validation.py video \
        --video Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi \
        --ecg  Dataset_rPPG-10/Subject_1/Subject_1_ECG.npy \
        --roi forehead --search-offset

    # Every ROI of one rPPG-10 subject
    python phase90_signal_validation.py subject --subject 1 --dataset Dataset_rPPG-10

    # A live-session export (raw_signals.csv from ReproducibilityLogger)
    python phase90_signal_validation.py session --csv rppg_session_123/raw_signals.csv
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Optional

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from signal_validation import (  # noqa: E402
    analyze_roi_series,
    analyze_session_csv,
    analyze_video_rois,
    build_case,
    classify_roi,
    compare_beats,
    compare_hr_traces,
    export_roi_signals,
    load_ecg_reference,
    match_peaks,
    match_peaks_with_latency,
    render_report,
    SYNTHETIC_CASES,
)
from signal_validation.pipeline import _read_video_channels  # noqa: E402


# ── Synthetic sweep ───────────────────────────────────────────────────────────

def run_synthetic(args) -> str:
    from signal_validation.report import Classification

    rows: List[dict] = []
    classifications: List[Classification] = []
    analyses = []

    for name in SYNTHETIC_CASES:
        case = build_case(
            name,
            duration_s=args.duration,
            fps=args.fps,
            bpm=args.bpm,
            seed=args.seed,
        )
        # Feed the synthetic trace through the production preprocessing and
        # both production peak detectors.
        sig = case.signal
        r = sig + 120.0
        g = sig + 100.0
        b = sig + 90.0
        analysis = analyze_roi_series(
            r, g, b, fps=case.fps,
            roi_name=f"synthetic:{name}",
            source=f"synthetic({name})",
        )
        analyses.append(analysis)

        matches: Dict[str, tuple] = {}
        for detector, peaks in (
            ("legacy", analysis.peaks_legacy_s),
            ("posterior", analysis.peaks_posterior_s),
        ):
            tm, latency = match_peaks_with_latency(
                peaks, case.true_peak_times_s, tolerance_s=args.tolerance
            )
            matches[detector] = (tm, latency)
            rows.append({
                "case": name,
                "detector": detector,
                "expected_category": case.expected_category,
                **tm.as_dict(),
                "latency_s": round(latency, 3),
                "ibi_cv": round(analysis.ibi_legacy.cv if detector == "legacy"
                                else analysis.ibi_posterior.cv, 4),
                "acf_regularity": round(analysis.acf.acf_regularity, 4),
                "snr_db": round(analysis.snr_db, 2),
                "regularity_legacy_pct": round(analysis.regularity_legacy, 2),
                "regularity_posterior_pct": round(analysis.regularity_posterior, 2),
                "bpm_fft": round(analysis.bpm_fft, 2),
            })

        # The classifier is fed the LEGACY detector's match, because the
        # legacy detector is the one whose beats feed the production
        # regularity breakdown; the posterior detector's numbers are reported
        # alongside but do not drive the verdict.
        cls = classify_roi(analysis, truth_match=matches["legacy"][0],
                           reference_available=bool(case.true_peak_times_s))
        classifications.append(cls)
        for detector in ("legacy", "posterior"):
            for row in rows:
                if row["case"] == name and row["detector"] == detector:
                    row["category"] = cls.category
                    row["category_expected"] = case.expected_category
                    row["category_match"] = (cls.category == case.expected_category)

    lines = ["# Phase 9.0 — Synthetic ground-truth validation", ""]
    lines.append("| case | detector | true | detected | matched | missed | false | sens | prec | latency s | IBI CV | ACF reg | SNR dB | verdict | expected |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r_ in rows:
        lines.append(
            f"| {r_['case']} | {r_['detector']} | {r_['n_true']} | {r_['n_detected']} | "
            f"{r_['n_matched']} | {r_['n_missed']} | {r_['n_false']} | "
            f"{r_['sensitivity']} | {r_['precision']} | {r_['latency_s']} | "
            f"{r_['ibi_cv']} | {r_['acf_regularity']} | {r_['snr_db']} | "
            f"{r_.get('category', 'n/a')} | {r_.get('category_expected', 'n/a')} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- `clean` is the control: both detectors should score sensitivity and precision near 1.0."
    )
    lines.append(
        "- `noisy`, `flat`, `white_noise` are category-A cases: there is no usable pulse to find, "
        "so low sensitivity is the CORRECT behaviour, not a detector bug."
    )
    lines.append(
        "- `missing_peaks` and `extra_peaks` are category-B cases: the pulse is present and the "
        "detector is expected to miss / invent beats. Sensitivity < 1 on `missing_peaks` and "
        "precision < 1 on `extra_peaks` are the detector behaving as specified, and the magnitude "
        "of the error is what the audit quantifies."
    )
    lines.append(
        "- `motion` is a category-C case: the pulse is still recoverable but the environment "
        "degrades the measurement."
    )
    lines.append("")
    lines.append(
        "A detector that reports high sensitivity on `flat`/`white_noise` would be the bug; "
        "a detector that reports low sensitivity on `clean` would be the bug."
    )
    lines.append("")

    if args.out:
        os.makedirs(args.out, exist_ok=True)
        path = os.path.join(args.out, "synthetic_results.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"rows": rows}, f, indent=2)
        lines.append(f"Machine-readable results: `{path}`")
        lines.append("")

    return "\n".join(lines)


# ── Video / subject analysis ──────────────────────────────────────────────────

def _analyse_video_with_ecg(
    video_path: str,
    roi_name: str,
    ecg_path: Optional[str],
    args,
) -> tuple:
    analysis = analyze_video_rois(
        video_path, roi_name=roi_name, fps=args.fps, max_frames=args.max_frames
    )

    truth_match = None
    hr_cmp = None
    offset_used = 0.0
    ecg = None
    if ecg_path:
        ecg = load_ecg_reference(
            ecg_path,
            ecg_fs=args.ecg_fs,
            offset_sec=args.offset,
            offset_known=args.offset_known,
        )
        truth_match, offset_used = compare_beats(
            analysis.peaks_legacy_s, ecg,
            tolerance_s=args.tolerance,
            search_offset=args.search_offset,
        )
        # Video HR trace from the FFT estimator, windowed like the ECG trace.
        video_times, video_bpm = _video_hr_trace(analysis, args.hr_window, args.hr_step)
        hr_cmp = compare_hr_traces(video_times, video_bpm, ecg, tolerance_s=args.hr_tolerance)

    classification = classify_roi(
        analysis,
        truth_match=truth_match,
        reference_available=ecg is not None,
    )
    return analysis, classification, truth_match, hr_cmp, ecg, offset_used


def _video_hr_trace(analysis, window_sec: float, step_sec: float):
    """Sliding-window BPM from the production FFT estimator over the trace."""
    from rppg_core import estimate_bpm_fft

    sig = analysis.filtered
    fps = analysis.fps
    win = max(int(window_sec * fps), 30)
    step = max(int(step_sec * fps), 1)
    times, bpms = [], []
    for start in range(0, max(len(sig) - win + 1, 1), step):
        seg = sig[start:start + win]
        if len(seg) < 30:
            break
        bpm, _, _, _ = estimate_bpm_fft(seg, fps, roi_name="offline")
        if bpm and bpm > 0:
            times.append((start + win / 2) / fps)
            bpms.append(float(bpm))
    return times, bpms


def _export(args, analyses, prefix: str) -> List[str]:
    """Write raw/filtered signals and peak timestamps for every ROI."""
    if not getattr(args, "export_signals", None):
        return []
    out: List[str] = []
    for a in analyses:
        tag = f"{prefix}_{a.roi_name}" if prefix else a.roi_name
        paths = export_roi_signals(a, args.export_signals, tag=tag)
        out.append(
            f"Exported ROI '{a.roi_name}': {paths['signal']}, {paths['peaks']}, {paths['meta']}"
        )
    return out


def run_video(args) -> str:
    analysis, classification, truth_match, hr_cmp, ecg, offset_used = \
        _analyse_video_with_ecg(args.video, args.roi, args.ecg, args)

    notes: List[str] = []
    notes.extend(_export(args, [analysis],
                         prefix=os.path.splitext(os.path.basename(args.video))[0]))
    if ecg is not None:
        notes.append(
            f"ECG reference: {os.path.basename(ecg.path)} — {len(ecg.r_peak_times_s)} R-peaks, "
            f"mean HR {ecg.mean_hr_bpm:.1f} BPM, SDNN {ecg.sdnn_ms:.1f} ms."
        )
        if args.search_offset:
            notes.append(
                f"Beat comparison used a SEARCHED offset of {offset_used:+.2f} s. This is a "
                "hypothesis fitted to the data, not a verified synchronisation; the "
                "dataset does not publish the ECG-video start offset."
            )
        if hr_cmp:
            notes.append(
                f"HR-trace comparison vs ECG: n={hr_cmp.get('n_pairs')}, "
                f"MAE={hr_cmp.get('mae_bpm', float('nan')):.2f} BPM, "
                f"bias={hr_cmp.get('bias_bpm', float('nan')):+.2f} BPM, "
                f"r={hr_cmp.get('pearson_r', float('nan')):.3f}."
            )
    notes.append(
        "All interval statistics describe the detector's output on this recording. "
        "They are not a measurement of the subject's heart rhythm."
    )

    return render_report(
        [analysis], [classification],
        title=f"Phase 9.0 — Signal validation: {os.path.basename(args.video)}",
        extra_notes=notes,
    )


def run_subject(args) -> str:
    """Analyse every ROI video of one rPPG-10 subject against that subject's ECG."""
    root = args.dataset
    subject_dir = os.path.join(root, f"Subject_{args.subject}")
    if not os.path.isdir(subject_dir):
        raise SystemExit(f"Subject directory not found: {subject_dir}")

    ecg_path = os.path.join(subject_dir, f"Subject_{args.subject}_ECG.npy")
    if not os.path.exists(ecg_path):
        ecg_path = None

    analyses, classifications = [], []
    skipped: List[str] = []
    for roi_key, roi_name in (("Forehead", "forehead"), ("Cheek1", "cheek_left"), ("Cheek2", "cheek_right")):
        matches = [f for f in os.listdir(subject_dir) if roi_key.lower() in f.lower() and f.lower().endswith(".avi")]
        if not matches:
            continue
        video_path = os.path.join(subject_dir, matches[0])
        try:
            a, c, _tm, _hr, _e, _o = _analyse_video_with_ecg(video_path, roi_name, ecg_path, args)
        except (ValueError, OSError) as exc:
            # Unreadable or empty ROI file (some rPPG-10 subjects ship 0-byte
            # videos). Report it and continue instead of aborting the subject.
            skipped.append(f"{roi_name}: {os.path.basename(video_path)} ({exc})")
            continue
        analyses.append(a)
        classifications.append(c)

    notes = [
        f"Subject {args.subject} of {root}. Each ROI video is a 64x64 crop of one face "
        "region, so the whole frame is treated as the ROI.",
    ]
    notes.extend(_export(args, analyses, prefix=f"subject{args.subject}"))
    for s in skipped:
        notes.append(f"SKIPPED ROI - {s}")
    if ecg_path:
        ecg = load_ecg_reference(ecg_path, ecg_fs=1000.0)
        notes.append(
            f"ECG reference: {os.path.basename(ecg.path)} - {len(ecg.r_peak_times_s)} "
            f"R-peaks, mean HR {ecg.mean_hr_bpm:.1f} BPM, SDNN {ecg.sdnn_ms:.1f} ms, "
            f"ECG inter-beat CV {ecg.ibi_cv:.3f}."
        )
        det_cv = [a.ibi_legacy.cv for a in analyses if np.isfinite(a.ibi_legacy.cv)]
        fft_bpm = [a.bpm_fft for a in analyses if np.isfinite(a.bpm_fft)]
        imp_bpm = [a.ibi_legacy.implied_bpm for a in analyses if np.isfinite(a.ibi_legacy.implied_bpm)]
        if det_cv:
            notes.append(
                f"Detector IBI CV across ROIs: {min(det_cv):.3f}-{max(det_cv):.3f} "
                f"(ECG inter-beat CV {ecg.ibi_cv:.3f}). A detector CV far above the "
                "ECG CV means the irregularity is produced by the detector."
            )
        if fft_bpm and imp_bpm:
            notes.append(
                f"Production FFT BPM: {sorted(fft_bpm)}; detector beat-implied BPM: "
                f"{[round(b, 1) for b in imp_bpm]}; ECG mean HR {ecg.mean_hr_bpm:.1f} BPM."
            )
    if ecg_path:
        notes.append(
            "The ECG-video start offset for rPPG-10 is not published; beat-level "
            "comparisons are therefore hypothesis-level only."
        )
    notes.append(
        "All interval statistics describe the detector's output on this recording. "
        "They are not a measurement of the subject's heart rhythm."
    )
    return render_report(
        analyses, classifications,
        title=f"Phase 9.0 — Signal validation: Subject {args.subject}",
        extra_notes=notes,
    )


def run_session(args) -> str:
    results = analyze_session_csv(args.csv, fps=args.fps)
    analyses = list(results.values())
    classifications = [classify_roi(a) for a in analyses]
    notes = [
        f"Source: {os.path.basename(args.csv)} (ReproducibilityLogger raw_signals.csv export).",
        "No ground truth / reference sensor was supplied for this session, so every "
        "verdict is D (inconclusive) unless the signal itself is clearly unusable.",
    ]
    notes.extend(_export(args, analyses,
                          prefix=os.path.splitext(os.path.basename(args.csv))[0]))
    return render_report(
        analyses, classifications,
        title=f"Phase 9.0 — Signal validation: {os.path.basename(args.csv)}",
        extra_notes=notes,
    )


# ── CLI ───────────────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="Phase 9.0 — offline rPPG signal validation (diagnostic only)",
    )
    p.add_argument("--out", default="validation_output", help="output directory for machine-readable results")
    p.add_argument("--export-signals", default=None,
                   help="directory to export raw/filtered signals, peak timestamps and "
                        "per-ROI metrics as CSV/JSON (video, subject and session modes)")

    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("synthetic", help="run the controlled synthetic ground-truth suite")
    s.add_argument("--duration", type=float, default=30.0)
    s.add_argument("--fps", type=float, default=30.0)
    s.add_argument("--bpm", type=float, default=None,
                   help="base BPM for the synthetic cases (default: per-case rate)")
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--tolerance", type=float, default=0.15)
    s.set_defaults(func=run_synthetic)

    def add_common(sp):
        sp.add_argument("--fps", type=float, default=None, help="override video fps")
        sp.add_argument("--max-frames", type=int, default=None)
        sp.add_argument("--tolerance", type=float, default=0.15, help="beat match tolerance (s)")
        sp.add_argument("--ecg", default=None, help="ECG .npy reference")
        sp.add_argument("--ecg-fs", type=float, default=1000.0)
        sp.add_argument("--offset", type=float, default=0.0, help="ECG-video offset (s)")
        sp.add_argument("--offset-known", action="store_true",
                        help="assert the ECG-video offset is verified")
        sp.add_argument("--search-offset", action="store_true",
                        help="search for the best-fitting beat offset (hypothesis only)")
        sp.add_argument("--hr-window", type=float, default=10.0)
        sp.add_argument("--hr-step", type=float, default=1.0)
        sp.add_argument("--hr-tolerance", type=float, default=3.0)

    v = sub.add_parser("video", help="analyse one video as a single ROI")
    v.add_argument("--video", required=True)
    v.add_argument("--roi", default="roi")
    add_common(v)
    v.set_defaults(func=run_video)

    j = sub.add_parser("subject", help="analyse all ROI videos of one rPPG-10 subject")
    j.add_argument("--subject", required=True)
    j.add_argument("--dataset", default="Dataset_rPPG-10")
    add_common(j)
    j.set_defaults(func=run_subject)

    c = sub.add_parser("session", help="analyse a recorded-session raw_signals.csv")
    c.add_argument("--csv", required=True)
    c.add_argument("--fps", type=float, default=30.0)
    c.set_defaults(func=run_session)

    args = p.parse_args(argv)
    try:
        report = args.func(args)
    except (ValueError, OSError) as exc:
        print(f"[error] {exc}")
        return 2
    print(report)
    if args.command in ("video", "subject", "session"):
        os.makedirs(args.out, exist_ok=True)
        stem = f"{args.command}_report"
        if args.command == "subject":
            stem = f"subject_{args.subject}_report"
        path = os.path.join(args.out, f"{stem}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n[report written] {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
