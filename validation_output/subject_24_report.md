# Phase 9.0 — Signal validation: Subject 24

## ROI: `forehead` (source: Subject_24_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.34 dB, spectral concentration=0.086, ACF regularity=0.077 (peak 0.189 @ 69.2 BPM)
- legacy detector: 719 peaks, IBI CV=0.270, implied BPM=72.0; FFT BPM=120.0
- posterior detector: 822 peaks, IBI CV=0.301; regularity legacy=67.6% posterior=8.0%
- motion proxy: frame-diff mean=0.1187 p95=0.3411; low-frequency/cardiac power ratio=9.547; exposure drift=n/a; brightness mean=90.7 std=1.9; saturated=0.000; flat=0.000
- ground truth: 847 true beats, 719 detected, matched=351, missed=496, false=368, sensitivity=0.414, precision=0.488, mean |interval error|=0.0750 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.34 |
| spectral_concentration | 0.0861 |
| n_peaks_legacy | 719 |
| n_peaks_posterior | 822 |
| regularity_legacy_pct | 67.6 |
| regularity_posterior_pct | 8.0 |
| sqi_legacy | 43.4 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 90.66 |
| brightness_std | 1.94 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1187 |
| frame_diff_p95 | 0.3411 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 718, 'mean_ibi_s': 0.8338, 'std_ibi_s': 0.22528, 'median_ibi_s': 0.8, 'cv': 0.27019, 'rmssd_ms': 322.94, 'pnn50_pct': 87.87, 'min_ibi_s': 0.5, 'max_ibi_s': 1.66667, 'implied_bpm': 71.96}
- posterior detector IBI: {'n_intervals': 821, 'mean_ibi_s': 0.72919, 'std_ibi_s': 0.2193, 'median_ibi_s': 0.7, 'cv': 0.30074, 'rmssd_ms': 304.92, 'pnn50_pct': 85.12, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.36667, 'implied_bpm': 82.28}

- autocorrelation: {'acf_peak_value': 0.1885, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0771}

## ROI: `cheek_left` (source: Subject_24_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.13 dB, spectral concentration=0.085, ACF regularity=0.003 (peak 0.151 @ 72.0 BPM)
- legacy detector: 692 peaks, IBI CV=0.283, implied BPM=69.3; FFT BPM=120.0
- posterior detector: 813 peaks, IBI CV=0.297; regularity legacy=66.0% posterior=3.2%
- motion proxy: frame-diff mean=0.1637 p95=0.8914; low-frequency/cardiac power ratio=3.321; exposure drift=n/a; brightness mean=61.7 std=2.1; saturated=0.000; flat=0.000
- ground truth: 847 true beats, 692 detected, matched=333, missed=514, false=359, sensitivity=0.393, precision=0.481, mean |interval error|=0.0766 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | chrom |
| bpm_fft | 120.0 |
| snr_db | 0.13 |
| spectral_concentration | 0.0853 |
| n_peaks_legacy | 692 |
| n_peaks_posterior | 813 |
| regularity_legacy_pct | 66.0 |
| regularity_posterior_pct | 3.2 |
| sqi_legacy | 42.9 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 61.75 |
| brightness_std | 2.08 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1637 |
| frame_diff_p95 | 0.8914 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 691, 'mean_ibi_s': 0.86633, 'std_ibi_s': 0.2451, 'median_ibi_s': 0.83333, 'cv': 0.28292, 'rmssd_ms': 342.86, 'pnn50_pct': 88.12, 'min_ibi_s': 0.5, 'max_ibi_s': 1.9, 'implied_bpm': 69.26}
- posterior detector IBI: {'n_intervals': 812, 'mean_ibi_s': 0.73846, 'std_ibi_s': 0.21951, 'median_ibi_s': 0.73333, 'cv': 0.29725, 'rmssd_ms': 316.57, 'pnn50_pct': 87.79, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.43333, 'implied_bpm': 81.25}

- autocorrelation: {'acf_peak_value': 0.1513, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0026}

## ROI: `cheek_right` (source: Subject_24_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.37 dB, spectral concentration=0.073, ACF regularity=0.023 (peak 0.162 @ 72.0 BPM)
- legacy detector: 710 peaks, IBI CV=0.273, implied BPM=71.0; FFT BPM=132.0
- posterior detector: 829 peaks, IBI CV=0.300; regularity legacy=67.2% posterior=4.4%
- motion proxy: frame-diff mean=0.2269 p95=1.1492; low-frequency/cardiac power ratio=2.878; exposure drift=n/a; brightness mean=68.0 std=2.3; saturated=0.000; flat=0.000
- ground truth: 847 true beats, 710 detected, matched=338, missed=509, false=372, sensitivity=0.399, precision=0.476, mean |interval error|=0.0725 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.37 |
| spectral_concentration | 0.0727 |
| n_peaks_legacy | 710 |
| n_peaks_posterior | 829 |
| regularity_legacy_pct | 67.2 |
| regularity_posterior_pct | 4.4 |
| sqi_legacy | 38.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 67.97 |
| brightness_std | 2.26 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2269 |
| frame_diff_p95 | 1.1492 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 709, 'mean_ibi_s': 0.84546, 'std_ibi_s': 0.23112, 'median_ibi_s': 0.8, 'cv': 0.27336, 'rmssd_ms': 321.49, 'pnn50_pct': 87.71, 'min_ibi_s': 0.5, 'max_ibi_s': 1.7, 'implied_bpm': 70.97}
- posterior detector IBI: {'n_intervals': 828, 'mean_ibi_s': 0.72395, 'std_ibi_s': 0.21742, 'median_ibi_s': 0.7, 'cv': 0.30033, 'rmssd_ms': 291.25, 'pnn50_pct': 85.01, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.46667, 'implied_bpm': 82.88}

- autocorrelation: {'acf_peak_value': 0.1616, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0232}

## Notes

- Subject 24 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_24_ECG.npy - 847 R-peaks, mean HR 84.7 BPM, SDNN 63.5 ms, ECG inter-beat CV 0.090.
- Detector IBI CV across ROIs: 0.270-0.283 (ECG inter-beat CV 0.090). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 120.0, 132.0]; detector beat-implied BPM: [72.0, 69.3, 71.0]; ECG mean HR 84.7 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
