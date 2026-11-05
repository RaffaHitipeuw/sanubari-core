# Phase 9.0 — Signal validation: Subject 11

## ROI: `forehead` (source: Subject_11_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.65 dB, spectral concentration=0.074, ACF regularity=0.018 (peak 0.159 @ 72.0 BPM)
- legacy detector: 698 peaks, IBI CV=0.280, implied BPM=69.9; FFT BPM=132.0
- posterior detector: 811 peaks, IBI CV=0.308; regularity legacy=66.4% posterior=4.9%
- motion proxy: frame-diff mean=0.1748 p95=0.6490; low-frequency/cardiac power ratio=1.443; exposure drift=n/a; brightness mean=108.2 std=0.6; saturated=0.000; flat=0.000
- ground truth: 864 true beats, 698 detected, matched=343, missed=521, false=355, sensitivity=0.397, precision=0.491, mean |interval error|=0.0765 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.65 |
| spectral_concentration | 0.0741 |
| n_peaks_legacy | 698 |
| n_peaks_posterior | 811 |
| regularity_legacy_pct | 66.4 |
| regularity_posterior_pct | 4.9 |
| sqi_legacy | 39.5 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 108.15 |
| brightness_std | 0.63 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1748 |
| frame_diff_p95 | 0.649 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 697, 'mean_ibi_s': 0.85887, 'std_ibi_s': 0.24039, 'median_ibi_s': 0.83333, 'cv': 0.27989, 'rmssd_ms': 330.36, 'pnn50_pct': 85.78, 'min_ibi_s': 0.5, 'max_ibi_s': 1.83333, 'implied_bpm': 69.86}
- posterior detector IBI: {'n_intervals': 810, 'mean_ibi_s': 0.73905, 'std_ibi_s': 0.22785, 'median_ibi_s': 0.73333, 'cv': 0.30829, 'rmssd_ms': 312.67, 'pnn50_pct': 86.03, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.83333, 'implied_bpm': 81.18}

- autocorrelation: {'acf_peak_value': 0.1588, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0176}

## ROI: `cheek_left` (source: Subject_11_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.10 dB, spectral concentration=0.080, ACF regularity=0.007 (peak 0.154 @ 75.0 BPM)
- legacy detector: 712 peaks, IBI CV=0.284, implied BPM=71.2; FFT BPM=120.0
- posterior detector: 830 peaks, IBI CV=0.307; regularity legacy=66.0% posterior=3.8%
- motion proxy: frame-diff mean=0.0964 p95=0.3293; low-frequency/cardiac power ratio=2.523; exposure drift=n/a; brightness mean=90.6 std=0.5; saturated=0.000; flat=0.000
- ground truth: 864 true beats, 712 detected, matched=348, missed=516, false=364, sensitivity=0.403, precision=0.489, mean |interval error|=0.0788 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | -0.1 |
| spectral_concentration | 0.0799 |
| n_peaks_legacy | 712 |
| n_peaks_posterior | 830 |
| regularity_legacy_pct | 66.0 |
| regularity_posterior_pct | 3.8 |
| sqi_legacy | 42.2 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 90.63 |
| brightness_std | 0.46 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.0964 |
| frame_diff_p95 | 0.3293 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 711, 'mean_ibi_s': 0.84243, 'std_ibi_s': 0.23895, 'median_ibi_s': 0.8, 'cv': 0.28365, 'rmssd_ms': 330.65, 'pnn50_pct': 87.75, 'min_ibi_s': 0.5, 'max_ibi_s': 1.7, 'implied_bpm': 71.22}
- posterior detector IBI: {'n_intervals': 829, 'mean_ibi_s': 0.72252, 'std_ibi_s': 0.22172, 'median_ibi_s': 0.7, 'cv': 0.30687, 'rmssd_ms': 313.86, 'pnn50_pct': 87.8, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.5, 'implied_bpm': 83.04}

- autocorrelation: {'acf_peak_value': 0.1537, 'acf_peak_lag_s': 0.8, 'acf_peak_bpm': 75.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0074}

## ROI: `cheek_right` (source: Subject_11_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.37 dB, spectral concentration=0.085, ACF regularity=0.000 (peak 0.141 @ 72.0 BPM)
- legacy detector: 721 peaks, IBI CV=0.281, implied BPM=72.1; FFT BPM=120.0
- posterior detector: 820 peaks, IBI CV=0.294; regularity legacy=66.2% posterior=2.6%
- motion proxy: frame-diff mean=0.1094 p95=0.4183; low-frequency/cardiac power ratio=2.146; exposure drift=n/a; brightness mean=91.3 std=0.6; saturated=0.000; flat=0.000
- ground truth: 864 true beats, 721 detected, matched=353, missed=511, false=368, sensitivity=0.409, precision=0.490, mean |interval error|=0.0787 s
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
| spectral_concentration | 0.0852 |
| n_peaks_legacy | 721 |
| n_peaks_posterior | 820 |
| regularity_legacy_pct | 66.2 |
| regularity_posterior_pct | 2.6 |
| sqi_legacy | 42.8 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 91.33 |
| brightness_std | 0.64 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1094 |
| frame_diff_p95 | 0.4183 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 720, 'mean_ibi_s': 0.83162, 'std_ibi_s': 0.23407, 'median_ibi_s': 0.8, 'cv': 0.28146, 'rmssd_ms': 321.34, 'pnn50_pct': 84.56, 'min_ibi_s': 0.5, 'max_ibi_s': 1.63333, 'implied_bpm': 72.15}
- posterior detector IBI: {'n_intervals': 819, 'mean_ibi_s': 0.73109, 'std_ibi_s': 0.21472, 'median_ibi_s': 0.7, 'cv': 0.29369, 'rmssd_ms': 290.5, 'pnn50_pct': 84.47, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.63333, 'implied_bpm': 82.07}

- autocorrelation: {'acf_peak_value': 0.1411, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0}

## Notes

- Subject 11 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_11_ECG.npy - 864 R-peaks, mean HR 86.4 BPM, SDNN 31.3 ms, ECG inter-beat CV 0.045.
- Detector IBI CV across ROIs: 0.280-0.284 (ECG inter-beat CV 0.045). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 120.0, 132.0]; detector beat-implied BPM: [69.9, 71.2, 72.1]; ECG mean HR 86.4 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
