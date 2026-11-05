# Phase 9.0 — Signal validation: Subject 2

## ROI: `forehead` (source: Subject_2_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=3.15 dB, spectral concentration=0.155, ACF regularity=0.032 (peak 0.166 @ 75.0 BPM)
- legacy detector: 712 peaks, IBI CV=0.279, implied BPM=71.2; FFT BPM=84.0
- posterior detector: 819 peaks, IBI CV=0.291; regularity legacy=66.6% posterior=7.1%
- motion proxy: frame-diff mean=0.1764 p95=0.6011; low-frequency/cardiac power ratio=8.666; exposure drift=n/a; brightness mean=95.1 std=3.3; saturated=0.000; flat=0.000
- ground truth: 939 true beats, 712 detected, matched=410, missed=529, false=302, sensitivity=0.437, precision=0.576, mean |interval error|=0.0742 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 84.0 |
| snr_db | 3.15 |
| spectral_concentration | 0.1553 |
| n_peaks_legacy | 712 |
| n_peaks_posterior | 819 |
| regularity_legacy_pct | 66.6 |
| regularity_posterior_pct | 7.1 |
| sqi_legacy | 78.5 |
| sqi_posterior | 0.1 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 95.07 |
| brightness_std | 3.27 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1764 |
| frame_diff_p95 | 0.6011 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 711, 'mean_ibi_s': 0.84285, 'std_ibi_s': 0.23482, 'median_ibi_s': 0.8, 'cv': 0.2786, 'rmssd_ms': 316.79, 'pnn50_pct': 87.04, 'min_ibi_s': 0.5, 'max_ibi_s': 1.73333, 'implied_bpm': 71.19}
- posterior detector IBI: {'n_intervals': 818, 'mean_ibi_s': 0.7326, 'std_ibi_s': 0.21336, 'median_ibi_s': 0.7, 'cv': 0.29124, 'rmssd_ms': 289.0, 'pnn50_pct': 84.94, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 81.9}

- autocorrelation: {'acf_peak_value': 0.1658, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0316}

## ROI: `cheek_left` (source: Subject_2_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=4.28 dB, spectral concentration=0.193, ACF regularity=0.075 (peak 0.187 @ 75.0 BPM)
- legacy detector: 725 peaks, IBI CV=0.275, implied BPM=72.5; FFT BPM=78.0
- posterior detector: 834 peaks, IBI CV=0.294; regularity legacy=67.0% posterior=9.1%
- motion proxy: frame-diff mean=0.0854 p95=0.2461; low-frequency/cardiac power ratio=14.329; exposure drift=n/a; brightness mean=94.7 std=3.3; saturated=0.000; flat=0.000
- ground truth: 939 true beats, 725 detected, matched=405, missed=534, false=320, sensitivity=0.431, precision=0.559, mean |interval error|=0.0745 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 78.0 |
| snr_db | 4.28 |
| spectral_concentration | 0.1932 |
| n_peaks_legacy | 725 |
| n_peaks_posterior | 834 |
| regularity_legacy_pct | 67.0 |
| regularity_posterior_pct | 9.1 |
| sqi_legacy | 79.1 |
| sqi_posterior | 0.1 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 94.75 |
| brightness_std | 3.32 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.0854 |
| frame_diff_p95 | 0.2461 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 724, 'mean_ibi_s': 0.82785, 'std_ibi_s': 0.2274, 'median_ibi_s': 0.76667, 'cv': 0.27468, 'rmssd_ms': 316.78, 'pnn50_pct': 85.34, 'min_ibi_s': 0.5, 'max_ibi_s': 1.73333, 'implied_bpm': 72.48}
- posterior detector IBI: {'n_intervals': 833, 'mean_ibi_s': 0.71953, 'std_ibi_s': 0.21186, 'median_ibi_s': 0.7, 'cv': 0.29444, 'rmssd_ms': 294.43, 'pnn50_pct': 83.53, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.76667, 'implied_bpm': 83.39}

- autocorrelation: {'acf_peak_value': 0.1874, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0748}

## ROI: `cheek_right` (source: Subject_2_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.82 dB, spectral concentration=0.091, ACF regularity=0.000 (peak 0.146 @ 75.0 BPM)
- legacy detector: 713 peaks, IBI CV=0.292, implied BPM=71.3; FFT BPM=120.0
- posterior detector: 818 peaks, IBI CV=0.306; regularity legacy=64.9% posterior=2.7%
- motion proxy: frame-diff mean=0.1423 p95=0.6156; low-frequency/cardiac power ratio=9.340; exposure drift=n/a; brightness mean=98.7 std=3.7; saturated=0.000; flat=0.000
- ground truth: 939 true beats, 713 detected, matched=387, missed=552, false=326, sensitivity=0.412, precision=0.543, mean |interval error|=0.0752 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.82 |
| spectral_concentration | 0.0912 |
| n_peaks_legacy | 713 |
| n_peaks_posterior | 818 |
| regularity_legacy_pct | 64.9 |
| regularity_posterior_pct | 2.7 |
| sqi_legacy | 43.4 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 98.74 |
| brightness_std | 3.69 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1423 |
| frame_diff_p95 | 0.6156 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 712, 'mean_ibi_s': 0.84106, 'std_ibi_s': 0.24594, 'median_ibi_s': 0.8, 'cv': 0.29242, 'rmssd_ms': 348.87, 'pnn50_pct': 86.78, 'min_ibi_s': 0.5, 'max_ibi_s': 1.76667, 'implied_bpm': 71.34}
- posterior detector IBI: {'n_intervals': 817, 'mean_ibi_s': 0.73297, 'std_ibi_s': 0.22452, 'median_ibi_s': 0.7, 'cv': 0.30632, 'rmssd_ms': 301.4, 'pnn50_pct': 85.17, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.6, 'implied_bpm': 81.86}

- autocorrelation: {'acf_peak_value': 0.1462, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0}

## Notes

- Subject 2 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_2_ECG.npy - 939 R-peaks, mean HR 94.3 BPM, SDNN 38.1 ms, ECG inter-beat CV 0.060.
- Detector IBI CV across ROIs: 0.275-0.292 (ECG inter-beat CV 0.060). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [78.0, 84.00000000000001, 120.0]; detector beat-implied BPM: [71.2, 72.5, 71.3]; ECG mean HR 94.3 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
