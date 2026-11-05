# Phase 9.0 — Signal validation: Subject 16

## ROI: `forehead` (source: Subject_16_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.12 dB, spectral concentration=0.065, ACF regularity=0.167 (peak 0.233 @ 66.7 BPM)
- legacy detector: 688 peaks, IBI CV=0.276, implied BPM=68.8; FFT BPM=132.0
- posterior detector: 798 peaks, IBI CV=0.311; regularity legacy=66.8% posterior=14.7%
- motion proxy: frame-diff mean=0.1689 p95=0.5168; low-frequency/cardiac power ratio=26.241; exposure drift=n/a; brightness mean=89.9 std=7.2; saturated=0.000; flat=0.000
- ground truth: 679 true beats, 688 detected, matched=331, missed=348, false=357, sensitivity=0.487, precision=0.481, mean |interval error|=0.0737 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -1.12 |
| spectral_concentration | 0.0652 |
| n_peaks_legacy | 688 |
| n_peaks_posterior | 798 |
| regularity_legacy_pct | 66.8 |
| regularity_posterior_pct | 14.7 |
| sqi_legacy | 37.8 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 89.91 |
| brightness_std | 7.17 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1689 |
| frame_diff_p95 | 0.5168 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 687, 'mean_ibi_s': 0.87186, 'std_ibi_s': 0.24104, 'median_ibi_s': 0.83333, 'cv': 0.27646, 'rmssd_ms': 336.05, 'pnn50_pct': 87.03, 'min_ibi_s': 0.5, 'max_ibi_s': 1.83333, 'implied_bpm': 68.82}
- posterior detector IBI: {'n_intervals': 797, 'mean_ibi_s': 0.75153, 'std_ibi_s': 0.23339, 'median_ibi_s': 0.73333, 'cv': 0.31056, 'rmssd_ms': 321.16, 'pnn50_pct': 87.06, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 79.84}

- autocorrelation: {'acf_peak_value': 0.2333, 'acf_peak_lag_s': 0.9, 'acf_peak_bpm': 66.67, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1666}

## ROI: `cheek_left` (source: Subject_16_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.11 dB, spectral concentration=0.065, ACF regularity=0.127 (peak 0.214 @ 72.0 BPM)
- legacy detector: 701 peaks, IBI CV=0.274, implied BPM=70.1; FFT BPM=132.0
- posterior detector: 811 peaks, IBI CV=0.296; regularity legacy=67.2% posterior=12.8%
- motion proxy: frame-diff mean=0.2151 p95=0.9022; low-frequency/cardiac power ratio=17.809; exposure drift=n/a; brightness mean=70.9 std=5.6; saturated=0.000; flat=0.000
- ground truth: 679 true beats, 701 detected, matched=326, missed=353, false=375, sensitivity=0.480, precision=0.465, mean |interval error|=0.0724 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -1.11 |
| spectral_concentration | 0.0653 |
| n_peaks_legacy | 701 |
| n_peaks_posterior | 811 |
| regularity_legacy_pct | 67.2 |
| regularity_posterior_pct | 12.8 |
| sqi_legacy | 38.2 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 70.9 |
| brightness_std | 5.63 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2151 |
| frame_diff_p95 | 0.9022 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 700, 'mean_ibi_s': 0.85624, 'std_ibi_s': 0.2343, 'median_ibi_s': 0.83333, 'cv': 0.27364, 'rmssd_ms': 335.34, 'pnn50_pct': 88.41, 'min_ibi_s': 0.5, 'max_ibi_s': 1.73333, 'implied_bpm': 70.07}
- posterior detector IBI: {'n_intervals': 810, 'mean_ibi_s': 0.73996, 'std_ibi_s': 0.21874, 'median_ibi_s': 0.73333, 'cv': 0.29561, 'rmssd_ms': 301.65, 'pnn50_pct': 87.52, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 81.09}

- autocorrelation: {'acf_peak_value': 0.2136, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1272}

## ROI: `cheek_right` (source: Subject_16_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.63 dB, spectral concentration=0.058, ACF regularity=0.160 (peak 0.230 @ 69.2 BPM)
- legacy detector: 702 peaks, IBI CV=0.277, implied BPM=70.2; FFT BPM=132.0
- posterior detector: 793 peaks, IBI CV=0.307; regularity legacy=66.8% posterior=14.3%
- motion proxy: frame-diff mean=0.1847 p95=0.8941; low-frequency/cardiac power ratio=23.338; exposure drift=n/a; brightness mean=79.1 std=7.9; saturated=0.000; flat=0.000
- ground truth: 679 true beats, 702 detected, matched=330, missed=349, false=372, sensitivity=0.486, precision=0.470, mean |interval error|=0.0782 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -1.63 |
| spectral_concentration | 0.0577 |
| n_peaks_legacy | 702 |
| n_peaks_posterior | 793 |
| regularity_legacy_pct | 66.8 |
| regularity_posterior_pct | 14.3 |
| sqi_legacy | 38.3 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 79.06 |
| brightness_std | 7.91 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1847 |
| frame_diff_p95 | 0.8941 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 701, 'mean_ibi_s': 0.85516, 'std_ibi_s': 0.23655, 'median_ibi_s': 0.8, 'cv': 0.27661, 'rmssd_ms': 325.6, 'pnn50_pct': 88.0, 'min_ibi_s': 0.5, 'max_ibi_s': 1.63333, 'implied_bpm': 70.16}
- posterior detector IBI: {'n_intervals': 792, 'mean_ibi_s': 0.7569, 'std_ibi_s': 0.23219, 'median_ibi_s': 0.73333, 'cv': 0.30677, 'rmssd_ms': 323.89, 'pnn50_pct': 87.74, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.6, 'implied_bpm': 79.27}

- autocorrelation: {'acf_peak_value': 0.2299, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1597}

## Notes

- Subject 16 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_16_ECG.npy - 679 R-peaks, mean HR 68.0 BPM, SDNN 53.1 ms, ECG inter-beat CV 0.060.
- Detector IBI CV across ROIs: 0.274-0.277 (ECG inter-beat CV 0.060). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [132.0, 132.0, 132.0]; detector beat-implied BPM: [68.8, 70.1, 70.2]; ECG mean HR 68.0 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
