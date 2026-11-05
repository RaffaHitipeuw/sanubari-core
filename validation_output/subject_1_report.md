# Phase 9.0 — Signal validation: Subject 1

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

## ROI: `cheek_left` (source: Subject_1_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.11 dB, spectral concentration=0.079, ACF regularity=0.106 (peak 0.203 @ 64.3 BPM)
- legacy detector: 691 peaks, IBI CV=0.273, implied BPM=69.1; FFT BPM=120.0
- posterior detector: 809 peaks, IBI CV=0.304; regularity legacy=67.2% posterior=8.2%
- motion proxy: frame-diff mean=0.0770 p95=0.2515; low-frequency/cardiac power ratio=1.797; exposure drift=n/a; brightness mean=90.8 std=2.5; saturated=0.000; flat=0.000
- ground truth: 574 true beats, 691 detected, matched=276, missed=298, false=415, sensitivity=0.481, precision=0.399, mean |interval error|=0.0761 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.11 |
| spectral_concentration | 0.0787 |
| n_peaks_legacy | 691 |
| n_peaks_posterior | 809 |
| regularity_legacy_pct | 67.2 |
| regularity_posterior_pct | 8.2 |
| sqi_legacy | 43.3 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 90.85 |
| brightness_std | 2.51 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.077 |
| frame_diff_p95 | 0.2515 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 690, 'mean_ibi_s': 0.86841, 'std_ibi_s': 0.23731, 'median_ibi_s': 0.83333, 'cv': 0.27327, 'rmssd_ms': 330.08, 'pnn50_pct': 89.11, 'min_ibi_s': 0.5, 'max_ibi_s': 1.66667, 'implied_bpm': 69.09}
- posterior detector IBI: {'n_intervals': 808, 'mean_ibi_s': 0.74109, 'std_ibi_s': 0.22557, 'median_ibi_s': 0.7, 'cv': 0.30438, 'rmssd_ms': 303.11, 'pnn50_pct': 86.86, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.46667, 'implied_bpm': 80.96}

- autocorrelation: {'acf_peak_value': 0.2032, 'acf_peak_lag_s': 0.9333, 'acf_peak_bpm': 64.29, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1064}

## ROI: `cheek_right` (source: Subject_1_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.12 dB, spectral concentration=0.082, ACF regularity=0.066 (peak 0.183 @ 64.3 BPM)
- legacy detector: 697 peaks, IBI CV=0.279, implied BPM=69.9; FFT BPM=120.0
- posterior detector: 820 peaks, IBI CV=0.300; regularity legacy=66.5% posterior=5.6%
- motion proxy: frame-diff mean=0.0777 p95=0.2554; low-frequency/cardiac power ratio=1.878; exposure drift=n/a; brightness mean=100.7 std=1.7; saturated=0.000; flat=0.000
- ground truth: 574 true beats, 697 detected, matched=268, missed=306, false=429, sensitivity=0.467, precision=0.385, mean |interval error|=0.0723 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.12 |
| spectral_concentration | 0.0818 |
| n_peaks_legacy | 697 |
| n_peaks_posterior | 820 |
| regularity_legacy_pct | 66.5 |
| regularity_posterior_pct | 5.6 |
| sqi_legacy | 43.2 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 100.69 |
| brightness_std | 1.65 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.0777 |
| frame_diff_p95 | 0.2554 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 696, 'mean_ibi_s': 0.85848, 'std_ibi_s': 0.2396, 'median_ibi_s': 0.83333, 'cv': 0.27909, 'rmssd_ms': 338.15, 'pnn50_pct': 87.77, 'min_ibi_s': 0.5, 'max_ibi_s': 1.66667, 'implied_bpm': 69.89}
- posterior detector IBI: {'n_intervals': 819, 'mean_ibi_s': 0.73138, 'std_ibi_s': 0.21963, 'median_ibi_s': 0.7, 'cv': 0.30029, 'rmssd_ms': 305.45, 'pnn50_pct': 86.43, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 82.04}

- autocorrelation: {'acf_peak_value': 0.183, 'acf_peak_lag_s': 0.9333, 'acf_peak_bpm': 64.29, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0659}

## Notes

- Subject 1 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_1_ECG.npy - 574 R-peaks, mean HR 57.4 BPM, SDNN 103.6 ms, ECG inter-beat CV 0.099.
- Detector IBI CV across ROIs: 0.267-0.279 (ECG inter-beat CV 0.099). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 120.0, 120.0]; detector beat-implied BPM: [67.6, 69.1, 69.9]; ECG mean HR 57.4 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
