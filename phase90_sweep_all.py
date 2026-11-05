#!/usr/bin/env python3
"""
Phase 9.0 - aggregate the per-subject validation reports into one table.

The per-subject reports (validation_output/subject_<N>_report.md) are produced
by phase90_signal_validation.py. This script parses them and writes a CSV and
a markdown summary so the whole dataset can be scanned at a glance.

It is DIAGNOSTIC ONLY and re-uses the reports; it never touches production
code and never recomputes the analysis.

Usage
-----
    python phase90_sweep_all.py --dir validation_output
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from typing import Dict, List, Optional

VERDICT_RE = re.compile(r"\*\*Verdict:\s*([A-Z]+|OK)\s*[—-]\s*([^(*]+)")
ROI_RE = re.compile(r"^## ROI:\s*`([^`]+)`")
SNR_RE = re.compile(r"SNR=([-\d.na]+) dB, spectral concentration=([\d.]+), ACF regularity=([\d.]+)")
GT_RE = re.compile(
    r"ground truth: (\d+) true beats, (\d+) detected, matched=(\d+), missed=(\d+), "
    r"false=(\d+), sensitivity=([\d.]+), precision=([\d.]+)"
)
LF_RE = re.compile(r"low-frequency/cardiac power ratio=([\d.]+)")
HR_RE = re.compile(r"HR-trace comparison vs ECG: n=(\d+), MAE=([-\d.]+) BPM, bias=([-\d.]+)")
OFFSET_RE = re.compile(r"SEARCHED offset of ([+-][\d.]+) s")
ECG_RE = re.compile(
    r"ECG reference: .*?mean HR ([\d.]+) BPM, SDNN ([\d.]+) ms, ECG inter-beat CV (\d+\.\d+)"
)
IBI_RE = re.compile(r"legacy detector IBI: \{[^}]*'cv': ([\d.]+)[^}]*'implied_bpm': ([\d.]+)")
FFT_RE = re.compile(r"\| bpm_fft \| ([\d.]+) \|")
REG_RE = re.compile(r"\| regularity_legacy_pct \| ([\d.]+) \|")
REGP_RE = re.compile(r"\| regularity_posterior_pct \| ([\d.]+) \|")
SQI_RE = re.compile(r"\| sqi_legacy \| ([\d.]+) \|")
SQIP_RE = re.compile(r"\| sqi_posterior \| ([\d.]+) \|")
NPK_RE = re.compile(r"\| n_peaks_legacy \| (\d+) \|")


def _num(x: str) -> Optional[float]:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def parse_report(path: str) -> List[Dict]:
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()

    subject = os.path.basename(path).split("_")[1]
    offset = None
    m = OFFSET_RE.search(text)
    if m:
        offset = float(m.group(1))

    hr_cmp = {}
    m = HR_RE.search(text)
    if m:
        hr_cmp = {"n": int(m.group(1)), "mae_bpm": float(m.group(2)),
                  "bias_bpm": float(m.group(3))}

    ecg = {}
    m = ECG_RE.search(text)
    if m:
        ecg = {"hr_bpm": float(m.group(1)), "sdnn_ms": float(m.group(2)),
               "ibi_cv": float(m.group(3))}

    rows: List[Dict] = []
    # Split the report into per-ROI sections.
    chunks = re.split(r"^## ROI:", text, flags=re.M)[1:]
    for chunk in chunks:
        roi = (ROI_RE.search(chunk) or [None, "roi"])[1]
        verdict = VERDICT_RE.search(chunk)
        snr = SNR_RE.search(chunk)
        gt = GT_RE.search(chunk)
        lf = LF_RE.search(chunk)
        ibi = IBI_RE.search(chunk)
        fft = FFT_RE.search(chunk)
        rows.append({
            "subject": int(subject),
            "roi": roi,
            "verdict": verdict.group(1) if verdict else "?",
            "verdict_label": (verdict.group(2).strip() if verdict else "?"),
            "snr_db": _num(snr.group(1)) if snr else None,
            "spectral_concentration": _num(snr.group(2)) if snr else None,
            "acf_regularity": _num(snr.group(3)) if snr else None,
            "n_true_beats": int(gt.group(1)) if gt else None,
            "n_detected": int(gt.group(2)) if gt else None,
            "n_matched": int(gt.group(3)) if gt else None,
            "sensitivity": _num(gt.group(6)) if gt else None,
            "precision": _num(gt.group(7)) if gt else None,
            "lf_ratio": _num(lf.group(1)) if lf else None,
            "ecg_hr_mae_bpm": hr_cmp.get("mae_bpm"),
            "ecg_hr_bias_bpm": hr_cmp.get("bias_bpm"),
            "searched_offset_s": offset,
            "ecg_hr_bpm": ecg.get("hr_bpm"),
            "ecg_sdnn_ms": ecg.get("sdnn_ms"),
            "ecg_ibi_cv": ecg.get("ibi_cv"),
            "detector_ibi_cv": _num(ibi.group(1)) if ibi else None,
            "detector_implied_bpm": _num(ibi.group(2)) if ibi else None,
            "fft_bpm": _num(fft.group(1)) if fft else None,
            "regularity_legacy_pct": _num(REG_RE.search(chunk).group(1)) if REG_RE.search(chunk) else None,
            "regularity_posterior_pct": _num(REGP_RE.search(chunk).group(1)) if REGP_RE.search(chunk) else None,
            "sqi_legacy": _num(SQI_RE.search(chunk).group(1)) if SQI_RE.search(chunk) else None,
            "sqi_posterior": _num(SQIP_RE.search(chunk).group(1)) if SQIP_RE.search(chunk) else None,
            "n_peaks_legacy": int(NPK_RE.search(chunk).group(1)) if NPK_RE.search(chunk) else None,
        })
    return rows


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Aggregate Phase 9.0 subject reports")
    ap.add_argument("--dir", default="validation_output")
    args = ap.parse_args(argv)

    reports = sorted(
        f for f in os.listdir(args.dir)
        if f.startswith("subject_") and f.endswith("_report.md")
    )
    if not reports:
        print(f"No subject reports found in {args.dir}. Run the sweep first:")
        print("  for s in $(seq 1 27); do python phase90_signal_validation.py "
              "--out validation_output subject --subject $s --search-offset; done")
        return 1

    rows: List[Dict] = []
    for name in reports:
        rows.extend(parse_report(os.path.join(args.dir, name)))

    csv_path = os.path.join(args.dir, "sweep_summary.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Aggregate
    counts: Dict[str, int] = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    def _stat(key):
        vals = [r[key] for r in rows if r[key] is not None]
        if not vals:
            return "n/a"
        vals.sort()
        return (f"{vals[0]:.2f} / {vals[len(vals)//2]:.2f} / {vals[-1]:.2f}")

    lines = ["# Phase 9.0 - dataset sweep summary", ""]
    lines.append(f"Reports parsed: {len(reports)} subjects, {len(rows)} ROI analyses.")
    lines.append("")
    lines.append("## Verdict distribution")
    lines.append("")
    lines.append("| verdict | count | meaning |")
    lines.append("| --- | --- | --- |")
    meaning = {
        "OK": "signal usable, detection consistent with the reference",
        "A": "genuinely poor signal quality",
        "B": "peak-detection failure",
        "C": "preprocessing or ROI artifact",
        "D": "inconclusive - reference sensor required",
    }
    for key in sorted(counts):
        lines.append(f"| {key} | {counts[key]} | {meaning.get(key, '')} |")
    lines.append("")
    lines.append("## Metric ranges (min / median / max)")
    lines.append("")
    lines.append("| metric | min / median / max |")
    lines.append("| --- | --- |")
    lines.append(f"| SNR (dB) | {_stat('snr_db')} |")
    lines.append(f"| spectral concentration | {_stat('spectral_concentration')} |")
    lines.append(f"| ACF regularity | {_stat('acf_regularity')} |")
    lines.append(f"| low-frequency/cardiac power ratio | {_stat('lf_ratio')} |")
    lines.append(f"| ECG beat sensitivity | {_stat('sensitivity')} |")
    lines.append(f"| ECG beat precision | {_stat('precision')} |")
    lines.append(f"| ECG HR-trace MAE (BPM) | {_stat('ecg_hr_mae_bpm')} |")
    lines.append(f"| ECG HR-trace bias (BPM) | {_stat('ecg_hr_bias_bpm')} |")
    lines.append(f"| ECG mean HR (BPM) | {_stat('ecg_hr_bpm')} |")
    lines.append(f"| ECG inter-beat CV (physiological) | {_stat('ecg_ibi_cv')} |")
    lines.append(f"| Detector IBI CV (as measured) | {_stat('detector_ibi_cv')} |")
    lines.append(f"| Production FFT BPM | {_stat('fft_bpm')} |")
    lines.append(f"| Detector beat-implied BPM | {_stat('detector_implied_bpm')} |")
    lines.append(f"| Production legacy regularity (%) | {_stat('regularity_legacy_pct')} |")
    lines.append(f"| Production posterior regularity (%) | {_stat('regularity_posterior_pct')} |")
    lines.append(f"| Production legacy SQI | {_stat('sqi_legacy')} |")
    lines.append(f"| Production posterior SQI | {_stat('sqi_posterior')} |")
    lines.append("")
    lines.append("## Per-ROI detail")
    lines.append("")
    lines.append("| subject | roi | verdict | SNR dB | spec conc | ACF reg | sens | prec | det CV | ECG CV | ECG HR | FFT BPM | det BPM | ECG HR MAE |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        lines.append(
            f"| {r['subject']} | {r['roi']} | {r['verdict']} | {r['snr_db']} | "
            f"{r['spectral_concentration']} | {r['acf_regularity']} | {r['sensitivity']} | "
            f"{r['precision']} | {r['detector_ibi_cv']} | {r['ecg_ibi_cv']} | "
            f"{r['ecg_hr_bpm']} | {r['fft_bpm']} | {r['detector_implied_bpm']} | "
            f"{r['ecg_hr_mae_bpm']} |"
        )
    lines.append("")
    lines.append(
        "All interval and beat statistics describe the DETECTOR's output on these "
        "recordings. The ECG-video start offset is not published for rPPG-10, so the "
        "beat-level columns are hypothesis-level comparisons, not verified "
        "synchronisation. No statement about any subject's heart rhythm is made."
    )
    lines.append("")

    md_path = os.path.join(args.dir, "sweep_summary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n".join(lines[:40]))
    print(f"\n[written] {csv_path}")
    print(f"[written] {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
