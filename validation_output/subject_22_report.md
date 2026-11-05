# Phase 9.0 — Signal validation: Subject 22

## ROI: `forehead` (source: Subject_22_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.05 dB, spectral concentration=0.084, ACF regularity=0.051 (peak 0.175 @ 72.0 BPM)
- legacy detector: 703 peaks, IBI CV=0.279, implied BPM=70.2; FFT BPM=120.0
- posterior detector: 814 peaks, IBI CV=0.314; regularity legacy=66.6% posterior=6.5%
- motion proxy: frame-diff mean=0.1791 p95=0.5584; low-frequency/cardiac power ratio=4.801; exposure drift=n/a; brightness mean=98.1 std=3.0; saturated=0.000; flat=0.000
- ground truth: 1026 true beats, 703 detected, matched=402, missed=624, false=301, sensitivity=0.392, precision=0.572, mean |interval error|=0.0726 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | pos |
| bpm_fft | 120.0 |
| snr_db | 0.05 |
| spectral_concentration | 0.0839 |
| n_peaks_legacy | 703 |
| n_peaks_posterior | 814 |
| regularity_legacy_pct | 66.6 |
| regularity_posterior_pct | 6.5 |
| sqi_legacy | 42.8 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 98.12 |
| brightness_std | 3.04 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1791 |
| frame_diff_p95 | 0.5584 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 702, 'mean_ibi_s': 0.85423, 'std_ibi_s': 0.23796, 'median_ibi_s': 0.8, 'cv': 0.27856, 'rmssd_ms': 334.35, 'pnn50_pct': 86.73, 'min_ibi_s': 0.5, 'max_ibi_s': 1.66667, 'implied_bpm': 70.24}
- posterior detector IBI: {'n_intervals': 813, 'mean_ibi_s': 0.7376, 'std_ibi_s': 0.23196, 'median_ibi_s': 0.73333, 'cv': 0.31449, 'rmssd_ms': 321.4, 'pnn50_pct': 84.11, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.66667, 'implied_bpm': 81.35}

- autocorrelation: {'acf_peak_value': 0.1754, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 2, 'acf_regularity': 0.0508}

## ROI: `cheek_left` (source: Subject_22_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.01 dB, spectral concentration=0.083, ACF regularity=0.000 (peak 0.145 @ 75.0 BPM)
- legacy detector: 707 peaks, IBI CV=0.293, implied BPM=70.7; FFT BPM=120.0
- posterior detector: 819 peaks, IBI CV=0.307; regularity legacy=64.8% posterior=2.7%
- motion proxy: frame-diff mean=0.2002 p95=0.9239; low-frequency/cardiac power ratio=6.621; exposure drift=n/a; brightness mean=84.6 std=3.4; saturated=0.000; flat=0.000
- ground truth: 1026 true beats, 707 detected, matched=393, missed=633, false=314, sensitivity=0.383, precision=0.556, mean |interval error|=0.0749 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.01 |
| spectral_concentration | 0.0828 |
| n_peaks_legacy | 707 |
| n_peaks_posterior | 819 |
| regularity_legacy_pct | 64.8 |
| regularity_posterior_pct | 2.7 |
| sqi_legacy | 43.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 84.62 |
| brightness_std | 3.45 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2002 |
| frame_diff_p95 | 0.9239 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 706, 'mean_ibi_s': 0.84863, 'std_ibi_s': 0.24901, 'median_ibi_s': 0.8, 'cv': 0.29342, 'rmssd_ms': 347.48, 'pnn50_pct': 86.38, 'min_ibi_s': 0.5, 'max_ibi_s': 2.1, 'implied_bpm': 70.7}
- posterior detector IBI: {'n_intervals': 818, 'mean_ibi_s': 0.73244, 'std_ibi_s': 0.22508, 'median_ibi_s': 0.7, 'cv': 0.30731, 'rmssd_ms': 309.07, 'pnn50_pct': 85.92, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.63333, 'implied_bpm': 81.92}

- autocorrelation: {'acf_peak_value': 0.1451, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 2, 'acf_regularity': 0.0}

## ROI: `cheek_right` (source: Subject_22_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=1.55 dB, spectral concentration=0.111, ACF regularity=0.058 (peak 0.179 @ 75.0 BPM)
- legacy detector: 710 peaks, IBI CV=0.287, implied BPM=71.0; FFT BPM=108.0
- posterior detector: 828 peaks, IBI CV=0.306; regularity legacy=65.5% posterior=7.3%
- motion proxy: frame-diff mean=0.1848 p95=0.8848; low-frequency/cardiac power ratio=10.311; exposure drift=n/a; brightness mean=69.8 std=3.0; saturated=0.000; flat=0.000
- ground truth: 1026 true beats, 710 detected, matched=408, missed=618, false=302, sensitivity=0.398, precision=0.575, mean |interval error|=0.0750 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | pos |
| bpm_fft | 108.0 |
| snr_db | 1.55 |
| spectral_concentration | 0.1111 |
| n_peaks_legacy | 710 |
| n_peaks_posterior | 828 |
| regularity_legacy_pct | 65.5 |
| regularity_posterior_pct | 7.3 |
| sqi_legacy | 78.6 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 69.79 |
| brightness_std | 2.99 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1848 |
| frame_diff_p95 | 0.8848 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 709, 'mean_ibi_s': 0.84565, 'std_ibi_s': 0.24295, 'median_ibi_s': 0.8, 'cv': 0.28729, 'rmssd_ms': 339.8, 'pnn50_pct': 85.73, 'min_ibi_s': 0.5, 'max_ibi_s': 1.76667, 'implied_bpm': 70.95}
- posterior detector IBI: {'n_intervals': 827, 'mean_ibi_s': 0.72499, 'std_ibi_s': 0.22208, 'median_ibi_s': 0.7, 'cv': 0.30632, 'rmssd_ms': 313.82, 'pnn50_pct': 84.62, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.7, 'implied_bpm': 82.76}

- autocorrelation: {'acf_peak_value': 0.1791, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0582}

## Notes

- Subject 22 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_22_ECG.npy - 1026 R-peaks, mean HR 102.6 BPM, SDNN 74.4 ms, ECG inter-beat CV 0.127.
- Detector IBI CV across ROIs: 0.279-0.293 (ECG inter-beat CV 0.127). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [108.0, 120.0, 120.0]; detector beat-implied BPM: [70.2, 70.7, 71.0]; ECG mean HR 102.6 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
