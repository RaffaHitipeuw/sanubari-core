"""
Controlled synthetic signals with KNOWN ground truth for Phase 9.0.

Each case returns the signal plus the ground-truth peak timestamps, so the
production peak detectors can be scored objectively:

    clean          — clean periodic pulse
    noisy          — periodic pulse plus white noise
    motion         — periodic pulse plus motion-like baseline wander + bursts
    missing_peaks  — periodic pulse with beats attenuated below detection
    extra_peaks    — periodic pulse with spurious extra pulses
    flat           — exactly constant signal
    white_noise    — pure white noise

Design notes (learned while building this suite — keep them in mind if you
add cases):

  * The production cardiac band-pass is CAUSAL (scipy.signal.sosfilt), so the
    filtered waveform lags the true pulse by the filter group delay: roughly
    0.23 s at 45 BPM falling to 0.07 s at 130 BPM. Any ground-truth
    comparison must compensate for that latency, otherwise every case looks
    like a total detection failure. See match_peaks_with_latency().

  * The legacy detector enforces a minimum peak distance of 0.50 s. A
    spurious pulse placed halfway between two beats can therefore only be
    detected when the beat period exceeds 1.0 s, i.e. below ~60 BPM. The
    extra_peaks case therefore defaults to 50 BPM; at 72 BPM the injection is
    geometrically impossible and would be a vacuous test.

  * Beats are attenuated with a smooth raised-cosine gain rather than being
    zeroed. Hard zeroing creates a step discontinuity, and the band-pass
    rings on that step, which produces spurious peaks that mask the effect
    being tested.

The synthetic generators deliberately cover the failure modes the audit is
trying to separate, and each carries a flag saying what the *correct*
verdict is, so the classifier can be regression-tested.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


# Per-case default BPM. Most cases use the caller-supplied rate; the two
# stress cases need a rate whose geometry makes the injection meaningful.
_DEFAULT_BPM: Dict[str, float] = {
    "extra_peaks": 50.0,
}


@dataclass
class SyntheticCase:
    """A synthetic signal plus its ground truth."""

    name: str
    signal: np.ndarray
    fps: float
    true_peak_times_s: List[float] = field(default_factory=list)
    true_bpm: float = float("nan")
    expected_category: str = ""   # A / B / C / D — what the audit should conclude
    description: str = ""
    notes: Dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "fps": self.fps,
            "n_samples": int(len(self.signal)),
            "duration_s": round(len(self.signal) / self.fps, 3),
            "n_true_peaks": len(self.true_peak_times_s),
            "true_bpm": round(self.true_bpm, 2),
            "expected_category": self.expected_category,
            "description": self.description,
            "notes": {k: round(float(v), 4) for k, v in self.notes.items()},
        }


def _pulse_train(
    n: int,
    fps: float,
    bpm: float,
    phase: float = 0.0,
) -> Tuple[np.ndarray, List[float]]:
    """
    Build a periodic pulse train (fundamental + 2nd harmonic).

    Returns the signal and the ground-truth peak timestamps, i.e. the times
    at which the waveform reaches its true maximum.
    """
    t = np.arange(n) / fps
    f = bpm / 60.0
    sig = np.sin(2 * np.pi * f * t + phase) + 0.30 * np.sin(2 * np.pi * 2 * f * t + 2 * phase)
    period = 60.0 / bpm

    # The waveform is a sum of a fundamental and its 2nd harmonic, so its
    # maximum does NOT sit at phase 0. Locate the true maximum of one period
    # on a dense grid and use it as the ground-truth peak offset.
    grid = np.linspace(0.0, period, 4096, endpoint=False)
    wave = (np.sin(2 * np.pi * grid / period + phase)
            + 0.30 * np.sin(4 * np.pi * grid / period + 2 * phase))
    peak_offset = float(grid[int(np.argmax(wave))])

    peaks = []
    k = 0
    while True:
        p = k * period + peak_offset
        if p >= n / fps:
            break
        peaks.append(p)
        k += 1
    return sig, peaks


def _apply_motion_burst(
    sig: np.ndarray,
    fps: float,
    center_s: float,
    length_s: float,
    rng: np.random.Generator,
    amplitude: float = 2.5,
    tremor_hz: float = 3.3,
    pulse_masking: float = 0.95,
    taper_s: float = 0.30,
) -> np.ndarray:
    """
    Superimpose a motion burst: broadband noise plus a tremor, under a
    smooth FLAT-TOP envelope so no step discontinuity is introduced.

    Motion does not merely add noise on top of the pulse: the illumination
    swing swamps the pulse itself. The pulse is therefore attenuated inside
    the burst by `pulse_masking` (fraction removed) while broadband noise
    and a tremor are added. Without the attenuation the pulse still shows
    through and the detector legitimately keeps finding it, which would make
    the case vacuous.

    The envelope has a flat core with cosine tapers of `taper_s` at both
    edges. A Hann envelope reaches its maximum at ONE sample, so only the
    single beat at the very centre of the burst is destroyed and the
    neighbouring beats are merely attenuated - which is why a Hann-shaped
    "missing peaks" burst still yields a sensitivity of ~0.97 and tests
    nothing. The flat top kills every beat inside the window.
    """
    n = len(sig)
    t = np.arange(n) / fps
    i0 = max(int((center_s - length_s / 2.0) * fps), 0)
    i1 = min(int((center_s + length_s / 2.0) * fps), n)
    env = np.zeros(n)
    if i1 > i0:
        taper = max(int(taper_s * fps), 1)
        core = i1 - i0
        if core > 2 * taper:
            env[i0:i0 + taper] = 0.5 * (1.0 - np.cos(np.pi * np.arange(taper) / taper))
            env[i0 + taper:i1 - taper] = 1.0
            env[i1 - taper:i1] = 0.5 * (1.0 + np.cos(np.pi * np.arange(taper) / taper))
        else:
            env[i0:i1] = np.hanning(core)
    out = sig * (1.0 - pulse_masking * env)
    out = out + env * amplitude * rng.standard_normal(n)
    out = out + 0.6 * env * np.sin(2 * np.pi * tremor_hz * t)
    return out


def build_case(
    name: str,
    duration_s: float = 30.0,
    fps: float = 30.0,
    bpm: Optional[float] = None,
    seed: int = 42,
) -> SyntheticCase:
    """
    Build one of the controlled synthetic cases by name.

    Raises KeyError for an unknown name.
    """
    n = int(round(duration_s * fps))
    rng = np.random.default_rng(seed)
    bpm = bpm if bpm is not None else _DEFAULT_BPM.get(name, 72.0)

    if name == "clean":
        sig, peaks = _pulse_train(n, fps, bpm)
        sig = sig + 0.002 * rng.standard_normal(n)
        return SyntheticCase(
            name=name, signal=sig, fps=fps, true_peak_times_s=peaks, true_bpm=bpm,
            expected_category="OK",
            description="Clean periodic pulse; both detectors should be near-perfect.",
        )

    if name == "noisy":
        # Noise must actually dominate the pulse for this to be a category-A
        # case: at noise_std 0.30 the pulse is still trivially recoverable
        # (SNR ~11 dB, sensitivity 1.0) and the case tests nothing.
        #
        # Phase 9.2 recalibration: 1.20 was calibrated against an estimator
        # that reported the DOUBLE of the true rate (the Phase 9.1 harmonic
        # doubling defect), so the SNR metric was measured in the 144 BPM band
        # instead of the 72 BPM band and looked poor (5.6 dB) even though the
        # pulse itself was still recoverable (ACF regularity 1.00, sensitivity
        # 0.92). With the doubling defect removed the case no longer tested
        # what it claims: at 1.20 the corrected estimator measures SNR 11.0 dB
        # and ACF regularity 1.00, so the audit correctly returns "OK".
        # At 4.00 the noise really does dominate - SNR 3.1 dB, ACF regularity
        # 0.32 and sensitivity 0.75 for the default seed (category A for every
        # seed checked) - so the case again tests the "low regularity, no usable
        # pulse" situation it was written for.
        sig, peaks = _pulse_train(n, fps, bpm)
        sig = sig + 4.00 * rng.standard_normal(n)
        return SyntheticCase(
            name=name, signal=sig, fps=fps, true_peak_times_s=peaks, true_bpm=bpm,
            expected_category="A",
            description="Periodic pulse buried in white noise; signal quality is poor.",
            notes={"noise_std": 4.00},
        )

    if name == "motion":
        sig, peaks = _pulse_train(n, fps, bpm)
        t = np.arange(n) / fps
        # Baseline wander (respiration / large motion) plus a motion burst.
        sig = sig + 0.8 * np.sin(2 * np.pi * 0.25 * t)
        burst_start = int(0.55 * n)
        burst_len = int(0.2 * n)
        # The burst amplitude is kept at a level where the cardiac band still
        # dominates (SNR ~20 dB, spectral concentration ~0.55): the point of
        # this case is that the PULSE SURVIVES while the environment is
        # degraded. With a stronger burst the cardiac band is swamped as well
        # and the case degenerates into a category-A case.
        ramp = np.ones(n)
        ramp[burst_start:burst_start + burst_len] = np.linspace(0, 4, burst_len)
        sig = sig + ramp * 0.25 * rng.standard_normal(n)
        return SyntheticCase(
            name=name, signal=sig, fps=fps, true_peak_times_s=peaks, true_bpm=bpm,
            expected_category="C",
            description="Motion-like baseline wander and a noise burst; preprocessing artifact.",
            notes={"wander_hz": 0.25, "burst_start_s": burst_start / fps},
        )

    if name == "missing_peaks":
        # A motion burst destroys a stretch of the signal. The beats inside
        # the burst are genuinely unrecoverable, so the detector must miss
        # them, and the ringing at the burst edges produces false beats.
        # Motion is the realistic mechanism; a hand-edited trace is not.
        #
        # The burst must swallow several whole beats: with only ~5 % of the
        # pulse left inside the burst the detector still recovers almost every
        # beat (sensitivity 0.97) and the case is vacuous. The pulse is
        # therefore fully masked over a 4-beat window.
        sig, peaks = _pulse_train(n, fps, bpm)
        period = 60.0 / bpm
        burst_center = 12 * period
        burst_len = 5.0 * period
        sig = _apply_motion_burst(
            sig, fps, burst_center, burst_len, rng,
            amplitude=1.2, pulse_masking=1.0,
        )
        return SyntheticCase(
            name=name, signal=sig, fps=fps, true_peak_times_s=peaks, true_bpm=bpm,
            expected_category="B",
            description="Motion burst wipes out several beats; the detector must miss "
                        "beats inside the burst and may report ringing at its edges.",
            notes={"burst_center_s": burst_center, "burst_len_s": burst_len},
        )

    if name == "extra_peaks":
        # A high-frequency oscillation (flickering light, muscle tremor)
        # superimposed on the pulse. The detector latches onto the
        # oscillation and reports beats that are not in the ground truth.
        sig, peaks = _pulse_train(n, fps, bpm)
        period = 60.0 / bpm
        osc_hz = 60.0 / (0.55 * period)   # ~1.8x the pulse rate
        t = np.arange(n) / fps
        onset = 8 * period
        onset_i = int(onset * fps)
        env = np.ones(n)
        ramp_len = max(int(0.5 * period * fps), 3)
        env[onset_i:onset_i + ramp_len] = np.linspace(0, 1, ramp_len)
        env[onset_i + ramp_len:] = 1.0
        sig = sig + 0.9 * env * np.sin(2 * np.pi * osc_hz * t)
        return SyntheticCase(
            name=name, signal=sig, fps=fps, true_peak_times_s=peaks, true_bpm=bpm,
            expected_category="B",
            description="Superimposed high-frequency oscillation; the detector reports "
                        "false beats that are not in the ground truth.",
            notes={"oscillation_hz": osc_hz, "onset_s": onset},
        )

    if name == "flat":
        # Genuinely constant: no noise at all. Any noise here would be
        # amplified to unit variance by the production z-normalisation step
        # and the case would silently degenerate into the white_noise case.
        sig = np.full(n, 0.25)
        return SyntheticCase(
            name=name, signal=sig, fps=fps, true_peak_times_s=[], true_bpm=float("nan"),
            expected_category="A",
            description="Exactly flat signal; no pulse and no noise is present.",
        )

    if name == "white_noise":
        sig = rng.standard_normal(n)
        return SyntheticCase(
            name=name, signal=sig, fps=fps, true_peak_times_s=[], true_bpm=float("nan"),
            expected_category="A",
            description="Pure white noise; no periodicity exists.",
        )

    raise KeyError(f"Unknown synthetic case: {name!r}. Known: {sorted(SYNTHETIC_CASES)}")


SYNTHETIC_CASES = (
    "clean",
    "noisy",
    "motion",
    "missing_peaks",
    "extra_peaks",
    "flat",
    "white_noise",
)


def build_all_cases(**kwargs) -> List[SyntheticCase]:
    """Build every controlled synthetic case."""
    return [build_case(name, **kwargs) for name in SYNTHETIC_CASES]
