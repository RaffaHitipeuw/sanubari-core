# Phase 9.0 — Signal validation: raw_signals_demo.csv

## ROI: `forehead` (source: raw_signals_demo.csv)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: medium)

Evidence:
- SNR=0.20 dB, spectral concentration=0.078, ACF regularity=0.193 (peak 0.246 @ 64.3 BPM)
- legacy detector: 73 peaks, IBI CV=0.282, implied BPM=72.8; FFT BPM=120.4
- posterior detector: 80 peaks, IBI CV=0.274; regularity legacy=66.1% posterior=17.4%
- motion proxy: frame-diff mean=0.1813 p95=0.7214; low-frequency/cardiac power ratio=3.984; exposure drift=n/a; brightness mean=103.9 std=1.2; saturated=0.000; flat=0.000
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- No ground truth / reference sensor for this ROI: the detector cannot be scored, so peak-level failure cannot be separated from a weak signal.
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 1800 |
| method | green |
| bpm_fft | 120.4 |
| snr_db | 0.2 |
| spectral_concentration | 0.0778 |
| n_peaks_legacy | 73 |
| n_peaks_posterior | 80 |
| regularity_legacy_pct | 66.1 |
| regularity_posterior_pct | 17.4 |
| sqi_legacy | 46.4 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 103.89 |
| brightness_std | 1.23 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1813 |
| frame_diff_p95 | 0.7214 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 72, 'mean_ibi_s': 0.82407, 'std_ibi_s': 0.23275, 'median_ibi_s': 0.8, 'cv': 0.28244, 'rmssd_ms': 316.25, 'pnn50_pct': 81.69, 'min_ibi_s': 0.46667, 'max_ibi_s': 1.4, 'implied_bpm': 72.81}
- posterior detector IBI: {'n_intervals': 79, 'mean_ibi_s': 0.75105, 'std_ibi_s': 0.20595, 'median_ibi_s': 0.76667, 'cv': 0.27421, 'rmssd_ms': 288.06, 'pnn50_pct': 82.05, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.23333, 'implied_bpm': 79.89}

- autocorrelation: {'acf_peak_value': 0.2464, 'acf_peak_lag_s': 0.9333, 'acf_peak_bpm': 64.29, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1928}

## Notes

- Source: raw_signals_demo.csv (ReproducibilityLogger raw_signals.csv export).
- No ground truth / reference sensor was supplied for this session, so every verdict is D (inconclusive) unless the signal itself is clearly unusable.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
