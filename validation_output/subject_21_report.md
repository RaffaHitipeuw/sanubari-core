# Phase 9.0 — Signal validation: Subject 21

## ROI: `forehead` (source: Subject_21_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.03 dB, spectral concentration=0.065, ACF regularity=0.168 (peak 0.234 @ 72.0 BPM)
- legacy detector: 708 peaks, IBI CV=0.274, implied BPM=71.0; FFT BPM=132.0
- posterior detector: 814 peaks, IBI CV=0.293; regularity legacy=67.2% posterior=15.9%
- motion proxy: frame-diff mean=0.1261 p95=0.4485; low-frequency/cardiac power ratio=10.482; exposure drift=n/a; brightness mean=95.6 std=5.7; saturated=0.000; flat=0.000
- ground truth: 766 true beats, 708 detected, matched=325, missed=441, false=383, sensitivity=0.424, precision=0.459, mean |interval error|=0.0749 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 17983 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -1.03 |
| spectral_concentration | 0.0649 |
| n_peaks_legacy | 708 |
| n_peaks_posterior | 814 |
| regularity_legacy_pct | 67.2 |
| regularity_posterior_pct | 15.9 |
| sqi_legacy | 38.7 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 95.59 |
| brightness_std | 5.69 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1261 |
| frame_diff_p95 | 0.4485 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 707, 'mean_ibi_s': 0.84559, 'std_ibi_s': 0.23129, 'median_ibi_s': 0.8, 'cv': 0.27352, 'rmssd_ms': 329.2, 'pnn50_pct': 88.53, 'min_ibi_s': 0.5, 'max_ibi_s': 1.93333, 'implied_bpm': 70.96}
- posterior detector IBI: {'n_intervals': 813, 'mean_ibi_s': 0.73534, 'std_ibi_s': 0.21525, 'median_ibi_s': 0.73333, 'cv': 0.29271, 'rmssd_ms': 298.9, 'pnn50_pct': 87.44, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 81.59}

- autocorrelation: {'acf_peak_value': 0.234, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1681}

## ROI: `cheek_left` (source: Subject_21_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=1.11 dB, spectral concentration=0.098, ACF regularity=0.000 (peak 0.141 @ 72.0 BPM)
- legacy detector: 712 peaks, IBI CV=0.285, implied BPM=71.3; FFT BPM=120.0
- posterior detector: 822 peaks, IBI CV=0.307; regularity legacy=65.8% posterior=1.4%
- motion proxy: frame-diff mean=0.1844 p95=1.2744; low-frequency/cardiac power ratio=7.384; exposure drift=n/a; brightness mean=72.5 std=4.8; saturated=0.000; flat=0.000
- ground truth: 766 true beats, 712 detected, matched=320, missed=446, false=392, sensitivity=0.418, precision=0.449, mean |interval error|=0.0745 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 17983 |
| method | pos |
| bpm_fft | 120.0 |
| snr_db | 1.11 |
| spectral_concentration | 0.0979 |
| n_peaks_legacy | 712 |
| n_peaks_posterior | 822 |
| regularity_legacy_pct | 65.8 |
| regularity_posterior_pct | 1.4 |
| sqi_legacy | 43.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 72.5 |
| brightness_std | 4.78 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1844 |
| frame_diff_p95 | 1.2744 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 711, 'mean_ibi_s': 0.84177, 'std_ibi_s': 0.23963, 'median_ibi_s': 0.8, 'cv': 0.28467, 'rmssd_ms': 342.33, 'pnn50_pct': 86.62, 'min_ibi_s': 0.5, 'max_ibi_s': 1.86667, 'implied_bpm': 71.28}
- posterior detector IBI: {'n_intervals': 821, 'mean_ibi_s': 0.72899, 'std_ibi_s': 0.22407, 'median_ibi_s': 0.7, 'cv': 0.30737, 'rmssd_ms': 311.49, 'pnn50_pct': 85.37, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.66667, 'implied_bpm': 82.31}

- autocorrelation: {'acf_peak_value': 0.1412, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0}

## ROI: `cheek_right` (source: Subject_21_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.05 dB, spectral concentration=0.079, ACF regularity=0.055 (peak 0.178 @ 72.0 BPM)
- legacy detector: 701 peaks, IBI CV=0.285, implied BPM=70.2; FFT BPM=120.0
- posterior detector: 811 peaks, IBI CV=0.300; regularity legacy=65.8% posterior=7.1%
- motion proxy: frame-diff mean=0.1752 p95=1.0886; low-frequency/cardiac power ratio=4.777; exposure drift=n/a; brightness mean=68.7 std=4.4; saturated=0.000; flat=0.000
- ground truth: 766 true beats, 701 detected, matched=323, missed=443, false=378, sensitivity=0.422, precision=0.461, mean |interval error|=0.0706 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 17983 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.05 |
| spectral_concentration | 0.0785 |
| n_peaks_legacy | 701 |
| n_peaks_posterior | 811 |
| regularity_legacy_pct | 65.8 |
| regularity_posterior_pct | 7.1 |
| sqi_legacy | 42.5 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 68.73 |
| brightness_std | 4.43 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1752 |
| frame_diff_p95 | 1.0886 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 700, 'mean_ibi_s': 0.85443, 'std_ibi_s': 0.24371, 'median_ibi_s': 0.8, 'cv': 0.28523, 'rmssd_ms': 330.81, 'pnn50_pct': 86.12, 'min_ibi_s': 0.5, 'max_ibi_s': 1.76667, 'implied_bpm': 70.22}
- posterior detector IBI: {'n_intervals': 810, 'mean_ibi_s': 0.73897, 'std_ibi_s': 0.22155, 'median_ibi_s': 0.7, 'cv': 0.29981, 'rmssd_ms': 305.26, 'pnn50_pct': 85.29, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.6, 'implied_bpm': 81.19}

- autocorrelation: {'acf_peak_value': 0.1775, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.055}

## Notes

- Subject 21 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_21_ECG.npy - 766 R-peaks, mean HR 76.5 BPM, SDNN 95.1 ms, ECG inter-beat CV 0.121.
- Detector IBI CV across ROIs: 0.274-0.285 (ECG inter-beat CV 0.121). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 120.0, 132.0]; detector beat-implied BPM: [71.0, 71.3, 70.2]; ECG mean HR 76.5 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
