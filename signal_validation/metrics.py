"""
Signal-quality metrics used by the Phase 9.0 offline validation.

Everything here is pure maths on arrays — no production code is imported, so
the metrics can be unit-tested in isolation against synthetic ground truth.

Metrics implemented
-------------------
ibi_stats()        inter-beat interval distribution + coefficient of variation
acf_periodicity()  autocorrelation periodicity strength and dominant lag
match_peaks()      detected-vs-true peak matching (missed / false / interval error)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import numpy as np
from scipy.signal import correlate, find_peaks


# ── IBI statistics ────────────────────────────────────────────────────────────

@dataclass
class IBIStats:
    """Descriptive statistics of an inter-beat interval sequence (seconds)."""

    n_intervals: int = 0
    mean_ibi: float = float("nan")
    std_ibi: float = float("nan")
    median_ibi: float = float("nan")
    cv: float = float("nan")            # coefficient of variation (std/mean)
    rmssd: float = float("nan")         # ms, successive-difference RMS
    pnn50: float = float("nan")         # % successive diffs > 50 ms
    min_ibi: float = float("nan")
    max_ibi: float = float("nan")
    implied_bpm: float = float("nan")   # 60 / mean_ibi
    intervals: List[float] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "n_intervals": self.n_intervals,
            "mean_ibi_s": round(self.mean_ibi, 5),
            "std_ibi_s": round(self.std_ibi, 5),
            "median_ibi_s": round(self.median_ibi, 5),
            "cv": round(self.cv, 5),
            "rmssd_ms": round(self.rmssd, 2),
            "pnn50_pct": round(self.pnn50, 2),
            "min_ibi_s": round(self.min_ibi, 5),
            "max_ibi_s": round(self.max_ibi, 5),
            "implied_bpm": round(self.implied_bpm, 2),
        }


def ibi_stats(peak_times_s: Sequence[float]) -> IBIStats:
    """
    Compute IBI distribution statistics from peak timestamps (seconds).

    Coefficient of variation is std/mean of the inter-beat intervals, which is
    the definition used by the production legacy regularity metric in
    rppg_core.compute_sqi().
    """
    peaks = np.asarray(sorted(float(p) for p in peak_times_s), dtype=float)
    if len(peaks) < 2:
        return IBIStats(n_intervals=0)

    ibi = np.diff(peaks)
    ibi = ibi[np.isfinite(ibi) & (ibi > 0)]
    if ibi.size == 0:
        return IBIStats(n_intervals=0)

    mean_ibi = float(np.mean(ibi))
    std_ibi = float(np.std(ibi))
    cv = std_ibi / (mean_ibi + 1e-9) if mean_ibi > 0 else float("nan")

    if ibi.size >= 2:
        diff = np.diff(ibi) * 1000.0
        rmssd = float(np.sqrt(np.mean(diff ** 2)))
        pnn50 = float(np.mean(np.abs(diff) > 50.0) * 100.0)
    else:
        rmssd = float("nan")
        pnn50 = float("nan")

    return IBIStats(
        n_intervals=int(ibi.size),
        mean_ibi=mean_ibi,
        std_ibi=std_ibi,
        median_ibi=float(np.median(ibi)),
        cv=float(cv),
        rmssd=rmssd,
        pnn50=pnn50,
        min_ibi=float(np.min(ibi)),
        max_ibi=float(np.max(ibi)),
        implied_bpm=(60.0 / mean_ibi) if mean_ibi > 0 else float("nan"),
        intervals=[float(x) for x in ibi],
    )


# ── Autocorrelation periodicity ───────────────────────────────────────────────

@dataclass
class ACFResult:
    """Autocorrelation-based periodicity description of a signal."""

    acf_peak_value: float = 0.0     # max |acf| within the physiological lag band
    acf_peak_lag_s: float = float("nan")
    acf_peak_bpm: float = float("nan")
    acf_peak_is_local: bool = False  # True if a genuine local maximum was found
    acf_peak_hits: int = 0          # number of autocorrelation peaks in band
    acf_regularity: float = 0.0     # scaled 0..1, same shape as production ACF score
    acf_lag_min_s: float = float("nan")
    acf_lag_max_s: float = float("nan")

    def as_dict(self) -> dict:
        return {
            "acf_peak_value": round(self.acf_peak_value, 4),
            "acf_peak_lag_s": round(self.acf_peak_lag_s, 4),
            "acf_peak_bpm": round(self.acf_peak_bpm, 2),
            "acf_peak_is_local": self.acf_peak_is_local,
            "acf_peak_hits": self.acf_peak_hits,
            "acf_regularity": round(self.acf_regularity, 4),
        }


def acf_periodicity(
    signal: np.ndarray,
    fps: float,
    min_bpm: float = 40.0,
    max_bpm: float = 190.0,
) -> ACFResult:
    """
    Autocorrelation periodicity analysis over the physiological lag band.

    The scoring shape mirrors rppg_sqi.PosteriorSQI._regularity(): a genuine
    local autocorrelation maximum is used when present, otherwise the band
    maximum is halved, and the result is scaled as (peak - 0.15) / 0.5 clipped
    to [0, 1].
    """
    sig = np.asarray(signal, dtype=float)
    if sig.size < 30 or fps <= 0:
        return ACFResult()

    sig = sig - np.mean(sig)
    std = float(np.std(sig))
    if std < 1e-9:
        return ACFResult()
    sig = sig / std

    n = sig.size
    acf = correlate(sig, sig, mode="full")[n - 1:]
    acf = acf / (acf[0] + 1e-12)

    lag_min = max(int(fps * 60.0 / max_bpm), 1)
    lag_max = int(fps * 60.0 / min_bpm)
    if lag_max <= lag_min or len(acf) <= lag_min:
        return ACFResult()

    band = acf[lag_min:min(len(acf), lag_max)]
    if band.size == 0:
        return ACFResult()

    peak_idx, props = find_peaks(band, height=0.1)
    if peak_idx.size > 0:
        acf_peak = float(np.max(props["peak_heights"]))
        best_rel = int(peak_idx[np.argmax(props["peak_heights"])])
        is_local = True
    else:
        acf_peak = float(np.max(band)) * 0.5
        best_rel = int(np.argmax(band))
        is_local = False

    lag_s = (best_rel + lag_min) / fps
    bpm = 60.0 / lag_s if lag_s > 0 else float("nan")
    regularity = float(np.clip((acf_peak - 0.15) / 0.5, 0.0, 1.0))

    return ACFResult(
        acf_peak_value=acf_peak,
        acf_peak_lag_s=lag_s,
        acf_peak_bpm=bpm,
        acf_peak_is_local=is_local,
        acf_peak_hits=int(peak_idx.size),
        acf_regularity=regularity,
        acf_lag_min_s=lag_min / fps,
        acf_lag_max_s=lag_max / fps,
    )


# ── Peak matching against ground truth ───────────────────────────────────────

@dataclass
class PeakMatch:
    """Result of matching detected peaks against known-true peaks."""

    n_true: int = 0
    n_detected: int = 0
    n_matched: int = 0
    n_missed: int = 0
    n_false: int = 0
    missed_times_s: List[float] = field(default_factory=list)
    false_times_s: List[float] = field(default_factory=list)
    interval_errors_s: List[float] = field(default_factory=list)
    tolerance_s: float = 0.0

    @property
    def sensitivity(self) -> float:
        """Fraction of true peaks that were detected (recall)."""
        return self.n_matched / self.n_true if self.n_true else float("nan")

    @property
    def precision(self) -> float:
        """Fraction of detected peaks that are true (PPV)."""
        return self.n_matched / self.n_detected if self.n_detected else float("nan")

    @property
    def mean_abs_interval_error_s(self) -> float:
        return float(np.mean(np.abs(self.interval_errors_s))) if self.interval_errors_s else float("nan")

    @property
    def max_abs_interval_error_s(self) -> float:
        return float(np.max(np.abs(self.interval_errors_s))) if self.interval_errors_s else float("nan")

    def as_dict(self) -> dict:
        return {
            "n_true": self.n_true,
            "n_detected": self.n_detected,
            "n_matched": self.n_matched,
            "n_missed": self.n_missed,
            "n_false": self.n_false,
            "sensitivity": round(self.sensitivity, 4),
            "precision": round(self.precision, 4),
            "mean_abs_interval_error_s": round(self.mean_abs_interval_error_s, 5),
            "max_abs_interval_error_s": round(self.max_abs_interval_error_s, 5),
            "tolerance_s": self.tolerance_s,
        }


def match_peaks(
    detected_times_s: Sequence[float],
    true_times_s: Sequence[float],
    tolerance_s: float = 0.15,
) -> PeakMatch:
    """
    Greedy one-to-one matching of detected peaks to ground-truth peaks.

    A detected peak matches a true peak when they are within tolerance_s.
    Matches are assigned to the closest candidate first, so a single true
    peak cannot absorb two detections (no double counting).

    interval_errors_s holds (detected - true) for each matched pair.
    """
    det = np.asarray(sorted(float(x) for x in detected_times_s), dtype=float)
    tru = np.asarray(sorted(float(x) for x in true_times_s), dtype=float)

    result = PeakMatch(n_true=int(tru.size), n_detected=int(det.size), tolerance_s=tolerance_s)
    if det.size == 0 or tru.size == 0:
        result.n_missed = int(tru.size)
        result.n_false = int(det.size)
        result.missed_times_s = [float(x) for x in tru]
        result.false_times_s = [float(x) for x in det]
        return result

    # Build all candidate pairs, sort by distance, greedily assign.
    dist = np.abs(det[:, None] - tru[None, :])
    order = np.argsort(dist, axis=None)
    used_det: set = set()
    used_tru: set = set()
    pairs: List[Tuple[int, int]] = []
    for flat in order:
        i, j = np.unravel_index(flat, dist.shape)
        if dist[i, j] > tolerance_s:
            break
        if i in used_det or j in used_tru:
            continue
        used_det.add(int(i))
        used_tru.add(int(j))
        pairs.append((int(i), int(j)))

    for i, j in pairs:
        result.interval_errors_s.append(float(det[i] - tru[j]))
    result.n_matched = len(pairs)
    result.n_missed = int(tru.size - result.n_matched)
    result.n_false = int(det.size - result.n_matched)
    result.missed_times_s = [float(x) for k, x in enumerate(tru) if k not in used_tru]
    result.false_times_s = [float(x) for k, x in enumerate(det) if k not in used_det]
    return result


def match_peaks_with_latency(
    detected_times_s: Sequence[float],
    true_times_s: Sequence[float],
    tolerance_s: float = 0.10,
    max_latency_s: float = 0.60,
    step_s: float = 0.01,
) -> Tuple[PeakMatch, float]:
    """
    Match peaks allowing a constant pipeline latency.

    The production cardiac band-pass (rppg_core.bandpass_filter) uses
    scipy.signal.sosfilt, which is CAUSAL: it delays the waveform by the
    filter's group delay (0.07-0.23 s across the 45-150 BPM band). A
    comparison against a ground truth must therefore either compensate for
    that latency or use a tolerance wide enough to absorb it.

    The latency is estimated ROBUSTLY: every candidate (detected, true)
    pairing within a generous window contributes an offset, and the MEDIAN
    offset is taken. A plain argmax search is biased by whichever region of
    the recording is most corrupted, which is exactly the region the audit
    is trying to characterise.

    Returns (match, latency_s). The latency is applied to the TRUE times, so
    interval_errors_s remain comparable to the un-compensated case.
    """
    det = np.asarray(sorted(float(x) for x in detected_times_s), dtype=float)
    tru = np.asarray(sorted(float(x) for x in true_times_s), dtype=float)

    if det.size == 0 or tru.size == 0:
        return match_peaks(detected_times_s, true_times_s, tolerance_s), 0.0

    # Robust latency estimate: median offset over all candidate pairings
    # inside a generous window.
    offsets = []
    for t in tru:
        d = det - t
        near = d[np.abs(d) <= max_latency_s]
        if near.size:
            offsets.append(float(near[np.argmin(np.abs(near))]))
    if offsets:
        latency = float(np.median(offsets))
    else:
        latency = 0.0

    shifted = [t + latency for t in tru]
    return match_peaks(detected_times_s, shifted, tolerance_s), latency

