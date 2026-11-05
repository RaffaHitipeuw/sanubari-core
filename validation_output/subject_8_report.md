# Phase 9.0 — Signal validation: Subject 8

## ROI: `forehead` (source: Subject_8_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.74 dB, spectral concentration=0.093, ACF regularity=0.026 (peak 0.163 @ 72.0 BPM)
- legacy detector: 712 peaks, IBI CV=0.278, implied BPM=71.2; FFT BPM=120.0
- posterior detector: 827 peaks, IBI CV=0.296; regularity legacy=66.6% posterior=5.1%
- motion proxy: frame-diff mean=0.1589 p95=0.5191; low-frequency/cardiac power ratio=3.930; exposure drift=n/a; brightness mean=100.4 std=1.0; saturated=0.000; flat=0.000
- ground truth: 864 true beats, 712 detected, matched=402, missed=462, false=310, sensitivity=0.465, precision=0.565, mean |interval error|=0.0709 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.74 |
| spectral_concentration | 0.0927 |
| n_peaks_legacy | 712 |
| n_peaks_posterior | 827 |
| regularity_legacy_pct | 66.6 |
| regularity_posterior_pct | 5.1 |
| sqi_legacy | 42.2 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 100.42 |
| brightness_std | 1.0 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1589 |
| frame_diff_p95 | 0.5191 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 711, 'mean_ibi_s': 0.84304, 'std_ibi_s': 0.23458, 'median_ibi_s': 0.8, 'cv': 0.27826, 'rmssd_ms': 327.35, 'pnn50_pct': 88.03, 'min_ibi_s': 0.5, 'max_ibi_s': 1.9, 'implied_bpm': 71.17}
- posterior detector IBI: {'n_intervals': 826, 'mean_ibi_s': 0.72567, 'std_ibi_s': 0.21472, 'median_ibi_s': 0.7, 'cv': 0.29589, 'rmssd_ms': 294.72, 'pnn50_pct': 85.21, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.53333, 'implied_bpm': 82.68}

- autocorrelation: {'acf_peak_value': 0.1632, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0263}

## ROI: `cheek_left` (source: Subject_8_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.19 dB, spectral concentration=0.078, ACF regularity=0.036 (peak 0.168 @ 72.0 BPM)
- legacy detector: 700 peaks, IBI CV=0.286, implied BPM=70.1; FFT BPM=120.0
- posterior detector: 826 peaks, IBI CV=0.307; regularity legacy=65.7% posterior=5.3%
- motion proxy: frame-diff mean=0.1901 p95=0.9373; low-frequency/cardiac power ratio=2.703; exposure drift=n/a; brightness mean=71.9 std=1.8; saturated=0.000; flat=0.000
- ground truth: 864 true beats, 700 detected, matched=374, missed=490, false=326, sensitivity=0.433, precision=0.534, mean |interval error|=0.0727 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | pos |
| bpm_fft | 120.0 |
| snr_db | 0.19 |
| spectral_concentration | 0.0781 |
| n_peaks_legacy | 700 |
| n_peaks_posterior | 826 |
| regularity_legacy_pct | 65.7 |
| regularity_posterior_pct | 5.3 |
| sqi_legacy | 41.3 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 71.87 |
| brightness_std | 1.76 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1901 |
| frame_diff_p95 | 0.9373 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 699, 'mean_ibi_s': 0.85622, 'std_ibi_s': 0.24448, 'median_ibi_s': 0.8, 'cv': 0.28554, 'rmssd_ms': 347.07, 'pnn50_pct': 89.4, 'min_ibi_s': 0.5, 'max_ibi_s': 1.76667, 'implied_bpm': 70.08}
- posterior detector IBI: {'n_intervals': 825, 'mean_ibi_s': 0.72602, 'std_ibi_s': 0.22287, 'median_ibi_s': 0.7, 'cv': 0.30698, 'rmssd_ms': 308.7, 'pnn50_pct': 87.14, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.63333, 'implied_bpm': 82.64}

- autocorrelation: {'acf_peak_value': 0.1678, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0357}

## ROI: `cheek_right` (source: Subject_8_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.26 dB, spectral concentration=0.082, ACF regularity=0.023 (peak 0.161 @ 72.0 BPM)
- legacy detector: 708 peaks, IBI CV=0.277, implied BPM=70.8; FFT BPM=120.0
- posterior detector: 816 peaks, IBI CV=0.306; regularity legacy=66.8% posterior=4.1%
- motion proxy: frame-diff mean=0.1791 p95=0.9482; low-frequency/cardiac power ratio=2.129; exposure drift=n/a; brightness mean=74.3 std=1.5; saturated=0.000; flat=0.000
- ground truth: 864 true beats, 708 detected, matched=364, missed=500, false=344, sensitivity=0.421, precision=0.514, mean |interval error|=0.0712 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 120.0 |
| snr_db | 0.26 |
| spectral_concentration | 0.0816 |
| n_peaks_legacy | 708 |
| n_peaks_posterior | 816 |
| regularity_legacy_pct | 66.8 |
| regularity_posterior_pct | 4.1 |
| sqi_legacy | 42.5 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 74.28 |
| brightness_std | 1.55 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1791 |
| frame_diff_p95 | 0.9482 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 707, 'mean_ibi_s': 0.84767, 'std_ibi_s': 0.23454, 'median_ibi_s': 0.8, 'cv': 0.27669, 'rmssd_ms': 319.21, 'pnn50_pct': 87.54, 'min_ibi_s': 0.5, 'max_ibi_s': 2.0, 'implied_bpm': 70.78}
- posterior detector IBI: {'n_intervals': 815, 'mean_ibi_s': 0.73534, 'std_ibi_s': 0.2249, 'median_ibi_s': 0.7, 'cv': 0.30584, 'rmssd_ms': 308.85, 'pnn50_pct': 86.12, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.53333, 'implied_bpm': 81.6}

- autocorrelation: {'acf_peak_value': 0.1614, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0228}

## Notes

- Subject 8 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_8_ECG.npy - 864 R-peaks, mean HR 86.5 BPM, SDNN 42.9 ms, ECG inter-beat CV 0.062.
- Detector IBI CV across ROIs: 0.277-0.286 (ECG inter-beat CV 0.062). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [120.0, 120.0, 120.0]; detector beat-implied BPM: [71.2, 70.1, 70.8]; ECG mean HR 86.5 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
