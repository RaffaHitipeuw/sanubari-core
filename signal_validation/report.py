"""
A/B/C/D classification and report rendering for Phase 9.0.

Categories
----------
OK. Usable signal, detection consistent with the reference
   The pulse is recoverable (good SNR, spectral concentration and ACF
   periodicity) and the detected beats agree with a reference. Nothing is
   limiting the measurement here.

A. Genuinely poor signal quality
   The optical signal itself does not carry a usable pulse: low SNR, weak
   spectral concentration, weak autocorrelation periodicity, or a flat /
   noise-dominated trace.

B. Peak-detection failure
   The signal carries a usable pulse (strong ACF periodicity, adequate SNR)
   but the production peak detector mis-locates beats: many missed beats,
   many false beats, or the two production detectors disagree strongly.

C. Preprocessing or ROI artifact
   The pulse is present and detectable, but the surrounding acquisition is
   compromised: motion, exposure drift, saturation, near-flat ROI.

D. Inconclusive — needs a reference sensor
   The offline evidence does not separate the candidate causes. A reference
   (ECG or another pulse sensor) is required to decide.

The classifier never claims a physiological conclusion. Irregular detected
intervals are reported as a measurement property of the detector, not as
evidence about a human heart rhythm.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np

from .metrics import PeakMatch
from .pipeline import ROIAnalysis


# Thresholds (documented so the classification is auditable and adjustable).
SNR_POOR_DB = 3.0            # below this the pulse is not recoverable
SNR_WEAK_DB = 6.0            # below this the signal is questionable
ACF_WEAK = 0.15              # ACF regularity floor (same constant production uses)
SPEC_CONC_WEAK = 0.10        # band power share of the cardiac peak
LF_RATIO_HIGH = 0.40         # low-frequency vs cardiac power in the raw channel
EXPOSURE_HIGH = 8.0          # brightness drift
SATURATION_HIGH = 0.10       # fraction of clipped frames
FLAT_HIGH = 0.50             # fraction of colour-flat frames


@dataclass
class Classification:
    """The audit verdict for one ROI."""

    roi_name: str = ""
    category: str = "D"
    label: str = ""
    confidence: str = "low"
    evidence: List[str] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "roi_name": self.roi_name,
            "category": self.category,
            "label": self.label,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
            "caveats": list(self.caveats),
        }


def _fmt(x, digits=3):
    if x is None:
        return "n/a"
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    if not np.isfinite(v):
        return "n/a"
    return f"{v:.{digits}f}"


def classify_roi(
    analysis: ROIAnalysis,
    truth_match: Optional[PeakMatch] = None,
    reference_available: bool = False,
) -> Classification:
    """
    Classify one ROI into A/B/C/D.

    Parameters
    ----------
    analysis        the offline analysis of the ROI
    truth_match     optional result of matching detected peaks against a
                    known ground truth (synthetic pulses or ECG beats)
    reference_available
                    True when a real reference sensor (ECG) is available for
                    this ROI. Without it, several signals stay ambiguous and
                    the verdict degrades to D.
    """
    c = Classification(roi_name=analysis.roi_name)
    ev = c.evidence
    cav = c.caveats

    acf_reg = analysis.acf.acf_regularity
    snr = analysis.snr_db
    cv = analysis.ibi_legacy.cv
    n_peaks = len(analysis.peaks_legacy_s)

    ev.append(
        f"SNR={_fmt(snr, 2)} dB, spectral concentration={_fmt(analysis.spectral_concentration, 3)}, "
        f"ACF regularity={_fmt(acf_reg, 3)} (peak {_fmt(analysis.acf.acf_peak_value, 3)} @ "
        f"{_fmt(analysis.acf.acf_peak_bpm, 1)} BPM)"
    )
    ev.append(
        f"legacy detector: {n_peaks} peaks, IBI CV={_fmt(cv, 3)}, "
        f"implied BPM={_fmt(analysis.ibi_legacy.implied_bpm, 1)}; "
        f"FFT BPM={_fmt(analysis.bpm_fft, 1)}"
    )
    ev.append(
        f"posterior detector: {len(analysis.peaks_posterior_s)} peaks, "
        f"IBI CV={_fmt(analysis.ibi_posterior.cv, 3)}; "
        f"regularity legacy={_fmt(analysis.regularity_legacy, 1)}% "
        f"posterior={_fmt(analysis.regularity_posterior, 1)}%"
    )
    ev.append(
        f"motion proxy: frame-diff mean={_fmt(analysis.frame_diff_mean, 4)} "
        f"p95={_fmt(analysis.frame_diff_p95, 4)}; low-frequency/cardiac power "
        f"ratio={_fmt(analysis.lf_ratio, 3)}; exposure drift="
        f"{_fmt(analysis.exposure_drift, 2)}; brightness mean="
        f"{_fmt(analysis.mean_brightness, 1)} std={_fmt(analysis.brightness_std, 1)}; "
        f"saturated={_fmt(analysis.saturation_fraction, 3)}; flat={_fmt(analysis.flat_fraction, 3)}"
    )

    # ── Evidence from a known ground truth, when available ──────────────────
    detection_failed = False
    if truth_match is not None:
        sens = truth_match.sensitivity
        prec = truth_match.precision
        ev.append(
            f"ground truth: {truth_match.n_true} true beats, {truth_match.n_detected} detected, "
            f"matched={truth_match.n_matched}, missed={truth_match.n_missed}, "
            f"false={truth_match.n_false}, sensitivity={_fmt(sens, 3)}, "
            f"precision={_fmt(prec, 3)}, "
            f"mean |interval error|={_fmt(truth_match.mean_abs_interval_error_s, 4)} s"
        )
        if truth_match.n_true >= 5 and (sens < 0.90 or prec < 0.90):
            detection_failed = True
    else:
        cav.append(
            "No ground truth / reference sensor for this ROI: the detector cannot be "
            "scored, so peak-level failure cannot be separated from a weak signal."
        )

    # ── Signal-quality indicators ──────────────────────────────────────────
    # "Poor" means the recording does not carry a usable pulse: either the
    # pulse is not recoverable at all (SNR < 3 dB, no cardiac-band energy, no
    # ACF periodicity, a flat ROI, fewer than 3 detected beats) or it is only
    # marginally recoverable (SNR < 6 dB).
    poor_signal = (
        (np.isfinite(snr) and snr < SNR_POOR_DB)
        or (np.isfinite(snr) and snr < SNR_WEAK_DB)
        or (np.isfinite(analysis.spectral_concentration) and analysis.spectral_concentration < SPEC_CONC_WEAK)
        or acf_reg < ACF_WEAK
        or (np.isfinite(analysis.flat_fraction) and analysis.flat_fraction > FLAT_HIGH)
        or n_peaks < 3
    )

    # ── Preprocessing / ROI artifact indicators ─────────────────────────────
    # NOTE: the raw frame-to-frame difference is reported but NOT used as an
    # artifact trigger. It is dominated by pixel noise (a white-noise trace
    # inflates it as much as real motion does) and it is not comparable
    # between a unit-amplitude synthetic trace and a 0-255 video. The
    # dimensionless low-frequency/cardiac power ratio is used instead.
    artifact = (
        (np.isfinite(analysis.lf_ratio) and analysis.lf_ratio > LF_RATIO_HIGH)
        or (np.isfinite(analysis.exposure_drift) and analysis.exposure_drift > EXPOSURE_HIGH)
        or (np.isfinite(analysis.saturation_fraction) and analysis.saturation_fraction > SATURATION_HIGH)
        or (np.isfinite(analysis.flat_fraction) and analysis.flat_fraction > FLAT_HIGH)
    )

    # ── Decide ──────────────────────────────────────────────────────────────
    # Precedence: a signal that carries no usable pulse is category A even
    # when the acquisition environment also looks bad - the acquisition
    # indicators are then reported as CONTRIBUTORS rather than re-labelling
    # the verdict as C. Category C is reserved for recordings where a usable
    # pulse IS present and the environment merely degrades it.
    if truth_match is not None and detection_failed and not poor_signal:
        c.category = "B"
        c.label = "Peak-detection failure"
        c.confidence = "high" if reference_available else "medium"
        ev.append(
            "The pulse is present (ACF periodicity and/or SNR are adequate) but the "
            "detected beats disagree with the reference: the mismatch is in the "
            "detector, not in the physiology."
        )
    elif poor_signal:
        c.category = "A"
        c.label = "Genuinely poor signal quality"
        c.confidence = "high" if truth_match is not None else "medium"
        ev.append(
            "The optical signal itself does not carry a usable pulse "
            "(weak SNR / spectral concentration / ACF periodicity)."
        )
        if artifact:
            c.label = "Genuinely poor signal quality (acquisition-side contributors present)"
            ev.append(
                "Acquisition-side indicators are ALSO degraded (low-frequency / "
                "illumination dominance, exposure, saturation or a flat ROI), so the "
                "upstream cause is very likely the acquisition or the ROI crop, not "
                "the detector."
            )
    elif artifact:
        c.category = "C"
        c.label = "Preprocessing or ROI artifact"
        c.confidence = "medium"
        ev.append(
            "A pulse is detectable, but the acquisition environment (motion, exposure, "
            "saturation, flat ROI) degrades the measurement."
        )
    elif detection_failed:
        c.category = "B"
        c.label = "Peak-detection failure (signal marginal)"
        c.confidence = "low"
        ev.append("Detection disagrees with the reference, but the signal is marginal too.")
    elif truth_match is not None and not poor_signal and not artifact:
        c.category = "OK"
        c.label = "Signal usable, detection consistent with reference"
        c.confidence = "high" if reference_available else "medium"
        ev.append(
            "The pulse is recoverable and the detected beats agree with the reference: "
            "neither signal quality nor the detector is the limiting factor here."
        )
    else:
        c.category = "D"
        c.label = "Inconclusive - reference sensor required"
        c.confidence = "low"
        ev.append(
            "The offline evidence does not separate a weak signal from a detection "
            "problem. A synchronised reference (ECG/PPG) is needed to decide."
        )
        if truth_match is None:
            cav.append("No reference was available for this ROI.")

    cav.append(
        "Irregular detected intervals describe the detector's output, not a measured "
        "heart rhythm; no arrhythmia conclusion is drawn."
    )
    return c


# ── Report rendering ─────────────────────────────────────────────────────────

_CATEGORY_TITLES = {
    "OK": "OK. Signal usable, detection consistent with the reference",
    "A": "A. Genuinely poor signal quality",
    "B": "B. Peak-detection failure",
    "C": "C. Preprocessing or ROI artifact",
    "D": "D. Inconclusive - reference sensor required",
}


def render_report(
    analyses: Sequence[ROIAnalysis],
    classifications: Optional[Sequence[Classification]] = None,
    title: str = "Phase 9.0 - rPPG Signal Validation",
    extra_notes: Optional[Sequence[str]] = None,
) -> str:
    """Render a human-readable markdown report."""
    if classifications is None:
        classifications = [classify_roi(a) for a in analyses]

    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")

    for a, c in zip(analyses, classifications):
        lines.append(f"## ROI: `{a.roi_name}`" + (f" (source: {a.source})" if a.source else ""))
        lines.append("")
        lines.append(f"**Verdict: {c.category} - {c.label}** (confidence: {c.confidence})")
        lines.append("")
        lines.append("Evidence:")
        for e in c.evidence:
            lines.append(f"- {e}")
        lines.append("")
        if c.caveats:
            lines.append("Caveats:")
            for cv_ in c.caveats:
                lines.append(f"- {cv_}")
            lines.append("")

        d = a.as_dict()
        lines.append("| metric | value |")
        lines.append("| --- | --- |")
        for k in (
            "n_samples", "method", "bpm_fft", "snr_db", "spectral_concentration",
            "n_peaks_legacy", "n_peaks_posterior", "regularity_legacy_pct",
            "regularity_posterior_pct", "sqi_legacy", "sqi_posterior",
            "motion_score", "exposure_drift", "mean_brightness", "brightness_std",
            "saturation_fraction", "frame_diff_mean", "frame_diff_p95", "flat_fraction",
        ):
            lines.append(f"| {k} | {d[k]} |")
        lines.append("")
        for label, stats in (("legacy detector", a.ibi_legacy), ("posterior detector", a.ibi_posterior)):
            lines.append(f"- {label} IBI: {stats.as_dict()}")
        lines.append("")
        lines.append(f"- autocorrelation: {a.acf.as_dict()}")
        lines.append("")

    if extra_notes:
        lines.append("## Notes")
        lines.append("")
        for n in extra_notes:
            lines.append(f"- {n}")
        lines.append("")

    lines.append("## Category legend")
    lines.append("")
    for key in ("OK", "A", "B", "C", "D"):
        lines.append(f"- **{key}** - {_CATEGORY_TITLES[key]}")
    lines.append("")
    return "\n".join(lines)
