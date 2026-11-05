# Phase 9.0 — Signal validation: Subject 10

## ROI: `forehead` (source: Subject_10_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.60 dB, spectral concentration=0.070, ACF regularity=0.165 (peak 0.232 @ 72.0 BPM)
- legacy detector: 689 peaks, IBI CV=0.271, implied BPM=68.9; FFT BPM=144.0
- posterior detector: 813 peaks, IBI CV=0.296; regularity legacy=67.5% posterior=15.5%
- motion proxy: frame-diff mean=0.1349 p95=0.3999; low-frequency/cardiac power ratio=5.513; exposure drift=n/a; brightness mean=89.4 std=5.1; saturated=0.000; flat=0.000
- ground truth: 753 true beats, 689 detected, matched=331, missed=422, false=358, sensitivity=0.440, precision=0.480, mean |interval error|=0.0724 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 144.0 |
| snr_db | -0.6 |
| spectral_concentration | 0.0701 |
| n_peaks_legacy | 689 |
| n_peaks_posterior | 813 |
| regularity_legacy_pct | 67.5 |
| regularity_posterior_pct | 15.5 |
| sqi_legacy | 39.2 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 89.37 |
| brightness_std | 5.08 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1349 |
| frame_diff_p95 | 0.3999 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 688, 'mean_ibi_s': 0.87088, 'std_ibi_s': 0.23581, 'median_ibi_s': 0.83333, 'cv': 0.27077, 'rmssd_ms': 324.79, 'pnn50_pct': 85.15, 'min_ibi_s': 0.5, 'max_ibi_s': 1.93333, 'implied_bpm': 68.9}
- posterior detector IBI: {'n_intervals': 812, 'mean_ibi_s': 0.73789, 'std_ibi_s': 0.21836, 'median_ibi_s': 0.73333, 'cv': 0.29592, 'rmssd_ms': 302.56, 'pnn50_pct': 84.83, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.46667, 'implied_bpm': 81.31}

- autocorrelation: {'acf_peak_value': 0.2325, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1649}

## ROI: `cheek_left` (source: Subject_10_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.67 dB, spectral concentration=0.086, ACF regularity=0.088 (peak 0.194 @ 72.0 BPM)
- legacy detector: 728 peaks, IBI CV=0.279, implied BPM=72.9; FFT BPM=120.0
- posterior detector: 827 peaks, IBI CV=0.298; regularity legacy=66.6% posterior=9.5%
- motion proxy: frame-diff mean=0.1201 p95=0.4700; low-frequency/cardiac power ratio=5.252; exposure drift=n/a; brightness mean=88.0 std=5.3; saturated=0.000; flat=0.000
- ground truth: 753 true beats, 728 detected, matched=344, missed=409, false=384, sensitivity=0.457, precision=0.473, mean |interval error|=0.0710 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.67 |
| spectral_concentration | 0.0855 |
| n_peaks_legacy | 728 |
| n_peaks_posterior | 827 |
| regularity_legacy_pct | 66.6 |
| regularity_posterior_pct | 9.5 |
| sqi_legacy | 42.3 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 87.97 |
| brightness_std | 5.26 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1201 |
| frame_diff_p95 | 0.47 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 727, 'mean_ibi_s': 0.82357, 'std_ibi_s': 0.22945, 'median_ibi_s': 0.8, 'cv': 0.27861, 'rmssd_ms': 316.69, 'pnn50_pct': 85.81, 'min_ibi_s': 0.5, 'max_ibi_s': 1.73333, 'implied_bpm': 72.85}
- posterior detector IBI: {'n_intervals': 826, 'mean_ibi_s': 0.72486, 'std_ibi_s': 0.21611, 'median_ibi_s': 0.7, 'cv': 0.29815, 'rmssd_ms': 291.95, 'pnn50_pct': 82.55, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.6, 'implied_bpm': 82.77}

- autocorrelation: {'acf_peak_value': 0.1938, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0876}

## ROI: `cheek_right` (source: Subject_10_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.36 dB, spectral concentration=0.076, ACF regularity=0.048 (peak 0.174 @ 75.0 BPM)
- legacy detector: 712 peaks, IBI CV=0.264, implied BPM=71.2; FFT BPM=144.0
- posterior detector: 819 peaks, IBI CV=0.295; regularity legacy=68.3% posterior=7.3%
- motion proxy: frame-diff mean=0.0839 p95=0.2603; low-frequency/cardiac power ratio=6.759; exposure drift=n/a; brightness mean=83.3 std=4.2; saturated=0.000; flat=0.000
- ground truth: 753 true beats, 712 detected, matched=344, missed=409, false=368, sensitivity=0.457, precision=0.483, mean |interval error|=0.0702 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 144.0 |
| snr_db | -0.36 |
| spectral_concentration | 0.0758 |
| n_peaks_legacy | 712 |
| n_peaks_posterior | 819 |
| regularity_legacy_pct | 68.3 |
| regularity_posterior_pct | 7.3 |
| sqi_legacy | 39.7 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 83.35 |
| brightness_std | 4.16 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.0839 |
| frame_diff_p95 | 0.2603 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 711, 'mean_ibi_s': 0.84266, 'std_ibi_s': 0.2227, 'median_ibi_s': 0.8, 'cv': 0.26428, 'rmssd_ms': 313.49, 'pnn50_pct': 87.18, 'min_ibi_s': 0.5, 'max_ibi_s': 1.6, 'implied_bpm': 71.2}
- posterior detector IBI: {'n_intervals': 818, 'mean_ibi_s': 0.73244, 'std_ibi_s': 0.21643, 'median_ibi_s': 0.7, 'cv': 0.29549, 'rmssd_ms': 302.6, 'pnn50_pct': 87.03, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.5, 'implied_bpm': 81.92}

- autocorrelation: {'acf_peak_value': 0.1741, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0482}

## Notes

- Subject 10 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_10_ECG.npy - 753 R-peaks, mean HR 75.1 BPM, SDNN 47.0 ms, ECG inter-beat CV 0.059.
- Detector IBI CV across ROIs: 0.264-0.279 (ECG inter-beat CV 0.059). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 144.00000000000003, 144.00000000000003]; detector beat-implied BPM: [68.9, 72.9, 71.2]; ECG mean HR 75.1 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
