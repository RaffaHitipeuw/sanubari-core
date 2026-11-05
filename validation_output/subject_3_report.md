# Phase 9.0 — Signal validation: Subject 3

## ROI: `forehead` (source: Subject_3_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.19 dB, spectral concentration=0.081, ACF regularity=0.196 (peak 0.248 @ 72.0 BPM)
- legacy detector: 697 peaks, IBI CV=0.266, implied BPM=69.7; FFT BPM=120.0
- posterior detector: 802 peaks, IBI CV=0.303; regularity legacy=68.1% posterior=16.6%
- motion proxy: frame-diff mean=0.1433 p95=0.5672; low-frequency/cardiac power ratio=3.036; exposure drift=n/a; brightness mean=100.0 std=2.8; saturated=0.000; flat=0.000
- ground truth: 788 true beats, 697 detected, matched=360, missed=428, false=337, sensitivity=0.457, precision=0.516, mean |interval error|=0.0743 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.19 |
| spectral_concentration | 0.0814 |
| n_peaks_legacy | 697 |
| n_peaks_posterior | 802 |
| regularity_legacy_pct | 68.1 |
| regularity_posterior_pct | 16.6 |
| sqi_legacy | 43.9 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 100.01 |
| brightness_std | 2.76 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1433 |
| frame_diff_p95 | 0.5672 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 696, 'mean_ibi_s': 0.86025, 'std_ibi_s': 0.22898, 'median_ibi_s': 0.83333, 'cv': 0.26617, 'rmssd_ms': 329.58, 'pnn50_pct': 87.91, 'min_ibi_s': 0.5, 'max_ibi_s': 1.63333, 'implied_bpm': 69.75}
- posterior detector IBI: {'n_intervals': 801, 'mean_ibi_s': 0.74802, 'std_ibi_s': 0.22699, 'median_ibi_s': 0.73333, 'cv': 0.30346, 'rmssd_ms': 319.09, 'pnn50_pct': 86.0, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.53333, 'implied_bpm': 80.21}

- autocorrelation: {'acf_peak_value': 0.2478, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1957}

## ROI: `cheek_left` (source: Subject_3_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.10 dB, spectral concentration=0.075, ACF regularity=0.146 (peak 0.223 @ 69.2 BPM)
- legacy detector: 706 peaks, IBI CV=0.277, implied BPM=70.6; FFT BPM=120.0
- posterior detector: 812 peaks, IBI CV=0.301; regularity legacy=66.8% posterior=12.9%
- motion proxy: frame-diff mean=0.0756 p95=0.2336; low-frequency/cardiac power ratio=3.141; exposure drift=n/a; brightness mean=90.3 std=2.2; saturated=0.000; flat=0.000
- ground truth: 788 true beats, 706 detected, matched=340, missed=448, false=366, sensitivity=0.431, precision=0.482, mean |interval error|=0.0758 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | pos |
| bpm_fft | 120.0 |
| snr_db | -0.1 |
| spectral_concentration | 0.0754 |
| n_peaks_legacy | 706 |
| n_peaks_posterior | 812 |
| regularity_legacy_pct | 66.8 |
| regularity_posterior_pct | 12.9 |
| sqi_legacy | 43.2 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 90.27 |
| brightness_std | 2.17 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.0756 |
| frame_diff_p95 | 0.2336 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 705, 'mean_ibi_s': 0.85007, 'std_ibi_s': 0.23552, 'median_ibi_s': 0.8, 'cv': 0.27705, 'rmssd_ms': 328.98, 'pnn50_pct': 86.93, 'min_ibi_s': 0.5, 'max_ibi_s': 1.93333, 'implied_bpm': 70.58}
- posterior detector IBI: {'n_intervals': 811, 'mean_ibi_s': 0.73896, 'std_ibi_s': 0.22212, 'median_ibi_s': 0.73333, 'cv': 0.30059, 'rmssd_ms': 297.43, 'pnn50_pct': 85.56, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.93333, 'implied_bpm': 81.19}

- autocorrelation: {'acf_peak_value': 0.223, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.146}

## ROI: `cheek_right` (source: Subject_3_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.51 dB, spectral concentration=0.070, ACF regularity=0.188 (peak 0.244 @ 72.0 BPM)
- legacy detector: 694 peaks, IBI CV=0.272, implied BPM=69.5; FFT BPM=144.0
- posterior detector: 797 peaks, IBI CV=0.300; regularity legacy=67.4% posterior=15.9%
- motion proxy: frame-diff mean=0.0983 p95=0.3430; low-frequency/cardiac power ratio=2.742; exposure drift=n/a; brightness mean=94.6 std=2.4; saturated=0.000; flat=0.000
- ground truth: 788 true beats, 694 detected, matched=363, missed=425, false=331, sensitivity=0.461, precision=0.523, mean |interval error|=0.0706 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | chrom |
| bpm_fft | 144.0 |
| snr_db | -0.51 |
| spectral_concentration | 0.0698 |
| n_peaks_legacy | 694 |
| n_peaks_posterior | 797 |
| regularity_legacy_pct | 67.4 |
| regularity_posterior_pct | 15.9 |
| sqi_legacy | 39.3 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 94.62 |
| brightness_std | 2.36 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.0983 |
| frame_diff_p95 | 0.343 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 693, 'mean_ibi_s': 0.86383, 'std_ibi_s': 0.23469, 'median_ibi_s': 0.83333, 'cv': 0.27169, 'rmssd_ms': 321.06, 'pnn50_pct': 84.83, 'min_ibi_s': 0.5, 'max_ibi_s': 1.96667, 'implied_bpm': 69.46}
- posterior detector IBI: {'n_intervals': 796, 'mean_ibi_s': 0.75205, 'std_ibi_s': 0.22578, 'median_ibi_s': 0.73333, 'cv': 0.30022, 'rmssd_ms': 323.87, 'pnn50_pct': 86.54, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.6, 'implied_bpm': 79.78}

- autocorrelation: {'acf_peak_value': 0.2441, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1881}

## Notes

- Subject 3 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_3_ECG.npy - 788 R-peaks, mean HR 79.2 BPM, SDNN 115.8 ms, ECG inter-beat CV 0.152.
- Detector IBI CV across ROIs: 0.266-0.277 (ECG inter-beat CV 0.152). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 120.0, 144.00000000000003]; detector beat-implied BPM: [69.7, 70.6, 69.5]; ECG mean HR 79.2 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
