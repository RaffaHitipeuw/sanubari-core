# Phase 9.0 — Signal validation: Subject 23

## ROI: `forehead` (source: Subject_23_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.22 dB, spectral concentration=0.065, ACF regularity=0.066 (peak 0.183 @ 72.0 BPM)
- legacy detector: 701 peaks, IBI CV=0.279, implied BPM=70.2; FFT BPM=132.0
- posterior detector: 811 peaks, IBI CV=0.294; regularity legacy=66.5% posterior=8.7%
- motion proxy: frame-diff mean=0.1591 p95=0.4958; low-frequency/cardiac power ratio=14.542; exposure drift=n/a; brightness mean=92.2 std=5.8; saturated=0.000; flat=0.000
- ground truth: 871 true beats, 701 detected, matched=370, missed=501, false=331, sensitivity=0.425, precision=0.528, mean |interval error|=0.0717 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | chrom |
| bpm_fft | 132.0 |
| snr_db | -1.22 |
| spectral_concentration | 0.0649 |
| n_peaks_legacy | 701 |
| n_peaks_posterior | 811 |
| regularity_legacy_pct | 66.5 |
| regularity_posterior_pct | 8.7 |
| sqi_legacy | 38.7 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 92.17 |
| brightness_std | 5.82 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1591 |
| frame_diff_p95 | 0.4958 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 700, 'mean_ibi_s': 0.85505, 'std_ibi_s': 0.2387, 'median_ibi_s': 0.8, 'cv': 0.27916, 'rmssd_ms': 326.84, 'pnn50_pct': 84.69, 'min_ibi_s': 0.5, 'max_ibi_s': 1.73333, 'implied_bpm': 70.17}
- posterior detector IBI: {'n_intervals': 810, 'mean_ibi_s': 0.73893, 'std_ibi_s': 0.2174, 'median_ibi_s': 0.73333, 'cv': 0.29421, 'rmssd_ms': 292.0, 'pnn50_pct': 84.43, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.53333, 'implied_bpm': 81.2}

- autocorrelation: {'acf_peak_value': 0.1831, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0661}

## ROI: `cheek_left` (source: Subject_23_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.42 dB, spectral concentration=0.080, ACF regularity=0.108 (peak 0.204 @ 72.0 BPM)
- legacy detector: 707 peaks, IBI CV=0.272, implied BPM=70.8; FFT BPM=120.0
- posterior detector: 803 peaks, IBI CV=0.298; regularity legacy=67.4% posterior=11.0%
- motion proxy: frame-diff mean=0.2031 p95=1.0174; low-frequency/cardiac power ratio=6.352; exposure drift=n/a; brightness mean=68.0 std=4.2; saturated=0.000; flat=0.000
- ground truth: 871 true beats, 707 detected, matched=342, missed=529, false=365, sensitivity=0.393, precision=0.484, mean |interval error|=0.0729 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.42 |
| spectral_concentration | 0.0803 |
| n_peaks_legacy | 707 |
| n_peaks_posterior | 803 |
| regularity_legacy_pct | 67.4 |
| regularity_posterior_pct | 11.0 |
| sqi_legacy | 43.6 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 68.03 |
| brightness_std | 4.18 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2031 |
| frame_diff_p95 | 1.0174 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 706, 'mean_ibi_s': 0.84792, 'std_ibi_s': 0.23065, 'median_ibi_s': 0.83333, 'cv': 0.27202, 'rmssd_ms': 314.62, 'pnn50_pct': 87.09, 'min_ibi_s': 0.5, 'max_ibi_s': 1.63333, 'implied_bpm': 70.76}
- posterior detector IBI: {'n_intervals': 802, 'mean_ibi_s': 0.74643, 'std_ibi_s': 0.22251, 'median_ibi_s': 0.73333, 'cv': 0.29809, 'rmssd_ms': 302.61, 'pnn50_pct': 86.02, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.46667, 'implied_bpm': 80.38}

- autocorrelation: {'acf_peak_value': 0.2039, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1079}

## ROI: `cheek_right` (source: Subject_23_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.24 dB, spectral concentration=0.084, ACF regularity=0.027 (peak 0.164 @ 69.2 BPM)
- legacy detector: 700 peaks, IBI CV=0.283, implied BPM=70.0; FFT BPM=120.0
- posterior detector: 809 peaks, IBI CV=0.300; regularity legacy=66.1% posterior=4.7%
- motion proxy: frame-diff mean=0.1645 p95=0.8323; low-frequency/cardiac power ratio=8.186; exposure drift=n/a; brightness mean=63.4 std=4.3; saturated=0.000; flat=0.000
- ground truth: 871 true beats, 700 detected, matched=361, missed=510, false=339, sensitivity=0.414, precision=0.516, mean |interval error|=0.0755 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | pos |
| bpm_fft | 120.0 |
| snr_db | 0.24 |
| spectral_concentration | 0.0838 |
| n_peaks_legacy | 700 |
| n_peaks_posterior | 809 |
| regularity_legacy_pct | 66.1 |
| regularity_posterior_pct | 4.7 |
| sqi_legacy | 42.6 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 63.37 |
| brightness_std | 4.26 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1645 |
| frame_diff_p95 | 0.8323 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 699, 'mean_ibi_s': 0.85708, 'std_ibi_s': 0.24235, 'median_ibi_s': 0.83333, 'cv': 0.28276, 'rmssd_ms': 334.74, 'pnn50_pct': 84.81, 'min_ibi_s': 0.5, 'max_ibi_s': 1.83333, 'implied_bpm': 70.01}
- posterior detector IBI: {'n_intervals': 808, 'mean_ibi_s': 0.74146, 'std_ibi_s': 0.22239, 'median_ibi_s': 0.7, 'cv': 0.29994, 'rmssd_ms': 305.69, 'pnn50_pct': 84.39, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 80.92}

- autocorrelation: {'acf_peak_value': 0.1637, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0274}

## Notes

- Subject 23 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_23_ECG.npy - 871 R-peaks, mean HR 87.2 BPM, SDNN 39.4 ms, ECG inter-beat CV 0.057.
- Detector IBI CV across ROIs: 0.272-0.283 (ECG inter-beat CV 0.057). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 120.0, 132.0]; detector beat-implied BPM: [70.2, 70.8, 70.0]; ECG mean HR 87.2 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
