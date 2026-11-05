# Phase 9.0 — Signal validation: Subject 5

## ROI: `forehead` (source: Subject_5_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.39 dB, spectral concentration=0.063, ACF regularity=0.050 (peak 0.175 @ 75.0 BPM)
- legacy detector: 713 peaks, IBI CV=0.275, implied BPM=71.3; FFT BPM=132.0
- posterior detector: 814 peaks, IBI CV=0.293; regularity legacy=67.0% posterior=8.1%
- motion proxy: frame-diff mean=0.2001 p95=0.6050; low-frequency/cardiac power ratio=2.078; exposure drift=n/a; brightness mean=95.5 std=1.3; saturated=0.000; flat=0.000
- ground truth: 816 true beats, 713 detected, matched=372, missed=444, false=341, sensitivity=0.456, precision=0.522, mean |interval error|=0.0718 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -1.39 |
| spectral_concentration | 0.0626 |
| n_peaks_legacy | 713 |
| n_peaks_posterior | 814 |
| regularity_legacy_pct | 67.0 |
| regularity_posterior_pct | 8.1 |
| sqi_legacy | 38.8 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 95.54 |
| brightness_std | 1.27 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2001 |
| frame_diff_p95 | 0.605 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 712, 'mean_ibi_s': 0.84143, 'std_ibi_s': 0.23169, 'median_ibi_s': 0.8, 'cv': 0.27535, 'rmssd_ms': 316.96, 'pnn50_pct': 84.39, 'min_ibi_s': 0.5, 'max_ibi_s': 1.76667, 'implied_bpm': 71.31}
- posterior detector IBI: {'n_intervals': 813, 'mean_ibi_s': 0.7369, 'std_ibi_s': 0.21607, 'median_ibi_s': 0.73333, 'cv': 0.29321, 'rmssd_ms': 304.43, 'pnn50_pct': 85.59, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.5, 'implied_bpm': 81.42}

- autocorrelation: {'acf_peak_value': 0.175, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0501}

## ROI: `cheek_left` (source: Subject_5_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.39 dB, spectral concentration=0.077, ACF regularity=0.044 (peak 0.172 @ 72.0 BPM)
- legacy detector: 715 peaks, IBI CV=0.282, implied BPM=71.6; FFT BPM=132.0
- posterior detector: 817 peaks, IBI CV=0.305; regularity legacy=66.1% posterior=5.5%
- motion proxy: frame-diff mean=0.2062 p95=0.6667; low-frequency/cardiac power ratio=2.363; exposure drift=n/a; brightness mean=76.3 std=2.0; saturated=0.000; flat=0.000
- ground truth: 816 true beats, 715 detected, matched=341, missed=475, false=374, sensitivity=0.418, precision=0.477, mean |interval error|=0.0756 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.39 |
| spectral_concentration | 0.0773 |
| n_peaks_legacy | 715 |
| n_peaks_posterior | 817 |
| regularity_legacy_pct | 66.1 |
| regularity_posterior_pct | 5.5 |
| sqi_legacy | 38.6 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 76.31 |
| brightness_std | 2.05 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2062 |
| frame_diff_p95 | 0.6667 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 714, 'mean_ibi_s': 0.83838, 'std_ibi_s': 0.23681, 'median_ibi_s': 0.8, 'cv': 0.28246, 'rmssd_ms': 319.41, 'pnn50_pct': 86.68, 'min_ibi_s': 0.5, 'max_ibi_s': 1.73333, 'implied_bpm': 71.57}
- posterior detector IBI: {'n_intervals': 816, 'mean_ibi_s': 0.73358, 'std_ibi_s': 0.22384, 'median_ibi_s': 0.7, 'cv': 0.30513, 'rmssd_ms': 304.1, 'pnn50_pct': 85.64, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 81.79}

- autocorrelation: {'acf_peak_value': 0.1718, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0437}

## ROI: `cheek_right` (source: Subject_5_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.29 dB, spectral concentration=0.086, ACF regularity=0.127 (peak 0.213 @ 72.0 BPM)
- legacy detector: 695 peaks, IBI CV=0.275, implied BPM=69.5; FFT BPM=120.0
- posterior detector: 811 peaks, IBI CV=0.308; regularity legacy=67.0% posterior=11.7%
- motion proxy: frame-diff mean=0.1250 p95=0.3872; low-frequency/cardiac power ratio=3.270; exposure drift=n/a; brightness mean=81.5 std=1.1; saturated=0.000; flat=0.000
- ground truth: 816 true beats, 695 detected, matched=305, missed=511, false=390, sensitivity=0.374, precision=0.439, mean |interval error|=0.0792 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.29 |
| spectral_concentration | 0.0864 |
| n_peaks_legacy | 695 |
| n_peaks_posterior | 811 |
| regularity_legacy_pct | 67.0 |
| regularity_posterior_pct | 11.7 |
| sqi_legacy | 42.5 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 81.49 |
| brightness_std | 1.1 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.125 |
| frame_diff_p95 | 0.3872 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 694, 'mean_ibi_s': 0.86311, 'std_ibi_s': 0.23749, 'median_ibi_s': 0.83333, 'cv': 0.27515, 'rmssd_ms': 329.21, 'pnn50_pct': 86.0, 'min_ibi_s': 0.5, 'max_ibi_s': 1.86667, 'implied_bpm': 69.52}
- posterior detector IBI: {'n_intervals': 810, 'mean_ibi_s': 0.73951, 'std_ibi_s': 0.22802, 'median_ibi_s': 0.73333, 'cv': 0.30835, 'rmssd_ms': 304.41, 'pnn50_pct': 84.3, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.6, 'implied_bpm': 81.14}

- autocorrelation: {'acf_peak_value': 0.2135, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1269}

## Notes

- Subject 5 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_5_ECG.npy - 816 R-peaks, mean HR 81.7 BPM, SDNN 43.0 ms, ECG inter-beat CV 0.059.
- Detector IBI CV across ROIs: 0.275-0.282 (ECG inter-beat CV 0.059). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 132.0, 132.0]; detector beat-implied BPM: [71.3, 71.6, 69.5]; ECG mean HR 81.7 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
