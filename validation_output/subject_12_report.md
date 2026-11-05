# Phase 9.0 — Signal validation: Subject 12

## ROI: `forehead` (source: Subject_12_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.46 dB, spectral concentration=0.070, ACF regularity=0.024 (peak 0.162 @ 72.0 BPM)
- legacy detector: 689 peaks, IBI CV=0.289, implied BPM=68.8; FFT BPM=120.0
- posterior detector: 803 peaks, IBI CV=0.312; regularity legacy=65.4% posterior=6.0%
- motion proxy: frame-diff mean=0.1202 p95=0.3477; low-frequency/cardiac power ratio=138.886; exposure drift=n/a; brightness mean=89.3 std=6.8; saturated=0.000; flat=0.000
- ground truth: 874 true beats, 689 detected, matched=387, missed=487, false=302, sensitivity=0.443, precision=0.562, mean |interval error|=0.0737 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.46 |
| spectral_concentration | 0.0703 |
| n_peaks_legacy | 689 |
| n_peaks_posterior | 803 |
| regularity_legacy_pct | 65.4 |
| regularity_posterior_pct | 6.0 |
| sqi_legacy | 42.7 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 89.32 |
| brightness_std | 6.8 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1202 |
| frame_diff_p95 | 0.3477 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 688, 'mean_ibi_s': 0.87156, 'std_ibi_s': 0.25145, 'median_ibi_s': 0.83333, 'cv': 0.28851, 'rmssd_ms': 344.52, 'pnn50_pct': 84.86, 'min_ibi_s': 0.5, 'max_ibi_s': 1.9, 'implied_bpm': 68.84}
- posterior detector IBI: {'n_intervals': 802, 'mean_ibi_s': 0.74767, 'std_ibi_s': 0.23356, 'median_ibi_s': 0.73333, 'cv': 0.31238, 'rmssd_ms': 319.48, 'pnn50_pct': 84.39, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.9, 'implied_bpm': 80.25}

- autocorrelation: {'acf_peak_value': 0.1618, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0237}

## ROI: `cheek_left` (source: Subject_12_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.09 dB, spectral concentration=0.085, ACF regularity=0.036 (peak 0.168 @ 69.2 BPM)
- legacy detector: 696 peaks, IBI CV=0.290, implied BPM=69.6; FFT BPM=120.0
- posterior detector: 811 peaks, IBI CV=0.314; regularity legacy=65.2% posterior=6.2%
- motion proxy: frame-diff mean=0.2167 p95=1.1760; low-frequency/cardiac power ratio=31.435; exposure drift=n/a; brightness mean=72.2 std=4.8; saturated=0.000; flat=0.000
- ground truth: 874 true beats, 696 detected, matched=343, missed=531, false=353, sensitivity=0.392, precision=0.493, mean |interval error|=0.0777 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.09 |
| spectral_concentration | 0.0845 |
| n_peaks_legacy | 696 |
| n_peaks_posterior | 811 |
| regularity_legacy_pct | 65.2 |
| regularity_posterior_pct | 6.2 |
| sqi_legacy | 42.7 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 72.24 |
| brightness_std | 4.79 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2167 |
| frame_diff_p95 | 1.176 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 695, 'mean_ibi_s': 0.86221, 'std_ibi_s': 0.25011, 'median_ibi_s': 0.8, 'cv': 0.29008, 'rmssd_ms': 332.9, 'pnn50_pct': 88.33, 'min_ibi_s': 0.5, 'max_ibi_s': 1.76667, 'implied_bpm': 69.59}
- posterior detector IBI: {'n_intervals': 810, 'mean_ibi_s': 0.73979, 'std_ibi_s': 0.23198, 'median_ibi_s': 0.7, 'cv': 0.31357, 'rmssd_ms': 320.55, 'pnn50_pct': 86.4, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.76667, 'implied_bpm': 81.1}

- autocorrelation: {'acf_peak_value': 0.1681, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0361}

## ROI: `cheek_right` (source: Subject_12_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.08 dB, spectral concentration=0.081, ACF regularity=0.008 (peak 0.154 @ 75.0 BPM)
- legacy detector: 697 peaks, IBI CV=0.284, implied BPM=69.7; FFT BPM=120.0
- posterior detector: 801 peaks, IBI CV=0.305; regularity legacy=66.0% posterior=4.6%
- motion proxy: frame-diff mean=0.2185 p95=1.1360; low-frequency/cardiac power ratio=24.923; exposure drift=n/a; brightness mean=67.4 std=6.7; saturated=0.000; flat=0.000
- ground truth: 874 true beats, 697 detected, matched=366, missed=508, false=331, sensitivity=0.419, precision=0.525, mean |interval error|=0.0752 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | pos |
| bpm_fft | 120.0 |
| snr_db | 0.08 |
| spectral_concentration | 0.0809 |
| n_peaks_legacy | 697 |
| n_peaks_posterior | 801 |
| regularity_legacy_pct | 66.0 |
| regularity_posterior_pct | 4.6 |
| sqi_legacy | 42.6 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 67.41 |
| brightness_std | 6.67 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2185 |
| frame_diff_p95 | 1.136 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 696, 'mean_ibi_s': 0.86087, 'std_ibi_s': 0.24424, 'median_ibi_s': 0.8, 'cv': 0.28372, 'rmssd_ms': 340.09, 'pnn50_pct': 87.05, 'min_ibi_s': 0.5, 'max_ibi_s': 1.76667, 'implied_bpm': 69.7}
- posterior detector IBI: {'n_intervals': 800, 'mean_ibi_s': 0.7495, 'std_ibi_s': 0.22896, 'median_ibi_s': 0.73333, 'cv': 0.30549, 'rmssd_ms': 311.69, 'pnn50_pct': 86.36, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.76667, 'implied_bpm': 80.05}

- autocorrelation: {'acf_peak_value': 0.1539, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0079}

## Notes

- Subject 12 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_12_ECG.npy - 874 R-peaks, mean HR 88.2 BPM, SDNN 26.4 ms, ECG inter-beat CV 0.038.
- Detector IBI CV across ROIs: 0.284-0.290 (ECG inter-beat CV 0.038). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 120.0, 120.0]; detector beat-implied BPM: [68.8, 69.6, 69.7]; ECG mean HR 88.2 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
