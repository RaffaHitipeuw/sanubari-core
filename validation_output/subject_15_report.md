# Phase 9.0 — Signal validation: Subject 15

## ROI: `forehead` (source: Subject_15_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.32 dB, spectral concentration=0.077, ACF regularity=0.055 (peak 0.177 @ 72.0 BPM)
- legacy detector: 708 peaks, IBI CV=0.273, implied BPM=70.9; FFT BPM=120.0
- posterior detector: 813 peaks, IBI CV=0.304; regularity legacy=67.2% posterior=7.3%
- motion proxy: frame-diff mean=0.1287 p95=0.4316; low-frequency/cardiac power ratio=18.640; exposure drift=n/a; brightness mean=88.5 std=5.3; saturated=0.000; flat=0.000
- ground truth: 697 true beats, 708 detected, matched=311, missed=386, false=397, sensitivity=0.446, precision=0.439, mean |interval error|=0.0750 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.32 |
| spectral_concentration | 0.0774 |
| n_peaks_legacy | 708 |
| n_peaks_posterior | 813 |
| regularity_legacy_pct | 67.2 |
| regularity_posterior_pct | 7.3 |
| sqi_legacy | 42.7 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 88.45 |
| brightness_std | 5.34 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1287 |
| frame_diff_p95 | 0.4316 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 707, 'mean_ibi_s': 0.84639, 'std_ibi_s': 0.23149, 'median_ibi_s': 0.8, 'cv': 0.2735, 'rmssd_ms': 331.31, 'pnn50_pct': 88.1, 'min_ibi_s': 0.5, 'max_ibi_s': 1.7, 'implied_bpm': 70.89}
- posterior detector IBI: {'n_intervals': 812, 'mean_ibi_s': 0.73695, 'std_ibi_s': 0.22369, 'median_ibi_s': 0.7, 'cv': 0.30354, 'rmssd_ms': 313.46, 'pnn50_pct': 86.68, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.53333, 'implied_bpm': 81.42}

- autocorrelation: {'acf_peak_value': 0.1773, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0547}

## ROI: `cheek_left` (source: Subject_15_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=1.36 dB, spectral concentration=0.108, ACF regularity=0.043 (peak 0.171 @ 72.0 BPM)
- legacy detector: 706 peaks, IBI CV=0.287, implied BPM=70.6; FFT BPM=108.0
- posterior detector: 831 peaks, IBI CV=0.308; regularity legacy=65.6% posterior=6.0%
- motion proxy: frame-diff mean=0.2082 p95=1.0572; low-frequency/cardiac power ratio=7.440; exposure drift=n/a; brightness mean=64.8 std=4.2; saturated=0.000; flat=0.000
- ground truth: 697 true beats, 706 detected, matched=288, missed=409, false=418, sensitivity=0.413, precision=0.408, mean |interval error|=0.0720 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 108.0 |
| snr_db | 1.36 |
| spectral_concentration | 0.1083 |
| n_peaks_legacy | 706 |
| n_peaks_posterior | 831 |
| regularity_legacy_pct | 65.6 |
| regularity_posterior_pct | 6.0 |
| sqi_legacy | 78.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 64.83 |
| brightness_std | 4.22 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2082 |
| frame_diff_p95 | 1.0572 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 705, 'mean_ibi_s': 0.8496, 'std_ibi_s': 0.24368, 'median_ibi_s': 0.8, 'cv': 0.28682, 'rmssd_ms': 334.01, 'pnn50_pct': 85.37, 'min_ibi_s': 0.5, 'max_ibi_s': 1.9, 'implied_bpm': 70.62}
- posterior detector IBI: {'n_intervals': 830, 'mean_ibi_s': 0.72165, 'std_ibi_s': 0.22195, 'median_ibi_s': 0.7, 'cv': 0.30755, 'rmssd_ms': 303.45, 'pnn50_pct': 84.56, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 83.14}

- autocorrelation: {'acf_peak_value': 0.1713, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0426}

## ROI: `cheek_right` (source: Subject_15_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.45 dB, spectral concentration=0.072, ACF regularity=0.108 (peak 0.204 @ 72.0 BPM)
- legacy detector: 696 peaks, IBI CV=0.274, implied BPM=69.6; FFT BPM=132.0
- posterior detector: 834 peaks, IBI CV=0.302; regularity legacy=67.1% posterior=10.7%
- motion proxy: frame-diff mean=0.1602 p95=0.7991; low-frequency/cardiac power ratio=14.409; exposure drift=n/a; brightness mean=77.3 std=5.7; saturated=0.000; flat=0.000
- ground truth: 697 true beats, 696 detected, matched=321, missed=376, false=375, sensitivity=0.461, precision=0.461, mean |interval error|=0.0757 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.45 |
| spectral_concentration | 0.0716 |
| n_peaks_legacy | 696 |
| n_peaks_posterior | 834 |
| regularity_legacy_pct | 67.1 |
| regularity_posterior_pct | 10.7 |
| sqi_legacy | 39.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 77.25 |
| brightness_std | 5.75 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1602 |
| frame_diff_p95 | 0.7991 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 695, 'mean_ibi_s': 0.86163, 'std_ibi_s': 0.23596, 'median_ibi_s': 0.83333, 'cv': 0.27385, 'rmssd_ms': 328.28, 'pnn50_pct': 88.9, 'min_ibi_s': 0.5, 'max_ibi_s': 1.6, 'implied_bpm': 69.64}
- posterior detector IBI: {'n_intervals': 833, 'mean_ibi_s': 0.71889, 'std_ibi_s': 0.21714, 'median_ibi_s': 0.7, 'cv': 0.30205, 'rmssd_ms': 291.51, 'pnn50_pct': 84.62, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.5, 'implied_bpm': 83.46}

- autocorrelation: {'acf_peak_value': 0.2038, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1075}

## Notes

- Subject 15 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_15_ECG.npy - 697 R-peaks, mean HR 69.8 BPM, SDNN 82.7 ms, ECG inter-beat CV 0.096.
- Detector IBI CV across ROIs: 0.273-0.287 (ECG inter-beat CV 0.096). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [108.0, 120.0, 132.0]; detector beat-implied BPM: [70.9, 70.6, 69.6]; ECG mean HR 69.8 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
