# Phase 9.0 — Signal validation: Subject 18

## ROI: `forehead` (source: Subject_18_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=1.94 dB, spectral concentration=0.107, ACF regularity=0.046 (peak 0.173 @ 72.0 BPM)
- legacy detector: 701 peaks, IBI CV=0.291, implied BPM=70.1; FFT BPM=108.0
- posterior detector: 804 peaks, IBI CV=0.309; regularity legacy=65.1% posterior=7.3%
- motion proxy: frame-diff mean=0.3464 p95=1.4495; low-frequency/cardiac power ratio=13.521; exposure drift=n/a; brightness mean=118.0 std=6.0; saturated=0.000; flat=0.000
- ground truth: 850 true beats, 701 detected, matched=380, missed=470, false=321, sensitivity=0.447, precision=0.542, mean |interval error|=0.0711 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 108.0 |
| snr_db | 1.94 |
| spectral_concentration | 0.1072 |
| n_peaks_legacy | 701 |
| n_peaks_posterior | 804 |
| regularity_legacy_pct | 65.1 |
| regularity_posterior_pct | 7.3 |
| sqi_legacy | 76.8 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 118.02 |
| brightness_std | 6.01 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.3464 |
| frame_diff_p95 | 1.4495 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 700, 'mean_ibi_s': 0.8559, 'std_ibi_s': 0.24906, 'median_ibi_s': 0.8, 'cv': 0.29099, 'rmssd_ms': 348.43, 'pnn50_pct': 86.41, 'min_ibi_s': 0.5, 'max_ibi_s': 1.73333, 'implied_bpm': 70.1}
- posterior detector IBI: {'n_intervals': 803, 'mean_ibi_s': 0.74666, 'std_ibi_s': 0.23094, 'median_ibi_s': 0.73333, 'cv': 0.3093, 'rmssd_ms': 323.88, 'pnn50_pct': 86.41, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.53333, 'implied_bpm': 80.36}

- autocorrelation: {'acf_peak_value': 0.173, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.046}

## ROI: `cheek_left` (source: Subject_18_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=2.07 dB, spectral concentration=0.121, ACF regularity=0.008 (peak 0.154 @ 72.0 BPM)
- legacy detector: 711 peaks, IBI CV=0.283, implied BPM=71.1; FFT BPM=108.0
- posterior detector: 813 peaks, IBI CV=0.306; regularity legacy=66.0% posterior=3.6%
- motion proxy: frame-diff mean=0.1906 p95=0.9131; low-frequency/cardiac power ratio=16.681; exposure drift=n/a; brightness mean=88.4 std=4.7; saturated=0.000; flat=0.000
- ground truth: 850 true beats, 711 detected, matched=363, missed=487, false=348, sensitivity=0.427, precision=0.511, mean |interval error|=0.0740 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | pos |
| bpm_fft | 108.0 |
| snr_db | 2.07 |
| spectral_concentration | 0.1211 |
| n_peaks_legacy | 711 |
| n_peaks_posterior | 813 |
| regularity_legacy_pct | 66.0 |
| regularity_posterior_pct | 3.6 |
| sqi_legacy | 78.1 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 88.41 |
| brightness_std | 4.67 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1906 |
| frame_diff_p95 | 0.9131 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 710, 'mean_ibi_s': 0.84427, 'std_ibi_s': 0.23888, 'median_ibi_s': 0.8, 'cv': 0.28294, 'rmssd_ms': 335.83, 'pnn50_pct': 89.0, 'min_ibi_s': 0.5, 'max_ibi_s': 1.8, 'implied_bpm': 71.07}
- posterior detector IBI: {'n_intervals': 812, 'mean_ibi_s': 0.73822, 'std_ibi_s': 0.22568, 'median_ibi_s': 0.7, 'cv': 0.30571, 'rmssd_ms': 314.55, 'pnn50_pct': 88.78, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 81.28}

- autocorrelation: {'acf_peak_value': 0.1538, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 2, 'acf_regularity': 0.0077}

## ROI: `cheek_right` (source: Subject_18_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=1.83 dB, spectral concentration=0.108, ACF regularity=0.000 (peak 0.148 @ 72.0 BPM)
- legacy detector: 704 peaks, IBI CV=0.287, implied BPM=70.4; FFT BPM=108.0
- posterior detector: 811 peaks, IBI CV=0.298; regularity legacy=65.5% posterior=3.3%
- motion proxy: frame-diff mean=0.1217 p95=0.4236; low-frequency/cardiac power ratio=28.297; exposure drift=n/a; brightness mean=93.7 std=5.0; saturated=0.000; flat=0.000
- ground truth: 850 true beats, 704 detected, matched=344, missed=506, false=360, sensitivity=0.405, precision=0.489, mean |interval error|=0.0779 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | chrom |
| bpm_fft | 108.0 |
| snr_db | 1.83 |
| spectral_concentration | 0.1084 |
| n_peaks_legacy | 704 |
| n_peaks_posterior | 811 |
| regularity_legacy_pct | 65.5 |
| regularity_posterior_pct | 3.3 |
| sqi_legacy | 77.2 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 93.67 |
| brightness_std | 5.0 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1217 |
| frame_diff_p95 | 0.4236 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 703, 'mean_ibi_s': 0.85216, 'std_ibi_s': 0.24489, 'median_ibi_s': 0.8, 'cv': 0.28737, 'rmssd_ms': 329.3, 'pnn50_pct': 87.18, 'min_ibi_s': 0.5, 'max_ibi_s': 1.96667, 'implied_bpm': 70.41}
- posterior detector IBI: {'n_intervals': 810, 'mean_ibi_s': 0.73959, 'std_ibi_s': 0.22075, 'median_ibi_s': 0.73333, 'cv': 0.29847, 'rmssd_ms': 305.57, 'pnn50_pct': 86.65, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 81.13}

- autocorrelation: {'acf_peak_value': 0.1478, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 2, 'acf_regularity': 0.0}

## Notes

- Subject 18 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_18_ECG.npy - 850 R-peaks, mean HR 85.4 BPM, SDNN 57.2 ms, ECG inter-beat CV 0.081.
- Detector IBI CV across ROIs: 0.283-0.291 (ECG inter-beat CV 0.081). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [108.0, 108.0, 108.0]; detector beat-implied BPM: [70.1, 71.1, 70.4]; ECG mean HR 85.4 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
