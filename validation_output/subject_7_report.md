# Phase 9.0 — Signal validation: Subject 7

## ROI: `forehead` (source: Subject_7_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.36 dB, spectral concentration=0.080, ACF regularity=0.059 (peak 0.179 @ 72.0 BPM)
- legacy detector: 700 peaks, IBI CV=0.270, implied BPM=70.0; FFT BPM=132.0
- posterior detector: 799 peaks, IBI CV=0.309; regularity legacy=67.6% posterior=7.2%
- motion proxy: frame-diff mean=0.1628 p95=0.5845; low-frequency/cardiac power ratio=1.163; exposure drift=n/a; brightness mean=102.8 std=0.8; saturated=0.000; flat=0.000
- ground truth: 687 true beats, 700 detected, matched=297, missed=390, false=403, sensitivity=0.432, precision=0.424, mean |interval error|=0.0773 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.36 |
| spectral_concentration | 0.0803 |
| n_peaks_legacy | 700 |
| n_peaks_posterior | 799 |
| regularity_legacy_pct | 67.6 |
| regularity_posterior_pct | 7.2 |
| sqi_legacy | 38.9 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 102.8 |
| brightness_std | 0.84 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1628 |
| frame_diff_p95 | 0.5845 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 699, 'mean_ibi_s': 0.85722, 'std_ibi_s': 0.23181, 'median_ibi_s': 0.83333, 'cv': 0.27041, 'rmssd_ms': 322.59, 'pnn50_pct': 86.96, 'min_ibi_s': 0.5, 'max_ibi_s': 1.56667, 'implied_bpm': 69.99}
- posterior detector IBI: {'n_intervals': 798, 'mean_ibi_s': 0.75088, 'std_ibi_s': 0.23203, 'median_ibi_s': 0.73333, 'cv': 0.30901, 'rmssd_ms': 315.37, 'pnn50_pct': 86.32, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.96667, 'implied_bpm': 79.91}

- autocorrelation: {'acf_peak_value': 0.1793, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0587}

## ROI: `cheek_left` (source: Subject_7_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.09 dB, spectral concentration=0.078, ACF regularity=0.091 (peak 0.195 @ 72.0 BPM)
- legacy detector: 710 peaks, IBI CV=0.278, implied BPM=71.0; FFT BPM=120.0
- posterior detector: 812 peaks, IBI CV=0.297; regularity legacy=66.6% posterior=9.9%
- motion proxy: frame-diff mean=0.2091 p95=1.1610; low-frequency/cardiac power ratio=0.876; exposure drift=n/a; brightness mean=95.8 std=0.7; saturated=0.000; flat=0.000
- ground truth: 687 true beats, 710 detected, matched=285, missed=402, false=425, sensitivity=0.415, precision=0.401, mean |interval error|=0.0760 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.09 |
| spectral_concentration | 0.0783 |
| n_peaks_legacy | 710 |
| n_peaks_posterior | 812 |
| regularity_legacy_pct | 66.6 |
| regularity_posterior_pct | 9.9 |
| sqi_legacy | 42.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 95.79 |
| brightness_std | 0.72 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2091 |
| frame_diff_p95 | 1.161 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 709, 'mean_ibi_s': 0.84518, 'std_ibi_s': 0.23506, 'median_ibi_s': 0.8, 'cv': 0.27812, 'rmssd_ms': 318.51, 'pnn50_pct': 87.43, 'min_ibi_s': 0.5, 'max_ibi_s': 1.9, 'implied_bpm': 70.99}
- posterior detector IBI: {'n_intervals': 811, 'mean_ibi_s': 0.73888, 'std_ibi_s': 0.21976, 'median_ibi_s': 0.73333, 'cv': 0.29742, 'rmssd_ms': 289.82, 'pnn50_pct': 85.93, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.6, 'implied_bpm': 81.2}

- autocorrelation: {'acf_peak_value': 0.1953, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0907}

## ROI: `cheek_right` (source: Subject_7_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.01 dB, spectral concentration=0.083, ACF regularity=0.047 (peak 0.173 @ 72.0 BPM)
- legacy detector: 700 peaks, IBI CV=0.293, implied BPM=70.0; FFT BPM=120.0
- posterior detector: 817 peaks, IBI CV=0.304; regularity legacy=64.8% posterior=6.0%
- motion proxy: frame-diff mean=0.0959 p95=0.3667; low-frequency/cardiac power ratio=1.521; exposure drift=n/a; brightness mean=93.2 std=0.7; saturated=0.000; flat=0.000
- ground truth: 687 true beats, 700 detected, matched=281, missed=406, false=419, sensitivity=0.409, precision=0.401, mean |interval error|=0.0752 s
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
| spectral_concentration | 0.0832 |
| n_peaks_legacy | 700 |
| n_peaks_posterior | 817 |
| regularity_legacy_pct | 64.8 |
| regularity_posterior_pct | 6.0 |
| sqi_legacy | 42.3 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 93.19 |
| brightness_std | 0.65 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.0959 |
| frame_diff_p95 | 0.3667 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 699, 'mean_ibi_s': 0.85675, 'std_ibi_s': 0.25134, 'median_ibi_s': 0.8, 'cv': 0.29337, 'rmssd_ms': 358.76, 'pnn50_pct': 86.1, 'min_ibi_s': 0.5, 'max_ibi_s': 2.03333, 'implied_bpm': 70.03}
- posterior detector IBI: {'n_intervals': 816, 'mean_ibi_s': 0.73444, 'std_ibi_s': 0.22333, 'median_ibi_s': 0.7, 'cv': 0.30409, 'rmssd_ms': 313.78, 'pnn50_pct': 84.05, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.76667, 'implied_bpm': 81.7}

- autocorrelation: {'acf_peak_value': 0.1733, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 2, 'acf_regularity': 0.0466}

## Notes

- Subject 7 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_7_ECG.npy - 687 R-peaks, mean HR 68.7 BPM, SDNN 53.9 ms, ECG inter-beat CV 0.062.
- Detector IBI CV across ROIs: 0.270-0.293 (ECG inter-beat CV 0.062). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 120.0, 132.0]; detector beat-implied BPM: [70.0, 71.0, 70.0]; ECG mean HR 68.7 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
