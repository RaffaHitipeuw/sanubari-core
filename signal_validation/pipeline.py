"""
Offline per-ROI signal extraction and analysis for Phase 9.0.

This module reproduces the *production* signal path in a way that the live
engine never exposes, so a recording can be inspected after the fact:

    raw ROI RGB  ->  MethodArbitrator (chrom/POS/green blend)
                 ->  linear detrend
                 ->  exposure trend removal
                 ->  respiratory notch suppression
                 ->  cardiac bandpass
                 ->  z-normalisation
                 ->  peak detection (two detectors, both production ones)

Two production peak detectors exist and they are NOT identical. Both are
evaluated here:

    "legacy"    find_peaks(sig_norm, distance=int(fps*0.50),
                           prominence=cfg.PEAK_PROMINENCE_MIN, height=0.1)
                — rppg_core.compute_sqi(), feeds breakdown["regularity"]

    "posterior" find_peaks(sig_z, distance=max(int(fps*0.45), 5),
                           prominence=0.35)
                — rppg_sqi.PosteriorSQI.compute(), feeds regularity_score

The BPM estimate itself comes from an FFT (estimate_bpm_fft), NOT from peak
detection, so a peak-detector failure degrades regularity/SQI but does not by
itself corrupt the BPM number.

Nothing here mutates production state. Production modules are imported and
called read-only.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.signal import detrend as scipy_detrend, find_peaks, welch

from rppg_core import (
    MethodArbitrator,
    ExposureCompensator,
    RespiratoryArtifactSuppressor,
    bandpass_filter,
    compute_sqi,
    estimate_bpm_fft,
    cfg,
)
from rppg_sqi import PosteriorSQI

from .metrics import ACFResult, IBIStats, acf_periodicity, ibi_stats


# ── Detection helpers (production-identical) ─────────────────────────────────

def detect_peaks_legacy(signal: np.ndarray, fps: float) -> np.ndarray:
    """
    Peak detection exactly as rppg_core.compute_sqi() performs it.

    compute_sqi() detrends the signal linearly, z-normalises it and then calls
    find_peaks with a 0.50 s minimum distance, cfg.PEAK_PROMINENCE_MIN
    prominence and a 0.1 height floor.
    """
    sig = np.asarray(signal, dtype=float)
    if sig.size < 3:
        return np.array([], dtype=int)
    sig = sig - np.mean(sig)
    sig = scipy_detrend(sig, type="linear")
    std = float(np.std(sig))
    if std < 1e-9:
        return np.array([], dtype=int)
    sig_norm = (sig - np.mean(sig)) / std
    peaks, _ = find_peaks(
        sig_norm,
        distance=int(fps * 0.50),
        prominence=cfg.PEAK_PROMINENCE_MIN,
        height=0.1,
    )
    return peaks


def detect_peaks_posterior(signal: np.ndarray, fps: float) -> np.ndarray:
    """
    Peak detection exactly as rppg_sqi.PosteriorSQI.compute() performs it.

    PosteriorSQI z-normalises the (already bandpassed) signal and calls
    find_peaks with a 0.45 s minimum distance and a fixed 0.35 prominence.
    """
    sig = np.asarray(signal, dtype=float)
    if sig.size < 3:
        return np.array([], dtype=int)
    std = float(np.std(sig))
    if std < 1e-9:
        return np.array([], dtype=int)
    sig_z = (sig - np.mean(sig)) / std
    min_dist = max(int(fps * 0.45), 5)
    peaks, _ = find_peaks(sig_z, distance=min_dist, prominence=0.35)
    return peaks


# ── Preprocessing ─────────────────────────────────────────────────────────────

def preprocess_like_production(
    r: np.ndarray,
    g: np.ndarray,
    b: np.ndarray,
    fps: float,
    roi_name: str = "roi",
) -> Dict[str, np.ndarray]:
    """
    Reproduce the V2 (MultiROIFusionEngineV2) per-ROI preprocessing chain.

    Chain (rppg_core.py, MultiROIFusionEngineV2.update):
        1. MethodArbitrator.select_best(r, g, b, fps)  -> blended chrom signal
        2. scipy detrend (linear)
        3. ExposureCompensator.normalize_roi_signal (linear trend removal)
        4. RespiratoryArtifactSuppressor.suppress (notch filters)
        5. bandpass_filter (0.833 - 3.0 Hz, order 4, sosfilt)
        6. z-normalisation

    Returns a dict with the raw per-channel series and the 'signal' entry
    holding the final filtered series that production feeds to the SQI and
    BPM estimators.
    """
    r = np.asarray(r, dtype=float)
    g = np.asarray(g, dtype=float)
    b = np.asarray(b, dtype=float)
    n = min(len(r), len(g), len(b))
    r, g, b = r[:n], g[:n], b[:n]

    arbitrator = MethodArbitrator()
    blended, winner, method_sqi = arbitrator.select_best(r, g, b, fps)

    sd = scipy_detrend(blended, type="linear")

    exposure = ExposureCompensator()
    sd = exposure.normalize_roi_signal(sd)

    resp = RespiratoryArtifactSuppressor()
    resp.update_resp_freq(g, fps)
    sd = resp.suppress(sd, fps)

    sf = bandpass_filter(sd, fps)
    std = float(np.std(sf))
    if std > 1e-8:
        sf = (sf - np.mean(sf)) / std

    return {
        "raw_r": r,
        "raw_g": g,
        "raw_b": b,
        "blended": np.asarray(blended, dtype=float),
        "signal": np.asarray(sf, dtype=float),
        "method": winner,
        "method_sqi": method_sqi,
    }


# ── Analysis result container ─────────────────────────────────────────────────

@dataclass
class ROIAnalysis:
    """Everything the offline audit knows about one ROI."""

    roi_name: str = ""
    source: str = ""
    fps: float = 30.0
    n_samples: int = 0

    raw_r: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)
    raw_g: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)
    raw_b: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)
    filtered: np.ndarray = field(default_factory=lambda: np.array([]), repr=False)

    method: str = ""
    method_sqi: Dict[str, float] = field(default_factory=dict)

    # Spectral
    snr_db: float = float("nan")
    spectral_concentration: float = float("nan")
    bpm_fft: float = float("nan")

    # Peak detection
    peaks_legacy_s: List[float] = field(default_factory=list)
    peaks_posterior_s: List[float] = field(default_factory=list)
    ibi_legacy: IBIStats = field(default_factory=IBIStats)
    ibi_posterior: IBIStats = field(default_factory=IBIStats)

    # Autocorrelation
    acf: ACFResult = field(default_factory=ACFResult)

    # Production regularity (0-100 scale)
    regularity_legacy: float = float("nan")   # compute_sqi breakdown["regularity"]
    regularity_posterior: float = float("nan")  # PosteriorSQI regularity_score

    # Production SQI
    sqi_legacy: float = float("nan")
    sqi_posterior: float = float("nan")

    # Environment / artifact indicators
    motion_score: float = float("nan")
    exposure_drift: float = float("nan")
    mean_brightness: float = float("nan")
    brightness_std: float = float("nan")
    saturation_fraction: float = float("nan")
    frame_diff_mean: float = float("nan")
    frame_diff_p95: float = float("nan")
    flat_fraction: float = float("nan")
    lf_ratio: float = float("nan")   # low-frequency vs cardiac power in raw green

    def as_dict(self) -> dict:
        return {
            "roi_name": self.roi_name,
            "source": self.source,
            "fps": self.fps,
            "n_samples": self.n_samples,
            "method": self.method,
            "bpm_fft": round(self.bpm_fft, 2),
            "snr_db": round(self.snr_db, 2),
            "spectral_concentration": round(self.spectral_concentration, 4),
            "n_peaks_legacy": len(self.peaks_legacy_s),
            "n_peaks_posterior": len(self.peaks_posterior_s),
            "ibi_legacy": self.ibi_legacy.as_dict(),
            "ibi_posterior": self.ibi_posterior.as_dict(),
            "acf": self.acf.as_dict(),
            "regularity_legacy_pct": round(self.regularity_legacy, 2),
            "regularity_posterior_pct": round(self.regularity_posterior, 2),
            "sqi_legacy": round(self.sqi_legacy, 1),
            "sqi_posterior": round(self.sqi_posterior, 1),
            "motion_score": round(self.motion_score, 3),
            "exposure_drift": round(self.exposure_drift, 3),
            "mean_brightness": round(self.mean_brightness, 2),
            "brightness_std": round(self.brightness_std, 2),
            "saturation_fraction": round(self.saturation_fraction, 4),
            "frame_diff_mean": round(self.frame_diff_mean, 4),
            "frame_diff_p95": round(self.frame_diff_p95, 4),
            "flat_fraction": round(self.flat_fraction, 4),
            "lf_ratio": round(self.lf_ratio, 4),
        }


def _saturation_and_flat(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> Tuple[float, float]:
    """Fraction of frames that are saturated or (near-)flat in colour."""
    if len(r) == 0:
        return float("nan"), float("nan")
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    saturation = float(np.mean((mx >= 250.0) | (mn <= 5.0)))
    flat = float(np.mean((mx - mn) < 3.0))
    return saturation, flat


def analyze_roi_series(
    r: Sequence[float],
    g: Sequence[float],
    b: Sequence[float],
    fps: float = 30.0,
    roi_name: str = "roi",
    source: str = "",
    motion_score: float = float("nan"),
    exposure_drift: float = float("nan"),
) -> ROIAnalysis:
    """
    Full offline analysis of one ROI's channel series.

    The peak timestamps reported here are the ones production would produce
    from the same signal, so they can be compared against a ground truth.
    """
    pre = preprocess_like_production(r, g, b, fps, roi_name)
    sf = pre["signal"]
    n = len(sf)

    res = ROIAnalysis(
        roi_name=roi_name,
        source=source,
        fps=fps,
        n_samples=n,
        raw_r=pre["raw_r"],
        raw_g=pre["raw_g"],
        raw_b=pre["raw_b"],
        filtered=sf,
        method=pre["method"],
        method_sqi=pre["method_sqi"],
        motion_score=motion_score,
        exposure_drift=exposure_drift,
    )

    if n < 30:
        return res

    raw_r, raw_g, raw_b = pre["raw_r"], pre["raw_g"], pre["raw_b"]
    res.mean_brightness = float(np.mean(raw_g))
    res.brightness_std = float(np.std(raw_g))
    res.saturation_fraction, res.flat_fraction = _saturation_and_flat(raw_r, raw_g, raw_b)

    # Frame-to-frame change of the raw green channel: a motion proxy that does
    # not need a face detector.
    if n >= 2:
        d = np.abs(np.diff(raw_g))
        res.frame_diff_mean = float(np.mean(d))
        res.frame_diff_p95 = float(np.percentile(d, 95))

    # Scale-free motion / illumination indicator: the share of the raw green
    # channel's power that sits BELOW the cardiac band (0.05-0.6 Hz) relative
    # to the power inside it (0.7-3.4 Hz). Frame-to-frame difference alone
    # cannot separate motion from sensor noise (both inflate it) and is not
    # comparable between a unit-amplitude synthetic trace and a 0-255 video;
    # this ratio is dimensionless and behaves for both.
    g_detr = scipy_detrend(np.asarray(raw_g, dtype=float), type="linear")
    nperseg = min(n, max(64, int(fps * 8)))
    f_g, psd_g = welch(g_detr, fs=fps, nperseg=nperseg, window="hann")
    lf_band = (f_g >= 0.05) & (f_g <= 0.60)
    card_band = (f_g >= 0.70) & (f_g <= 3.40)
    p_lf = float(np.sum(psd_g[lf_band])) if np.any(lf_band) else 0.0
    p_card = float(np.sum(psd_g[card_band])) if np.any(card_band) else 0.0
    res.lf_ratio = float(p_lf / p_card) if p_card > 1e-12 else float("nan")

    # Spectral metrics, mirroring PosteriorSQI's welch-based SNR.
    freqs, psd = welch(sf, fs=fps, nperseg=min(n, max(64, int(fps * 4))), window="hann")
    band = (freqs >= 0.7) & (freqs <= 3.33)
    band_power = float(np.sum(psd[band])) + 1e-12
    if res.bpm_fft == 0.0 or np.isnan(res.bpm_fft):
        bpm_fft, _, _, _ = estimate_bpm_fft(sf, fps, roi_name=roi_name)
        res.bpm_fft = float(bpm_fft)
    peak_hz = res.bpm_fft / 60.0 if res.bpm_fft > 0 else 1.2
    sig_mask = (freqs >= peak_hz - 0.10) & (freqs <= peak_hz + 0.10)
    noise_mask = band & (~sig_mask)
    p_signal = float(np.sum(psd[sig_mask])) if np.any(sig_mask) else 0.0
    p_noise = float(np.median(psd[noise_mask])) if np.any(noise_mask) else 1e-9
    n_sig = max(int(np.sum(sig_mask)), 1)
    snr_raw = p_signal / (p_noise * n_sig + 1e-12)
    res.snr_db = float(10.0 * np.log10(max(snr_raw, 1e-9)))
    res.spectral_concentration = float(p_signal / band_power)

    # Peak detection, both production detectors.
    peaks_legacy = detect_peaks_legacy(sf, fps)
    peaks_posterior = detect_peaks_posterior(sf, fps)
    res.peaks_legacy_s = [float(p / fps) for p in peaks_legacy]
    res.peaks_posterior_s = [float(p / fps) for p in peaks_posterior]
    res.ibi_legacy = ibi_stats(res.peaks_legacy_s)
    res.ibi_posterior = ibi_stats(res.peaks_posterior_s)

    res.acf = acf_periodicity(sf, fps)

    # Production regularity / SQI numbers for the same signal.
    sqi_legacy, breakdown = compute_sqi(
        sf, fps, res.bpm_fft,
        motion_score=0.0 if np.isnan(motion_score) else motion_score,
        mean_brightness=res.mean_brightness,
        roi_brightness=res.mean_brightness,
        roi_name=roi_name,
    )
    res.sqi_legacy = float(sqi_legacy)
    res.regularity_legacy = float(breakdown.get("regularity", float("nan")))

    posterior = PosteriorSQI(roi_name)
    sqi_post = posterior.compute(sf, fps, res.bpm_fft)
    res.sqi_posterior = float(sqi_post.sqi)
    res.regularity_posterior = float(sqi_post.regularity_score) * 100.0

    return res


# ── Video ingestion ───────────────────────────────────────────────────────────

def _read_video_channels(path: str, max_frames: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """
    Read a video and return per-frame mean R, G, B plus the frame rate.

    NOTE: this treats the *whole frame* as the ROI. That is the correct
    behaviour for the rPPG-10 dataset, whose videos are already cropped to a
    single face region (64x64). For full-frame recordings the caller should
    crop to an ROI first, or use analyze_session_csv() on a recorded session.
    """
    import cv2

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    if fps <= 0 or not np.isfinite(fps):
        cap.release()
        raise ValueError(f"Invalid FPS for video: {path}")

    rs: List[float] = []
    gs: List[float] = []
    bs: List[float] = []
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if max_frames is not None and idx >= max_frames:
            break
        b_mean = float(cv2.mean(frame[:, :, 0])[0])
        g_mean = float(cv2.mean(frame[:, :, 1])[0])
        r_mean = float(cv2.mean(frame[:, :, 2])[0])
        bs.append(b_mean)
        gs.append(g_mean)
        rs.append(r_mean)
        idx += 1
    cap.release()

    return np.array(rs), np.array(gs), np.array(bs), fps


def analyze_video_rois(
    video_path: str,
    roi_name: str = "roi",
    fps: Optional[float] = None,
    max_frames: Optional[int] = None,
) -> ROIAnalysis:
    """Analyse every frame of a video as if it were a single ROI."""
    r, g, b, vid_fps = _read_video_channels(video_path, max_frames=max_frames)
    use_fps = fps if fps else vid_fps
    return analyze_roi_series(
        r, g, b, fps=use_fps,
        roi_name=roi_name,
        source=os.path.basename(video_path),
    )


# ── Signal export ─────────────────────────────────────────────────────────────

def export_roi_signals(
    analysis: ROIAnalysis,
    out_dir: str,
    tag: Optional[str] = None,
) -> Dict[str, str]:
    """
    Write the raw channels, the filtered signal and the detected peak
    timestamps of one ROI to CSV files.

    Three files per ROI:
      <tag>_signal.csv   frame_index, t_s, raw_r, raw_g, raw_b, filtered,
                         is_peak_legacy, is_peak_posterior
      <tag>_peaks.csv    detector, peak_time_s
      <tag>_meta.json    the metrics of the ROI

    This is the offline export of what the live engine computes but never
    exposes, so a recording can be inspected after the fact.
    """
    import json

    os.makedirs(out_dir, exist_ok=True)
    tag = tag or (analysis.roi_name or "roi").replace(":", "_").replace(" ", "_")
    sig_path = os.path.join(out_dir, f"{tag}_signal.csv")
    peaks_path = os.path.join(out_dir, f"{tag}_peaks.csv")
    meta_path = os.path.join(out_dir, f"{tag}_meta.json")

    n = len(analysis.filtered)
    legacy = set(int(round(t * analysis.fps)) for t in analysis.peaks_legacy_s)
    posterior = set(int(round(t * analysis.fps)) for t in analysis.peaks_posterior_s)

    with open(sig_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["frame_index", "t_s", "raw_r", "raw_g", "raw_b",
                    "filtered", "is_peak_legacy", "is_peak_posterior"])
        for i in range(n):
            w.writerow([
                i,
                round(i / analysis.fps, 6),
                round(float(analysis.raw_r[i]), 6) if i < len(analysis.raw_r) else "",
                round(float(analysis.raw_g[i]), 6) if i < len(analysis.raw_g) else "",
                round(float(analysis.raw_b[i]), 6) if i < len(analysis.raw_b) else "",
                round(float(analysis.filtered[i]), 8),
                int(i in legacy),
                int(i in posterior),
            ])

    with open(peaks_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["detector", "peak_time_s"])
        for t in analysis.peaks_legacy_s:
            w.writerow(["legacy", round(float(t), 6)])
        for t in analysis.peaks_posterior_s:
            w.writerow(["posterior", round(float(t), 6)])

    meta = analysis.as_dict()
    meta["ibi_legacy"] = analysis.ibi_legacy.as_dict()
    meta["ibi_posterior"] = analysis.ibi_posterior.as_dict()
    meta["acf"] = analysis.acf.as_dict()
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return {"signal": sig_path, "peaks": peaks_path, "meta": meta_path}


# ── Recorded-session ingestion ────────────────────────────────────────────────

def analyze_session_csv(
    csv_path: str,
    roi_name: str = "roi",
    fps: float = 30.0,
) -> Dict[str, ROIAnalysis]:
    """
    Analyse a ReproducibilityLogger raw_signals.csv export.

    The logger (rppg_core.ReproducibilityLogger) writes one row per frame per
    ROI with columns timestamp, roi_name, r, g, b, bpm, sqi. This is the
    natural offline artefact for a live recording.
    """
    rows: Dict[str, List[Tuple[float, float, float, float]]] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = (row.get("roi_name") or "").strip()
            if not name:
                continue
            try:
                ts = float(row["timestamp"])
                rr = float(row["r"])
                gg = float(row["g"])
                bb = float(row["b"])
            except (KeyError, TypeError, ValueError):
                continue
            rows.setdefault(name, []).append((ts, rr, gg, bb))

    out: Dict[str, ROIAnalysis] = {}
    for name, entries in rows.items():
        entries.sort(key=lambda e: e[0])
        r = np.array([e[1] for e in entries])
        g = np.array([e[2] for e in entries])
        b = np.array([e[3] for e in entries])
        # Derive the effective sample rate from the timestamps themselves.
        eff_fps = fps
        if len(entries) >= 3:
            span = entries[-1][0] - entries[0][0]
            if span > 0:
                eff_fps = (len(entries) - 1) / span
        out[name] = analyze_roi_series(
            r, g, b, fps=eff_fps,
            roi_name=name,
            source=os.path.basename(csv_path),
        )
    return out
