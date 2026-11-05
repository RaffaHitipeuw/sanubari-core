# Phase 9.0 — Signal validation: Subject 14

## ROI: `forehead` (source: Subject_14_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=3.93 dB, spectral concentration=0.198, ACF regularity=0.086 (peak 0.193 @ 69.2 BPM)
- legacy detector: 700 peaks, IBI CV=0.283, implied BPM=70.0; FFT BPM=78.0
- posterior detector: 811 peaks, IBI CV=0.300; regularity legacy=66.0% posterior=8.6%
- motion proxy: frame-diff mean=0.1256 p95=0.4158; low-frequency/cardiac power ratio=20.157; exposure drift=n/a; brightness mean=83.1 std=5.1; saturated=0.000; flat=0.000
- ground truth: 915 true beats, 700 detected, matched=402, missed=513, false=298, sensitivity=0.439, precision=0.574, mean |interval error|=0.0750 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 78.0 |
| snr_db | 3.93 |
| spectral_concentration | 0.1977 |
| n_peaks_legacy | 700 |
| n_peaks_posterior | 811 |
| regularity_legacy_pct | 66.0 |
| regularity_posterior_pct | 8.6 |
| sqi_legacy | 78.3 |
| sqi_posterior | 0.1 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 83.14 |
| brightness_std | 5.07 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1256 |
| frame_diff_p95 | 0.4158 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 699, 'mean_ibi_s': 0.85732, 'std_ibi_s': 0.24297, 'median_ibi_s': 0.83333, 'cv': 0.2834, 'rmssd_ms': 353.45, 'pnn50_pct': 88.68, 'min_ibi_s': 0.5, 'max_ibi_s': 1.7, 'implied_bpm': 69.99}
- posterior detector IBI: {'n_intervals': 810, 'mean_ibi_s': 0.73934, 'std_ibi_s': 0.22183, 'median_ibi_s': 0.73333, 'cv': 0.30004, 'rmssd_ms': 313.69, 'pnn50_pct': 87.27, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.5, 'implied_bpm': 81.15}

- autocorrelation: {'acf_peak_value': 0.1928, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0857}

## ROI: `cheek_left` (source: Subject_14_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.04 dB, spectral concentration=0.083, ACF regularity=0.088 (peak 0.194 @ 69.2 BPM)
- legacy detector: 716 peaks, IBI CV=0.260, implied BPM=71.7; FFT BPM=120.0
- posterior detector: 806 peaks, IBI CV=0.292; regularity legacy=68.8% posterior=9.7%
- motion proxy: frame-diff mean=0.2019 p95=1.2399; low-frequency/cardiac power ratio=7.229; exposure drift=n/a; brightness mean=67.3 std=4.0; saturated=0.000; flat=0.000
- ground truth: 915 true beats, 716 detected, matched=396, missed=519, false=320, sensitivity=0.433, precision=0.553, mean |interval error|=0.0701 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | pos |
| bpm_fft | 120.0 |
| snr_db | 0.04 |
| spectral_concentration | 0.0825 |
| n_peaks_legacy | 716 |
| n_peaks_posterior | 806 |
| regularity_legacy_pct | 68.8 |
| regularity_posterior_pct | 9.7 |
| sqi_legacy | 42.9 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 67.34 |
| brightness_std | 3.98 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2019 |
| frame_diff_p95 | 1.2399 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 715, 'mean_ibi_s': 0.83702, 'std_ibi_s': 0.21754, 'median_ibi_s': 0.8, 'cv': 0.2599, 'rmssd_ms': 306.91, 'pnn50_pct': 87.25, 'min_ibi_s': 0.5, 'max_ibi_s': 1.63333, 'implied_bpm': 71.68}
- posterior detector IBI: {'n_intervals': 805, 'mean_ibi_s': 0.74406, 'std_ibi_s': 0.21731, 'median_ibi_s': 0.73333, 'cv': 0.29206, 'rmssd_ms': 290.05, 'pnn50_pct': 85.45, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.63333, 'implied_bpm': 80.64}

- autocorrelation: {'acf_peak_value': 0.194, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.088}

## ROI: `cheek_right` (source: Subject_14_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.21 dB, spectral concentration=0.063, ACF regularity=0.040 (peak 0.170 @ 72.0 BPM)
- legacy detector: 712 peaks, IBI CV=0.282, implied BPM=71.3; FFT BPM=132.0
- posterior detector: 804 peaks, IBI CV=0.304; regularity legacy=66.2% posterior=5.5%
- motion proxy: frame-diff mean=0.1854 p95=1.0391; low-frequency/cardiac power ratio=11.685; exposure drift=n/a; brightness mean=60.6 std=4.1; saturated=0.000; flat=0.000
- ground truth: 915 true beats, 712 detected, matched=403, missed=512, false=309, sensitivity=0.440, precision=0.566, mean |interval error|=0.0732 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | chrom |
| bpm_fft | 132.0 |
| snr_db | -1.21 |
| spectral_concentration | 0.0634 |
| n_peaks_legacy | 712 |
| n_peaks_posterior | 804 |
| regularity_legacy_pct | 66.2 |
| regularity_posterior_pct | 5.5 |
| sqi_legacy | 38.2 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 60.64 |
| brightness_std | 4.12 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1854 |
| frame_diff_p95 | 1.0391 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 711, 'mean_ibi_s': 0.84168, 'std_ibi_s': 0.23711, 'median_ibi_s': 0.8, 'cv': 0.28171, 'rmssd_ms': 331.68, 'pnn50_pct': 87.46, 'min_ibi_s': 0.5, 'max_ibi_s': 1.86667, 'implied_bpm': 71.29}
- posterior detector IBI: {'n_intervals': 803, 'mean_ibi_s': 0.74579, 'std_ibi_s': 0.2266, 'median_ibi_s': 0.73333, 'cv': 0.30384, 'rmssd_ms': 311.71, 'pnn50_pct': 85.66, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.86667, 'implied_bpm': 80.45}

- autocorrelation: {'acf_peak_value': 0.1699, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0398}

## Notes

- Subject 14 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_14_ECG.npy - 915 R-peaks, mean HR 90.8 BPM, SDNN 154.6 ms, ECG inter-beat CV 0.236.
- Detector IBI CV across ROIs: 0.260-0.283 (ECG inter-beat CV 0.236). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [78.0, 120.0, 132.0]; detector beat-implied BPM: [70.0, 71.7, 71.3]; ECG mean HR 90.8 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
