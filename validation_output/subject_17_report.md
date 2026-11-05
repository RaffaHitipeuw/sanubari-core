# Phase 9.0 — Signal validation: Subject 17

## ROI: `forehead` (source: Subject_17_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.46 dB, spectral concentration=0.078, ACF regularity=0.146 (peak 0.223 @ 72.0 BPM)
- legacy detector: 709 peaks, IBI CV=0.268, implied BPM=71.0; FFT BPM=120.0
- posterior detector: 808 peaks, IBI CV=0.292; regularity legacy=67.8% posterior=14.1%
- motion proxy: frame-diff mean=0.1131 p95=0.3511; low-frequency/cardiac power ratio=2.208; exposure drift=n/a; brightness mean=96.4 std=0.6; saturated=0.000; flat=0.000
- ground truth: 635 true beats, 709 detected, matched=282, missed=353, false=427, sensitivity=0.444, precision=0.398, mean |interval error|=0.0756 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.46 |
| spectral_concentration | 0.0783 |
| n_peaks_legacy | 709 |
| n_peaks_posterior | 808 |
| regularity_legacy_pct | 67.8 |
| regularity_posterior_pct | 14.1 |
| sqi_legacy | 42.7 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 96.4 |
| brightness_std | 0.59 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1131 |
| frame_diff_p95 | 0.3511 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 708, 'mean_ibi_s': 0.84529, 'std_ibi_s': 0.22691, 'median_ibi_s': 0.8, 'cv': 0.26843, 'rmssd_ms': 317.0, 'pnn50_pct': 84.87, 'min_ibi_s': 0.5, 'max_ibi_s': 1.7, 'implied_bpm': 70.98}
- posterior detector IBI: {'n_intervals': 807, 'mean_ibi_s': 0.74159, 'std_ibi_s': 0.2166, 'median_ibi_s': 0.73333, 'cv': 0.29207, 'rmssd_ms': 302.33, 'pnn50_pct': 84.49, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.63333, 'implied_bpm': 80.91}

- autocorrelation: {'acf_peak_value': 0.2231, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1462}

## ROI: `cheek_left` (source: Subject_17_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.48 dB, spectral concentration=0.088, ACF regularity=0.000 (peak 0.141 @ 72.0 BPM)
- legacy detector: 696 peaks, IBI CV=0.290, implied BPM=69.6; FFT BPM=132.0
- posterior detector: 823 peaks, IBI CV=0.319; regularity legacy=65.3% posterior=1.4%
- motion proxy: frame-diff mean=0.1562 p95=0.6834; low-frequency/cardiac power ratio=1.852; exposure drift=n/a; brightness mean=91.3 std=0.7; saturated=0.000; flat=0.000
- ground truth: 635 true beats, 696 detected, matched=254, missed=381, false=442, sensitivity=0.400, precision=0.365, mean |interval error|=0.0752 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | chrom |
| bpm_fft | 132.0 |
| snr_db | -0.48 |
| spectral_concentration | 0.0875 |
| n_peaks_legacy | 696 |
| n_peaks_posterior | 823 |
| regularity_legacy_pct | 65.3 |
| regularity_posterior_pct | 1.4 |
| sqi_legacy | 38.3 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 91.3 |
| brightness_std | 0.73 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1562 |
| frame_diff_p95 | 0.6834 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 695, 'mean_ibi_s': 0.86187, 'std_ibi_s': 0.24955, 'median_ibi_s': 0.83333, 'cv': 0.28954, 'rmssd_ms': 351.92, 'pnn50_pct': 88.62, 'min_ibi_s': 0.5, 'max_ibi_s': 2.0, 'implied_bpm': 69.62}
- posterior detector IBI: {'n_intervals': 822, 'mean_ibi_s': 0.72871, 'std_ibi_s': 0.23232, 'median_ibi_s': 0.7, 'cv': 0.31881, 'rmssd_ms': 325.12, 'pnn50_pct': 86.72, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.96667, 'implied_bpm': 82.34}

- autocorrelation: {'acf_peak_value': 0.1413, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0}

## ROI: `cheek_right` (source: Subject_17_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.12 dB, spectral concentration=0.082, ACF regularity=0.041 (peak 0.170 @ 72.0 BPM)
- legacy detector: 698 peaks, IBI CV=0.276, implied BPM=69.8; FFT BPM=132.0
- posterior detector: 816 peaks, IBI CV=0.293; regularity legacy=66.8% posterior=6.3%
- motion proxy: frame-diff mean=0.1602 p95=0.7048; low-frequency/cardiac power ratio=2.445; exposure drift=n/a; brightness mean=94.7 std=0.9; saturated=0.000; flat=0.000
- ground truth: 635 true beats, 698 detected, matched=284, missed=351, false=414, sensitivity=0.447, precision=0.407, mean |interval error|=0.0761 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.12 |
| spectral_concentration | 0.0824 |
| n_peaks_legacy | 698 |
| n_peaks_posterior | 816 |
| regularity_legacy_pct | 66.8 |
| regularity_posterior_pct | 6.3 |
| sqi_legacy | 39.5 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 94.68 |
| brightness_std | 0.92 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1602 |
| frame_diff_p95 | 0.7048 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 697, 'mean_ibi_s': 0.85921, 'std_ibi_s': 0.23736, 'median_ibi_s': 0.83333, 'cv': 0.27625, 'rmssd_ms': 335.51, 'pnn50_pct': 87.64, 'min_ibi_s': 0.5, 'max_ibi_s': 1.83333, 'implied_bpm': 69.83}
- posterior detector IBI: {'n_intervals': 815, 'mean_ibi_s': 0.73431, 'std_ibi_s': 0.21509, 'median_ibi_s': 0.73333, 'cv': 0.29292, 'rmssd_ms': 301.07, 'pnn50_pct': 88.08, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.53333, 'implied_bpm': 81.71}

- autocorrelation: {'acf_peak_value': 0.1705, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0409}

## Notes

- Subject 17 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_17_ECG.npy - 635 R-peaks, mean HR 63.7 BPM, SDNN 78.9 ms, ECG inter-beat CV 0.083.
- Detector IBI CV across ROIs: 0.268-0.290 (ECG inter-beat CV 0.083). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 132.0, 132.0]; detector beat-implied BPM: [71.0, 69.6, 69.8]; ECG mean HR 63.7 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
