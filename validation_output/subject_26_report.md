# Phase 9.0 — Signal validation: Subject 26

## ROI: `forehead` (source: Subject_26_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.94 dB, spectral concentration=0.065, ACF regularity=0.131 (peak 0.215 @ 69.2 BPM)
- legacy detector: 707 peaks, IBI CV=0.266, implied BPM=70.7; FFT BPM=132.0
- posterior detector: 802 peaks, IBI CV=0.289; regularity legacy=68.0% posterior=13.1%
- motion proxy: frame-diff mean=0.1571 p95=0.4761; low-frequency/cardiac power ratio=14.034; exposure drift=n/a; brightness mean=85.0 std=5.4; saturated=0.000; flat=0.000
- ground truth: 667 true beats, 707 detected, matched=311, missed=356, false=396, sensitivity=0.466, precision=0.440, mean |interval error|=0.0725 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.94 |
| spectral_concentration | 0.0651 |
| n_peaks_legacy | 707 |
| n_peaks_posterior | 802 |
| regularity_legacy_pct | 68.0 |
| regularity_posterior_pct | 13.1 |
| sqi_legacy | 38.5 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 85.04 |
| brightness_std | 5.37 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1571 |
| frame_diff_p95 | 0.4761 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 706, 'mean_ibi_s': 0.84854, 'std_ibi_s': 0.22607, 'median_ibi_s': 0.83333, 'cv': 0.26643, 'rmssd_ms': 312.35, 'pnn50_pct': 86.95, 'min_ibi_s': 0.5, 'max_ibi_s': 1.63333, 'implied_bpm': 70.71}
- posterior detector IBI: {'n_intervals': 801, 'mean_ibi_s': 0.7479, 'std_ibi_s': 0.21622, 'median_ibi_s': 0.73333, 'cv': 0.2891, 'rmssd_ms': 296.0, 'pnn50_pct': 86.12, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 80.22}

- autocorrelation: {'acf_peak_value': 0.2154, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1308}

## ROI: `cheek_left` (source: Subject_26_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.52 dB, spectral concentration=0.086, ACF regularity=0.033 (peak 0.166 @ 72.0 BPM)
- legacy detector: 710 peaks, IBI CV=0.274, implied BPM=71.0; FFT BPM=120.0
- posterior detector: 814 peaks, IBI CV=0.294; regularity legacy=67.2% posterior=6.1%
- motion proxy: frame-diff mean=0.1655 p95=0.6101; low-frequency/cardiac power ratio=12.767; exposure drift=n/a; brightness mean=92.7 std=6.4; saturated=0.000; flat=0.000
- ground truth: 667 true beats, 710 detected, matched=261, missed=406, false=449, sensitivity=0.391, precision=0.368, mean |interval error|=0.0736 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.52 |
| spectral_concentration | 0.0859 |
| n_peaks_legacy | 710 |
| n_peaks_posterior | 814 |
| regularity_legacy_pct | 67.2 |
| regularity_posterior_pct | 6.1 |
| sqi_legacy | 41.9 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 92.72 |
| brightness_std | 6.43 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1655 |
| frame_diff_p95 | 0.6101 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 709, 'mean_ibi_s': 0.84504, 'std_ibi_s': 0.2313, 'median_ibi_s': 0.8, 'cv': 0.27372, 'rmssd_ms': 323.35, 'pnn50_pct': 84.6, 'min_ibi_s': 0.5, 'max_ibi_s': 2.1, 'implied_bpm': 71.0}
- posterior detector IBI: {'n_intervals': 813, 'mean_ibi_s': 0.73694, 'std_ibi_s': 0.21654, 'median_ibi_s': 0.73333, 'cv': 0.29384, 'rmssd_ms': 297.43, 'pnn50_pct': 84.73, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.53333, 'implied_bpm': 81.42}

- autocorrelation: {'acf_peak_value': 0.1663, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0326}

## ROI: `cheek_right` (source: Subject_26_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.79 dB, spectral concentration=0.069, ACF regularity=0.054 (peak 0.177 @ 72.0 BPM)
- legacy detector: 711 peaks, IBI CV=0.271, implied BPM=71.1; FFT BPM=132.0
- posterior detector: 813 peaks, IBI CV=0.296; regularity legacy=67.5% posterior=7.1%
- motion proxy: frame-diff mean=0.1380 p95=0.5342; low-frequency/cardiac power ratio=10.017; exposure drift=n/a; brightness mean=83.1 std=4.8; saturated=0.000; flat=0.000
- ground truth: 667 true beats, 711 detected, matched=286, missed=381, false=425, sensitivity=0.429, precision=0.402, mean |interval error|=0.0767 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | chrom |
| bpm_fft | 132.0 |
| snr_db | -0.79 |
| spectral_concentration | 0.0688 |
| n_peaks_legacy | 711 |
| n_peaks_posterior | 813 |
| regularity_legacy_pct | 67.5 |
| regularity_posterior_pct | 7.1 |
| sqi_legacy | 38.5 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 83.14 |
| brightness_std | 4.82 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.138 |
| frame_diff_p95 | 0.5342 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 710, 'mean_ibi_s': 0.84376, 'std_ibi_s': 0.2287, 'median_ibi_s': 0.8, 'cv': 0.27105, 'rmssd_ms': 319.62, 'pnn50_pct': 85.33, 'min_ibi_s': 0.5, 'max_ibi_s': 1.63333, 'implied_bpm': 71.11}
- posterior detector IBI: {'n_intervals': 812, 'mean_ibi_s': 0.73777, 'std_ibi_s': 0.2183, 'median_ibi_s': 0.73333, 'cv': 0.29589, 'rmssd_ms': 301.01, 'pnn50_pct': 87.42, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.53333, 'implied_bpm': 81.33}

- autocorrelation: {'acf_peak_value': 0.1768, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0537}

## Notes

- Subject 26 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_26_ECG.npy - 667 R-peaks, mean HR 66.7 BPM, SDNN 74.1 ms, ECG inter-beat CV 0.082.
- Detector IBI CV across ROIs: 0.266-0.274 (ECG inter-beat CV 0.082). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 132.0, 132.0]; detector beat-implied BPM: [70.7, 71.0, 71.1]; ECG mean HR 66.7 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
