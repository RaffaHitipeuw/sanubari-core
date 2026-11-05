"""
Reference-sensor comparison for Phase 9.0.

The rPPG-10 dataset in this repository ships synchronised ECG
(Subject_X_ECG.npy at 1000 Hz) next to 30 fps ROI videos of the same
recording, so a genuine reference exists and no reference data has to be
invented.

Two important caveats, both enforced by this module:

  1. The ECG-video start offset is NOT verified in the dataset. The adapter
     (p11_validation.rppg10_adapter) exposes ecg_offset_known, defaulting to
     False. Everything produced here is therefore reported as
     "ECG-native / offset-unverified" unless an offset is explicitly
     supplied AND the caller asserts it is known.

  2. Beat-level comparison needs an offset. The module can SEARCH for the
     offset that maximises beat agreement, but a searched offset is a
     hypothesis, not ground truth, and is reported as such.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import numpy as np

from .metrics import PeakMatch, match_peaks


@dataclass
class ECGCondition:
    """A loaded ECG reference plus its derived beat timestamps."""

    path: str
    ecg_fs: float = 1000.0
    r_peak_times_s: List[float] = field(default_factory=list)
    hr_times_s: List[float] = field(default_factory=list)
    hr_bpm: List[float] = field(default_factory=list)
    offset_sec: float = 0.0
    offset_known: bool = False
    issues: List[str] = field(default_factory=list)

    @property
    def mean_hr_bpm(self) -> float:
        finite = [h for h in self.hr_bpm if np.isfinite(h)]
        return float(np.mean(finite)) if finite else float("nan")

    @property
    def sdnn_ms(self) -> float:
        """SDNN of the ECG inter-beat intervals, in ms."""
        if len(self.r_peak_times_s) < 3:
            return float("nan")
        ibi = np.diff(np.asarray(self.r_peak_times_s)) * 1000.0
        return float(np.std(ibi))

    @property
    def ibi_cv(self) -> float:
        """
        Coefficient of variation of the ECG inter-beat intervals.

        This is the physiological counterpart of the detector's IBI CV: if the
        detector reports a much larger CV than the ECG does, the irregularity
        is a property of the DETECTOR, not of the recorded heart rhythm.
        """
        if len(self.r_peak_times_s) < 3:
            return float("nan")
        ibi = np.diff(np.asarray(self.r_peak_times_s))
        mean = float(np.mean(ibi))
        return float(np.std(ibi) / mean) if mean > 0 else float("nan")

    def as_dict(self) -> dict:
        return {
            "path": os.path.basename(self.path),
            "ecg_fs": self.ecg_fs,
            "n_r_peaks": len(self.r_peak_times_s),
            "mean_hr_bpm": round(self.mean_hr_bpm, 2),
            "sdnn_ms": round(self.sdnn_ms, 2),
            "offset_sec": self.offset_sec,
            "offset_known": self.offset_known,
            "issues": list(self.issues),
        }


def load_ecg_reference(
    ecg_path: str,
    ecg_fs: float = 1000.0,
    offset_sec: float = 0.0,
    offset_known: bool = False,
    hr_window_sec: float = 10.0,
    hr_step_sec: float = 1.0,
) -> ECGCondition:
    """
    Load an ECG .npy file and derive R-peak timestamps and a windowed HR trace.

    Reuses p11_validation.rppg10_adapter so the R-peak detection is the same
    one already validated for this dataset.
    """
    from p11_validation.rppg10_adapter import detect_r_peaks, ecg_to_hr, load_ecg

    cond = ECGCondition(
        path=ecg_path,
        ecg_fs=ecg_fs,
        offset_sec=offset_sec,
        offset_known=offset_known,
    )
    if not os.path.exists(ecg_path):
        cond.issues.append(f"ECG file not found: {ecg_path}")
        return cond

    ecg = load_ecg(ecg_path)
    cond.issues.append(
        "ECG-video start offset is UNVERIFIED; beat-level results are hypotheses only."
        if not offset_known else "ECG-video offset supplied by the caller and marked known."
    )

    peaks = detect_r_peaks(ecg, ecg_fs)
    cond.r_peak_times_s = [float(p / ecg_fs) for p in peaks]

    t_hr, hr, _counts = ecg_to_hr(ecg, ecg_fs, window_sec=hr_window_sec, step_sec=hr_step_sec)
    cond.hr_times_s = [float(t + offset_sec) for t in t_hr]
    cond.hr_bpm = [float(h) for h in hr]
    return cond


# ── Beat comparison ───────────────────────────────────────────────────────────

def compare_beats(
    detected_times_s: Sequence[float],
    ecg: ECGCondition,
    tolerance_s: float = 0.15,
    search_offset: bool = False,
    search_range_s: float = 5.0,
    search_step_s: float = 0.05,
) -> Tuple[PeakMatch, float]:
    """
    Compare detected pulse peaks against ECG R-peaks.

    Returns (match, offset_used_s). The offset is 0 when no search was done.
    When search_offset is True the offset is chosen to maximise beat
    agreement — the result is a hypothesis, and the caller is expected to
    treat it as such (see module docstring).
    """
    true_times = [t + ecg.offset_sec for t in ecg.r_peak_times_s]

    if not search_offset:
        return match_peaks(detected_times_s, true_times, tolerance_s), ecg.offset_sec

    best_offset = 0.0
    best_match = match_peaks(detected_times_s, true_times, tolerance_s)
    n_off = int(search_range_s / search_step_s)
    for k in range(-n_off, n_off + 1):
        off = k * search_step_s
        shifted = [t + off for t in true_times]
        m = match_peaks(detected_times_s, shifted, tolerance_s)
        if (m.n_matched, -m.n_false) > (best_match.n_matched, -best_match.n_false):
            best_match = m
            best_offset = off
    return best_match, best_offset


def compare_hr_traces(
    video_times_s: Sequence[float],
    video_bpm: Sequence[float],
    ecg: ECGCondition,
    tolerance_s: float = 3.0,
) -> dict:
    """
    Compare a video-derived HR trace against the ECG HR trace.

    Matching is by nearest timestamp within tolerance_s. Only finite values
    on both sides are used.
    """
    vt = np.asarray(list(video_times_s), dtype=float)
    vb = np.asarray(list(video_bpm), dtype=float)
    et = np.asarray(ecg.hr_times_s, dtype=float)
    eb = np.asarray(ecg.hr_bpm, dtype=float)

    if vt.size == 0 or et.size == 0:
        return {"n_pairs": 0, "mae_bpm": float("nan"), "rmse_bpm": float("nan"),
                "bias_bpm": float("nan"), "pearson_r": float("nan"),
                "note": "no overlapping HR samples"}

    pairs: List[Tuple[float, float]] = []
    for t, v in zip(vt, vb):
        if not np.isfinite(v):
            continue
        d = np.abs(et - t)
        j = int(np.argmin(d))
        if d[j] <= tolerance_s and np.isfinite(eb[j]):
            pairs.append((float(v), float(eb[j])))
    if not pairs:
        return {"n_pairs": 0, "mae_bpm": float("nan"), "rmse_bpm": float("nan"),
                "bias_bpm": float("nan"), "pearson_r": float("nan"),
                "note": "no overlapping HR samples"}

    arr = np.asarray(pairs)
    diff = arr[:, 0] - arr[:, 1]
    r = float("nan")
    if arr.shape[0] >= 3 and np.std(arr[:, 0]) > 0 and np.std(arr[:, 1]) > 0:
        r = float(np.corrcoef(arr[:, 0], arr[:, 1])[0, 1])
    return {
        "n_pairs": int(arr.shape[0]),
        "mae_bpm": float(np.mean(np.abs(diff))),
        "rmse_bpm": float(np.sqrt(np.mean(diff ** 2))),
        "bias_bpm": float(np.mean(diff)),
        "pearson_r": r,
        "mean_video_bpm": float(np.mean(arr[:, 0])),
        "mean_ecg_bpm": float(np.mean(arr[:, 1])),
        "note": "offset-unverified alignment" if not ecg.offset_known else "known offset",
    }
