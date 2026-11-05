# Phase 9.0 — Signal validation: Subject 19

## ROI: `forehead` (source: Subject_19_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=3.94 dB, spectral concentration=0.193, ACF regularity=0.131 (peak 0.216 @ 72.0 BPM)
- legacy detector: 706 peaks, IBI CV=0.279, implied BPM=70.6; FFT BPM=78.0
- posterior detector: 808 peaks, IBI CV=0.296; regularity legacy=66.5% posterior=12.7%
- motion proxy: frame-diff mean=0.1358 p95=0.4822; low-frequency/cardiac power ratio=16.290; exposure drift=n/a; brightness mean=91.8 std=3.8; saturated=0.000; flat=0.000
- ground truth: 775 true beats, 706 detected, matched=343, missed=432, false=363, sensitivity=0.443, precision=0.486, mean |interval error|=0.0706 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 78.0 |
| snr_db | 3.94 |
| spectral_concentration | 0.1925 |
| n_peaks_legacy | 706 |
| n_peaks_posterior | 808 |
| regularity_legacy_pct | 66.5 |
| regularity_posterior_pct | 12.7 |
| sqi_legacy | 79.1 |
| sqi_posterior | 0.1 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 91.77 |
| brightness_std | 3.8 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1358 |
| frame_diff_p95 | 0.4822 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 705, 'mean_ibi_s': 0.84931, 'std_ibi_s': 0.23716, 'median_ibi_s': 0.8, 'cv': 0.27923, 'rmssd_ms': 322.96, 'pnn50_pct': 87.07, 'min_ibi_s': 0.5, 'max_ibi_s': 1.96667, 'implied_bpm': 70.65}
- posterior detector IBI: {'n_intervals': 807, 'mean_ibi_s': 0.7425, 'std_ibi_s': 0.21943, 'median_ibi_s': 0.73333, 'cv': 0.29553, 'rmssd_ms': 298.91, 'pnn50_pct': 86.97, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 80.81}

- autocorrelation: {'acf_peak_value': 0.2155, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.131}

## ROI: `cheek_left` (source: Subject_19_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.37 dB, spectral concentration=0.084, ACF regularity=0.053 (peak 0.176 @ 75.0 BPM)
- legacy detector: 695 peaks, IBI CV=0.294, implied BPM=69.5; FFT BPM=120.0
- posterior detector: 818 peaks, IBI CV=0.308; regularity legacy=64.8% posterior=7.3%
- motion proxy: frame-diff mean=0.0899 p95=0.3250; low-frequency/cardiac power ratio=22.814; exposure drift=n/a; brightness mean=86.9 std=4.1; saturated=0.000; flat=0.000
- ground truth: 775 true beats, 695 detected, matched=325, missed=450, false=370, sensitivity=0.419, precision=0.468, mean |interval error|=0.0753 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.37 |
| spectral_concentration | 0.0836 |
| n_peaks_legacy | 695 |
| n_peaks_posterior | 818 |
| regularity_legacy_pct | 64.8 |
| regularity_posterior_pct | 7.3 |
| sqi_legacy | 42.7 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 86.88 |
| brightness_std | 4.06 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.0899 |
| frame_diff_p95 | 0.325 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 694, 'mean_ibi_s': 0.86311, 'std_ibi_s': 0.25339, 'median_ibi_s': 0.8, 'cv': 0.29357, 'rmssd_ms': 358.13, 'pnn50_pct': 85.71, 'min_ibi_s': 0.5, 'max_ibi_s': 2.0, 'implied_bpm': 69.52}
- posterior detector IBI: {'n_intervals': 817, 'mean_ibi_s': 0.73317, 'std_ibi_s': 0.22563, 'median_ibi_s': 0.7, 'cv': 0.30775, 'rmssd_ms': 317.29, 'pnn50_pct': 84.19, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.66667, 'implied_bpm': 81.84}

- autocorrelation: {'acf_peak_value': 0.1763, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0526}

## ROI: `cheek_right` (source: Subject_19_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.63 dB, spectral concentration=0.069, ACF regularity=0.114 (peak 0.207 @ 72.0 BPM)
- legacy detector: 705 peaks, IBI CV=0.283, implied BPM=70.5; FFT BPM=132.0
- posterior detector: 814 peaks, IBI CV=0.305; regularity legacy=66.0% posterior=11.7%
- motion proxy: frame-diff mean=0.1125 p95=0.4847; low-frequency/cardiac power ratio=16.873; exposure drift=n/a; brightness mean=82.0 std=3.2; saturated=0.000; flat=0.000
- ground truth: 775 true beats, 705 detected, matched=341, missed=434, false=364, sensitivity=0.440, precision=0.484, mean |interval error|=0.0696 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.63 |
| spectral_concentration | 0.0692 |
| n_peaks_legacy | 705 |
| n_peaks_posterior | 814 |
| regularity_legacy_pct | 66.0 |
| regularity_posterior_pct | 11.7 |
| sqi_legacy | 38.5 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 81.98 |
| brightness_std | 3.2 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1125 |
| frame_diff_p95 | 0.4847 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 704, 'mean_ibi_s': 0.85057, 'std_ibi_s': 0.24105, 'median_ibi_s': 0.83333, 'cv': 0.2834, 'rmssd_ms': 332.9, 'pnn50_pct': 85.63, 'min_ibi_s': 0.5, 'max_ibi_s': 1.7, 'implied_bpm': 70.54}
- posterior detector IBI: {'n_intervals': 813, 'mean_ibi_s': 0.73752, 'std_ibi_s': 0.22523, 'median_ibi_s': 0.73333, 'cv': 0.30539, 'rmssd_ms': 310.76, 'pnn50_pct': 86.08, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.7, 'implied_bpm': 81.35}

- autocorrelation: {'acf_peak_value': 0.2072, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1144}

## Notes

- Subject 19 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_19_ECG.npy - 775 R-peaks, mean HR 77.6 BPM, SDNN 71.4 ms, ECG inter-beat CV 0.092.
- Detector IBI CV across ROIs: 0.279-0.294 (ECG inter-beat CV 0.092). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [78.0, 120.0, 132.0]; detector beat-implied BPM: [70.6, 69.5, 70.5]; ECG mean HR 77.6 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
