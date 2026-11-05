# Phase 9.0 — Signal validation: Subject_1_Forehead_.avi

## ROI: `forehead` (source: Subject_1_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.07 dB, spectral concentration=0.074, ACF regularity=0.229 (peak 0.265 @ 60.0 BPM)
- legacy detector: 676 peaks, IBI CV=0.267, implied BPM=67.6; FFT BPM=120.0
- posterior detector: 774 peaks, IBI CV=0.311; regularity legacy=68.0% posterior=14.8%
- motion proxy: frame-diff mean=0.1745 p95=0.6875; low-frequency/cardiac power ratio=1.529; exposure drift=n/a; brightness mean=103.8 std=2.1; saturated=0.000; flat=0.000
- ground truth: 574 true beats, 676 detected, matched=341, missed=233, false=335, sensitivity=0.594, precision=0.504, mean |interval error|=0.0720 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.07 |
| spectral_concentration | 0.0743 |
| n_peaks_legacy | 676 |
| n_peaks_posterior | 774 |
| regularity_legacy_pct | 68.0 |
| regularity_posterior_pct | 14.8 |
| sqi_legacy | 42.4 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 103.75 |
| brightness_std | 2.12 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1745 |
| frame_diff_p95 | 0.6875 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 675, 'mean_ibi_s': 0.88696, 'std_ibi_s': 0.23682, 'median_ibi_s': 0.86667, 'cv': 0.267, 'rmssd_ms': 312.57, 'pnn50_pct': 84.87, 'min_ibi_s': 0.5, 'max_ibi_s': 1.8, 'implied_bpm': 67.65}
- posterior detector IBI: {'n_intervals': 773, 'mean_ibi_s': 0.77572, 'std_ibi_s': 0.24117, 'median_ibi_s': 0.76667, 'cv': 0.31089, 'rmssd_ms': 317.56, 'pnn50_pct': 83.55, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.66667, 'implied_bpm': 77.35}

- autocorrelation: {'acf_peak_value': 0.2647, 'acf_peak_lag_s': 1.0, 'acf_peak_bpm': 60.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.2294}

## Notes

- ECG reference: Subject_1_ECG.npy — 574 R-peaks, mean HR 57.4 BPM, SDNN 103.6 ms.
- Beat comparison used a SEARCHED offset of +1.60 s. This is a hypothesis fitted to the data, not a verified synchronisation; the dataset does not publish the ECG-video start offset.
- HR-trace comparison vs ECG: n=588, MAE=33.09 BPM, bias=+32.45 BPM, r=0.064.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
