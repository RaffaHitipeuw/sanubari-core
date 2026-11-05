# Phase 9.0 — Signal validation: Subject 6

## ROI: `forehead` (source: Subject_6_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.14 dB, spectral concentration=0.063, ACF regularity=0.079 (peak 0.189 @ 72.0 BPM)
- legacy detector: 713 peaks, IBI CV=0.294, implied BPM=71.3; FFT BPM=132.0
- posterior detector: 818 peaks, IBI CV=0.309; regularity legacy=64.7% posterior=8.3%
- motion proxy: frame-diff mean=0.1403 p95=0.4998; low-frequency/cardiac power ratio=7.244; exposure drift=n/a; brightness mean=99.7 std=1.2; saturated=0.000; flat=0.000
- ground truth: 925 true beats, 713 detected, matched=402, missed=523, false=311, sensitivity=0.435, precision=0.564, mean |interval error|=0.0695 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -1.14 |
| spectral_concentration | 0.0634 |
| n_peaks_legacy | 713 |
| n_peaks_posterior | 818 |
| regularity_legacy_pct | 64.7 |
| regularity_posterior_pct | 8.3 |
| sqi_legacy | 38.3 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 99.7 |
| brightness_std | 1.22 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1403 |
| frame_diff_p95 | 0.4998 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 712, 'mean_ibi_s': 0.84148, 'std_ibi_s': 0.24756, 'median_ibi_s': 0.8, 'cv': 0.29419, 'rmssd_ms': 345.28, 'pnn50_pct': 87.48, 'min_ibi_s': 0.5, 'max_ibi_s': 1.73333, 'implied_bpm': 71.3}
- posterior detector IBI: {'n_intervals': 817, 'mean_ibi_s': 0.73333, 'std_ibi_s': 0.2268, 'median_ibi_s': 0.7, 'cv': 0.30928, 'rmssd_ms': 316.73, 'pnn50_pct': 86.89, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.43333, 'implied_bpm': 81.82}

- autocorrelation: {'acf_peak_value': 0.1894, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0788}

## ROI: `cheek_left` (source: Subject_6_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=1.13 dB, spectral concentration=0.094, ACF regularity=0.000 (peak 0.148 @ 75.0 BPM)
- legacy detector: 706 peaks, IBI CV=0.287, implied BPM=70.7; FFT BPM=120.0
- posterior detector: 832 peaks, IBI CV=0.306; regularity legacy=65.6% posterior=2.2%
- motion proxy: frame-diff mean=0.1581 p95=0.7975; low-frequency/cardiac power ratio=3.017; exposure drift=n/a; brightness mean=56.4 std=1.0; saturated=0.000; flat=0.000
- ground truth: 925 true beats, 706 detected, matched=374, missed=551, false=332, sensitivity=0.404, precision=0.530, mean |interval error|=0.0768 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | pos |
| bpm_fft | 120.0 |
| snr_db | 1.13 |
| spectral_concentration | 0.0938 |
| n_peaks_legacy | 706 |
| n_peaks_posterior | 832 |
| regularity_legacy_pct | 65.6 |
| regularity_posterior_pct | 2.2 |
| sqi_legacy | 42.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 56.36 |
| brightness_std | 1.01 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1581 |
| frame_diff_p95 | 0.7975 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 705, 'mean_ibi_s': 0.84846, 'std_ibi_s': 0.2432, 'median_ibi_s': 0.8, 'cv': 0.28664, 'rmssd_ms': 325.81, 'pnn50_pct': 83.52, 'min_ibi_s': 0.5, 'max_ibi_s': 1.73333, 'implied_bpm': 70.72}
- posterior detector IBI: {'n_intervals': 831, 'mean_ibi_s': 0.71982, 'std_ibi_s': 0.22042, 'median_ibi_s': 0.7, 'cv': 0.30622, 'rmssd_ms': 303.53, 'pnn50_pct': 83.01, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.6, 'implied_bpm': 83.35}

- autocorrelation: {'acf_peak_value': 0.1478, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0}

## ROI: `cheek_right` (source: Subject_6_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.80 dB, spectral concentration=0.065, ACF regularity=0.059 (peak 0.179 @ 72.0 BPM)
- legacy detector: 698 peaks, IBI CV=0.288, implied BPM=69.7; FFT BPM=132.0
- posterior detector: 822 peaks, IBI CV=0.312; regularity legacy=65.4% posterior=6.5%
- motion proxy: frame-diff mean=0.1847 p95=1.1290; low-frequency/cardiac power ratio=2.232; exposure drift=n/a; brightness mean=75.3 std=1.1; saturated=0.000; flat=0.000
- ground truth: 925 true beats, 698 detected, matched=357, missed=568, false=341, sensitivity=0.386, precision=0.511, mean |interval error|=0.0700 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.8 |
| spectral_concentration | 0.0655 |
| n_peaks_legacy | 698 |
| n_peaks_posterior | 822 |
| regularity_legacy_pct | 65.4 |
| regularity_posterior_pct | 6.5 |
| sqi_legacy | 39.1 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 75.28 |
| brightness_std | 1.1 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1847 |
| frame_diff_p95 | 1.129 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 697, 'mean_ibi_s': 0.86035, 'std_ibi_s': 0.24808, 'median_ibi_s': 0.8, 'cv': 0.28834, 'rmssd_ms': 344.6, 'pnn50_pct': 87.93, 'min_ibi_s': 0.5, 'max_ibi_s': 1.76667, 'implied_bpm': 69.74}
- posterior detector IBI: {'n_intervals': 821, 'mean_ibi_s': 0.73041, 'std_ibi_s': 0.22771, 'median_ibi_s': 0.7, 'cv': 0.31175, 'rmssd_ms': 313.47, 'pnn50_pct': 86.22, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.6, 'implied_bpm': 82.15}

- autocorrelation: {'acf_peak_value': 0.1795, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0589}

## Notes

- Subject 6 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_6_ECG.npy - 925 R-peaks, mean HR 92.6 BPM, SDNN 61.2 ms, ECG inter-beat CV 0.094.
- Detector IBI CV across ROIs: 0.287-0.294 (ECG inter-beat CV 0.094). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 132.0, 132.0]; detector beat-implied BPM: [71.3, 70.7, 69.7]; ECG mean HR 92.6 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
