# Phase 9.0 — Signal validation: Subject 25

## ROI: `forehead` (source: Subject_25_Forehead_.avi)

**Verdict: B - Peak-detection failure** (confidence: high)

Evidence:
- SNR=7.72 dB, spectral concentration=0.312, ACF regularity=0.372 (peak 0.336 @ 62.1 BPM)
- legacy detector: 668 peaks, IBI CV=0.258, implied BPM=66.8; FFT BPM=60.0
- posterior detector: 762 peaks, IBI CV=0.306; regularity legacy=69.0% posterior=25.4%
- motion proxy: frame-diff mean=0.1793 p95=0.7222; low-frequency/cardiac power ratio=3.094; exposure drift=n/a; brightness mean=109.7 std=6.7; saturated=0.000; flat=0.000
- ground truth: 606 true beats, 668 detected, matched=406, missed=200, false=262, sensitivity=0.670, precision=0.608, mean |interval error|=0.0664 s
- The pulse is present (ACF periodicity and/or SNR are adequate) but the detected beats disagree with the reference: the mismatch is in the detector, not in the physiology.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 60.0 |
| snr_db | 7.72 |
| spectral_concentration | 0.3122 |
| n_peaks_legacy | 668 |
| n_peaks_posterior | 762 |
| regularity_legacy_pct | 69.0 |
| regularity_posterior_pct | 25.4 |
| sqi_legacy | 93.2 |
| sqi_posterior | 0.9 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 109.73 |
| brightness_std | 6.67 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1793 |
| frame_diff_p95 | 0.7222 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 667, 'mean_ibi_s': 0.89805, 'std_ibi_s': 0.23168, 'median_ibi_s': 0.9, 'cv': 0.25798, 'rmssd_ms': 313.78, 'pnn50_pct': 86.94, 'min_ibi_s': 0.5, 'max_ibi_s': 1.7, 'implied_bpm': 66.81}
- posterior detector IBI: {'n_intervals': 761, 'mean_ibi_s': 0.78712, 'std_ibi_s': 0.24104, 'median_ibi_s': 0.76667, 'cv': 0.30624, 'rmssd_ms': 316.68, 'pnn50_pct': 86.58, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.7, 'implied_bpm': 76.23}

- autocorrelation: {'acf_peak_value': 0.3361, 'acf_peak_lag_s': 0.9667, 'acf_peak_bpm': 62.07, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.3722}

## ROI: `cheek_left` (source: Subject_25_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=1.40 dB, spectral concentration=0.105, ACF regularity=0.051 (peak 0.175 @ 72.0 BPM)
- legacy detector: 693 peaks, IBI CV=0.280, implied BPM=69.4; FFT BPM=108.0
- posterior detector: 818 peaks, IBI CV=0.312; regularity legacy=66.4% posterior=6.3%
- motion proxy: frame-diff mean=0.0951 p95=0.3728; low-frequency/cardiac power ratio=4.779; exposure drift=n/a; brightness mean=90.3 std=5.6; saturated=0.000; flat=0.000
- ground truth: 606 true beats, 693 detected, matched=263, missed=343, false=430, sensitivity=0.434, precision=0.380, mean |interval error|=0.0756 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 108.0 |
| snr_db | 1.4 |
| spectral_concentration | 0.1051 |
| n_peaks_legacy | 693 |
| n_peaks_posterior | 818 |
| regularity_legacy_pct | 66.4 |
| regularity_posterior_pct | 6.3 |
| sqi_legacy | 76.2 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 90.3 |
| brightness_std | 5.55 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.0951 |
| frame_diff_p95 | 0.3728 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 692, 'mean_ibi_s': 0.86435, 'std_ibi_s': 0.24235, 'median_ibi_s': 0.83333, 'cv': 0.28039, 'rmssd_ms': 339.35, 'pnn50_pct': 87.55, 'min_ibi_s': 0.5, 'max_ibi_s': 1.76667, 'implied_bpm': 69.42}
- posterior detector IBI: {'n_intervals': 817, 'mean_ibi_s': 0.7335, 'std_ibi_s': 0.22882, 'median_ibi_s': 0.7, 'cv': 0.31195, 'rmssd_ms': 310.99, 'pnn50_pct': 85.54, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 81.8}

- autocorrelation: {'acf_peak_value': 0.1754, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0507}

## ROI: `cheek_right` (source: Subject_25_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.04 dB, spectral concentration=0.077, ACF regularity=0.060 (peak 0.180 @ 72.0 BPM)
- legacy detector: 709 peaks, IBI CV=0.273, implied BPM=71.0; FFT BPM=120.0
- posterior detector: 800 peaks, IBI CV=0.293; regularity legacy=67.2% posterior=7.7%
- motion proxy: frame-diff mean=0.1271 p95=0.5267; low-frequency/cardiac power ratio=5.861; exposure drift=n/a; brightness mean=97.1 std=5.7; saturated=0.000; flat=0.000
- ground truth: 606 true beats, 709 detected, matched=274, missed=332, false=435, sensitivity=0.452, precision=0.386, mean |interval error|=0.0774 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.04 |
| spectral_concentration | 0.0774 |
| n_peaks_legacy | 709 |
| n_peaks_posterior | 800 |
| regularity_legacy_pct | 67.2 |
| regularity_posterior_pct | 7.7 |
| sqi_legacy | 42.2 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 97.11 |
| brightness_std | 5.68 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1271 |
| frame_diff_p95 | 0.5267 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 708, 'mean_ibi_s': 0.84557, 'std_ibi_s': 0.23121, 'median_ibi_s': 0.8, 'cv': 0.27344, 'rmssd_ms': 325.09, 'pnn50_pct': 86.7, 'min_ibi_s': 0.5, 'max_ibi_s': 1.6, 'implied_bpm': 70.96}
- posterior detector IBI: {'n_intervals': 799, 'mean_ibi_s': 0.74927, 'std_ibi_s': 0.2193, 'median_ibi_s': 0.73333, 'cv': 0.29269, 'rmssd_ms': 304.45, 'pnn50_pct': 86.84, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.46667, 'implied_bpm': 80.08}

- autocorrelation: {'acf_peak_value': 0.1801, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0601}

## Notes

- Subject 25 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_25_ECG.npy - 606 R-peaks, mean HR 60.7 BPM, SDNN 61.0 ms, ECG inter-beat CV 0.062.
- Detector IBI CV across ROIs: 0.258-0.280 (ECG inter-beat CV 0.062). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [60.0, 108.0, 120.0]; detector beat-implied BPM: [66.8, 69.4, 71.0]; ECG mean HR 60.7 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
