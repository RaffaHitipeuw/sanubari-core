# Phase 9.0 — Signal validation: Subject 13

## ROI: `forehead` (source: Subject_13_Forehead_.avi)

**Verdict: B - Peak-detection failure** (confidence: high)

Evidence:
- SNR=6.26 dB, spectral concentration=0.250, ACF regularity=0.287 (peak 0.294 @ 69.2 BPM)
- legacy detector: 681 peaks, IBI CV=0.262, implied BPM=68.1; FFT BPM=66.0
- posterior detector: 787 peaks, IBI CV=0.299; regularity legacy=68.5% posterior=23.5%
- motion proxy: frame-diff mean=0.1514 p95=0.4666; low-frequency/cardiac power ratio=27.802; exposure drift=n/a; brightness mean=88.4 std=4.7; saturated=0.000; flat=0.000
- ground truth: 679 true beats, 681 detected, matched=337, missed=342, false=344, sensitivity=0.496, precision=0.495, mean |interval error|=0.0757 s
- The pulse is present (ACF periodicity and/or SNR are adequate) but the detected beats disagree with the reference: the mismatch is in the detector, not in the physiology.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 17996 |
| method | green |
| bpm_fft | 66.0 |
| snr_db | 6.26 |
| spectral_concentration | 0.2503 |
| n_peaks_legacy | 681 |
| n_peaks_posterior | 787 |
| regularity_legacy_pct | 68.5 |
| regularity_posterior_pct | 23.5 |
| sqi_legacy | 86.9 |
| sqi_posterior | 0.4 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 88.39 |
| brightness_std | 4.65 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1514 |
| frame_diff_p95 | 0.4666 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 680, 'mean_ibi_s': 0.88103, 'std_ibi_s': 0.23095, 'median_ibi_s': 0.83333, 'cv': 0.26214, 'rmssd_ms': 330.12, 'pnn50_pct': 85.13, 'min_ibi_s': 0.5, 'max_ibi_s': 1.7, 'implied_bpm': 68.1}
- posterior detector IBI: {'n_intervals': 786, 'mean_ibi_s': 0.76281, 'std_ibi_s': 0.22791, 'median_ibi_s': 0.76667, 'cv': 0.29878, 'rmssd_ms': 306.42, 'pnn50_pct': 84.2, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.63333, 'implied_bpm': 78.66}

- autocorrelation: {'acf_peak_value': 0.2936, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.2872}

## ROI: `cheek_left` (source: Subject_13_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.31 dB, spectral concentration=0.064, ACF regularity=0.119 (peak 0.210 @ 69.2 BPM)
- legacy detector: 699 peaks, IBI CV=0.272, implied BPM=69.9; FFT BPM=132.0
- posterior detector: 808 peaks, IBI CV=0.298; regularity legacy=67.3% posterior=11.5%
- motion proxy: frame-diff mean=0.2105 p95=0.9681; low-frequency/cardiac power ratio=30.238; exposure drift=n/a; brightness mean=68.5 std=3.5; saturated=0.000; flat=0.000
- ground truth: 679 true beats, 699 detected, matched=302, missed=377, false=397, sensitivity=0.445, precision=0.432, mean |interval error|=0.0745 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 17996 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -1.31 |
| spectral_concentration | 0.0643 |
| n_peaks_legacy | 699 |
| n_peaks_posterior | 808 |
| regularity_legacy_pct | 67.3 |
| regularity_posterior_pct | 11.5 |
| sqi_legacy | 38.3 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 68.49 |
| brightness_std | 3.53 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2105 |
| frame_diff_p95 | 0.9681 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 698, 'mean_ibi_s': 0.85821, 'std_ibi_s': 0.23361, 'median_ibi_s': 0.83333, 'cv': 0.27221, 'rmssd_ms': 315.04, 'pnn50_pct': 87.52, 'min_ibi_s': 0.5, 'max_ibi_s': 2.06667, 'implied_bpm': 69.91}
- posterior detector IBI: {'n_intervals': 807, 'mean_ibi_s': 0.7423, 'std_ibi_s': 0.22088, 'median_ibi_s': 0.73333, 'cv': 0.29756, 'rmssd_ms': 298.3, 'pnn50_pct': 86.6, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 80.83}

- autocorrelation: {'acf_peak_value': 0.2096, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1192}

## ROI: `cheek_right` (source: Subject_13_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.46 dB, spectral concentration=0.071, ACF regularity=0.067 (peak 0.184 @ 69.2 BPM)
- legacy detector: 713 peaks, IBI CV=0.282, implied BPM=71.3; FFT BPM=120.0
- posterior detector: 806 peaks, IBI CV=0.297; regularity legacy=66.1% posterior=8.0%
- motion proxy: frame-diff mean=0.2842 p95=1.1907; low-frequency/cardiac power ratio=25.317; exposure drift=n/a; brightness mean=67.8 std=3.7; saturated=0.000; flat=0.000
- ground truth: 679 true beats, 713 detected, matched=311, missed=368, false=402, sensitivity=0.458, precision=0.436, mean |interval error|=0.0727 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 17996 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.46 |
| spectral_concentration | 0.0712 |
| n_peaks_legacy | 713 |
| n_peaks_posterior | 806 |
| regularity_legacy_pct | 66.1 |
| regularity_posterior_pct | 8.0 |
| sqi_legacy | 42.9 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 67.83 |
| brightness_std | 3.7 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2842 |
| frame_diff_p95 | 1.1907 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 712, 'mean_ibi_s': 0.84148, 'std_ibi_s': 0.23755, 'median_ibi_s': 0.8, 'cv': 0.2823, 'rmssd_ms': 326.14, 'pnn50_pct': 87.2, 'min_ibi_s': 0.5, 'max_ibi_s': 1.66667, 'implied_bpm': 71.3}
- posterior detector IBI: {'n_intervals': 805, 'mean_ibi_s': 0.74427, 'std_ibi_s': 0.22124, 'median_ibi_s': 0.73333, 'cv': 0.29726, 'rmssd_ms': 304.5, 'pnn50_pct': 86.44, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.63333, 'implied_bpm': 80.62}

- autocorrelation: {'acf_peak_value': 0.1837, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0674}

## Notes

- Subject 13 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_13_ECG.npy - 679 R-peaks, mean HR 67.7 BPM, SDNN 69.6 ms, ECG inter-beat CV 0.079.
- Detector IBI CV across ROIs: 0.262-0.282 (ECG inter-beat CV 0.079). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [66.0, 120.0, 132.0]; detector beat-implied BPM: [68.1, 69.9, 71.3]; ECG mean HR 67.7 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
