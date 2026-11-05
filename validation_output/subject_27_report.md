# Phase 9.0 — Signal validation: Subject 27

## ROI: `forehead` (source: Subject_27_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.54 dB, spectral concentration=0.072, ACF regularity=0.090 (peak 0.195 @ 75.0 BPM)
- legacy detector: 723 peaks, IBI CV=0.287, implied BPM=72.3; FFT BPM=132.0
- posterior detector: 817 peaks, IBI CV=0.298; regularity legacy=65.6% posterior=10.1%
- motion proxy: frame-diff mean=0.1306 p95=0.3936; low-frequency/cardiac power ratio=5.042; exposure drift=n/a; brightness mean=88.7 std=3.4; saturated=0.000; flat=0.000
- ground truth: 816 true beats, 723 detected, matched=360, missed=456, false=363, sensitivity=0.441, precision=0.498, mean |interval error|=0.0747 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.54 |
| spectral_concentration | 0.072 |
| n_peaks_legacy | 723 |
| n_peaks_posterior | 817 |
| regularity_legacy_pct | 65.6 |
| regularity_posterior_pct | 10.1 |
| sqi_legacy | 38.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 88.68 |
| brightness_std | 3.45 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1306 |
| frame_diff_p95 | 0.3936 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 722, 'mean_ibi_s': 0.82959, 'std_ibi_s': 0.23789, 'median_ibi_s': 0.8, 'cv': 0.28675, 'rmssd_ms': 337.6, 'pnn50_pct': 86.69, 'min_ibi_s': 0.5, 'max_ibi_s': 1.86667, 'implied_bpm': 72.32}
- posterior detector IBI: {'n_intervals': 816, 'mean_ibi_s': 0.73403, 'std_ibi_s': 0.21883, 'median_ibi_s': 0.7, 'cv': 0.29812, 'rmssd_ms': 314.03, 'pnn50_pct': 86.5, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 81.74}

- autocorrelation: {'acf_peak_value': 0.1948, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0896}

## ROI: `cheek_left` (source: Subject_27_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.33 dB, spectral concentration=0.077, ACF regularity=0.048 (peak 0.174 @ 72.0 BPM)
- legacy detector: 716 peaks, IBI CV=0.286, implied BPM=71.6; FFT BPM=132.0
- posterior detector: 837 peaks, IBI CV=0.300; regularity legacy=65.6% posterior=6.1%
- motion proxy: frame-diff mean=0.0800 p95=0.2681; low-frequency/cardiac power ratio=3.299; exposure drift=n/a; brightness mean=85.2 std=4.9; saturated=0.000; flat=0.000
- ground truth: 816 true beats, 716 detected, matched=345, missed=471, false=371, sensitivity=0.423, precision=0.482, mean |interval error|=0.0749 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.33 |
| spectral_concentration | 0.0774 |
| n_peaks_legacy | 716 |
| n_peaks_posterior | 837 |
| regularity_legacy_pct | 65.6 |
| regularity_posterior_pct | 6.1 |
| sqi_legacy | 38.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 85.23 |
| brightness_std | 4.89 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.08 |
| frame_diff_p95 | 0.2681 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 715, 'mean_ibi_s': 0.83837, 'std_ibi_s': 0.24008, 'median_ibi_s': 0.8, 'cv': 0.28637, 'rmssd_ms': 342.38, 'pnn50_pct': 86.69, 'min_ibi_s': 0.5, 'max_ibi_s': 2.0, 'implied_bpm': 71.57}
- posterior detector IBI: {'n_intervals': 836, 'mean_ibi_s': 0.71703, 'std_ibi_s': 0.21516, 'median_ibi_s': 0.7, 'cv': 0.30008, 'rmssd_ms': 293.53, 'pnn50_pct': 85.39, 'min_ibi_s': 0.43333, 'max_ibi_s': 2.0, 'implied_bpm': 83.68}

- autocorrelation: {'acf_peak_value': 0.1741, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0481}

## ROI: `cheek_right` (source: Subject_27_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.70 dB, spectral concentration=0.098, ACF regularity=0.011 (peak 0.156 @ 72.0 BPM)
- legacy detector: 710 peaks, IBI CV=0.282, implied BPM=71.0; FFT BPM=120.0
- posterior detector: 829 peaks, IBI CV=0.309; regularity legacy=66.2% posterior=3.2%
- motion proxy: frame-diff mean=0.1098 p95=0.4536; low-frequency/cardiac power ratio=2.479; exposure drift=n/a; brightness mean=78.7 std=2.1; saturated=0.000; flat=0.000
- ground truth: 816 true beats, 710 detected, matched=314, missed=502, false=396, sensitivity=0.385, precision=0.442, mean |interval error|=0.0785 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.7 |
| spectral_concentration | 0.0982 |
| n_peaks_legacy | 710 |
| n_peaks_posterior | 829 |
| regularity_legacy_pct | 66.2 |
| regularity_posterior_pct | 3.2 |
| sqi_legacy | 42.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 78.66 |
| brightness_std | 2.06 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1098 |
| frame_diff_p95 | 0.4536 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 709, 'mean_ibi_s': 0.84452, 'std_ibi_s': 0.23774, 'median_ibi_s': 0.8, 'cv': 0.2815, 'rmssd_ms': 336.59, 'pnn50_pct': 85.59, 'min_ibi_s': 0.5, 'max_ibi_s': 1.66667, 'implied_bpm': 71.05}
- posterior detector IBI: {'n_intervals': 828, 'mean_ibi_s': 0.72371, 'std_ibi_s': 0.22371, 'median_ibi_s': 0.7, 'cv': 0.30912, 'rmssd_ms': 304.44, 'pnn50_pct': 83.31, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 82.91}

- autocorrelation: {'acf_peak_value': 0.1555, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0111}

## Notes

- Subject 27 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_27_ECG.npy - 816 R-peaks, mean HR 81.6 BPM, SDNN 47.5 ms, ECG inter-beat CV 0.065.
- Detector IBI CV across ROIs: 0.282-0.287 (ECG inter-beat CV 0.065). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 132.0, 132.0]; detector beat-implied BPM: [72.3, 71.6, 71.0]; ECG mean HR 81.6 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
