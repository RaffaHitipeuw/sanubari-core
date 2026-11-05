# Phase 9.0 — Signal validation: Subject 20

## ROI: `forehead` (source: Subject_20_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.52 dB, spectral concentration=0.096, ACF regularity=0.071 (peak 0.185 @ 72.0 BPM)
- legacy detector: 707 peaks, IBI CV=0.274, implied BPM=70.7; FFT BPM=144.0
- posterior detector: 823 peaks, IBI CV=0.296; regularity legacy=67.1% posterior=8.8%
- motion proxy: frame-diff mean=0.2100 p95=0.7178; low-frequency/cardiac power ratio=6.218; exposure drift=n/a; brightness mean=64.1 std=2.8; saturated=0.000; flat=0.000
- ground truth: 687 true beats, 707 detected, matched=297, missed=390, false=410, sensitivity=0.432, precision=0.420, mean |interval error|=0.0752 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 144.0 |
| snr_db | 0.52 |
| spectral_concentration | 0.0962 |
| n_peaks_legacy | 707 |
| n_peaks_posterior | 823 |
| regularity_legacy_pct | 67.1 |
| regularity_posterior_pct | 8.8 |
| sqi_legacy | 38.9 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 64.06 |
| brightness_std | 2.84 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.21 |
| frame_diff_p95 | 0.7178 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 706, 'mean_ibi_s': 0.84835, 'std_ibi_s': 0.23257, 'median_ibi_s': 0.8, 'cv': 0.27415, 'rmssd_ms': 314.33, 'pnn50_pct': 85.25, 'min_ibi_s': 0.5, 'max_ibi_s': 1.7, 'implied_bpm': 70.73}
- posterior detector IBI: {'n_intervals': 822, 'mean_ibi_s': 0.72863, 'std_ibi_s': 0.21564, 'median_ibi_s': 0.7, 'cv': 0.29595, 'rmssd_ms': 298.21, 'pnn50_pct': 84.04, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.66667, 'implied_bpm': 82.35}

- autocorrelation: {'acf_peak_value': 0.1853, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0705}

## ROI: `cheek_left` (source: Subject_20_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=0.96 dB, spectral concentration=0.099, ACF regularity=0.117 (peak 0.209 @ 72.0 BPM)
- legacy detector: 710 peaks, IBI CV=0.281, implied BPM=71.0; FFT BPM=108.0
- posterior detector: 821 peaks, IBI CV=0.297; regularity legacy=66.3% posterior=11.7%
- motion proxy: frame-diff mean=0.1710 p95=0.6421; low-frequency/cardiac power ratio=10.898; exposure drift=n/a; brightness mean=86.3 std=4.1; saturated=0.000; flat=0.000
- ground truth: 687 true beats, 710 detected, matched=303, missed=384, false=407, sensitivity=0.441, precision=0.427, mean |interval error|=0.0757 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 108.0 |
| snr_db | 0.96 |
| spectral_concentration | 0.0986 |
| n_peaks_legacy | 710 |
| n_peaks_posterior | 821 |
| regularity_legacy_pct | 66.3 |
| regularity_posterior_pct | 11.7 |
| sqi_legacy | 75.6 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 86.28 |
| brightness_std | 4.13 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.171 |
| frame_diff_p95 | 0.6421 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 709, 'mean_ibi_s': 0.84518, 'std_ibi_s': 0.23741, 'median_ibi_s': 0.8, 'cv': 0.2809, 'rmssd_ms': 327.68, 'pnn50_pct': 84.75, 'min_ibi_s': 0.5, 'max_ibi_s': 1.96667, 'implied_bpm': 70.99}
- posterior detector IBI: {'n_intervals': 820, 'mean_ibi_s': 0.73077, 'std_ibi_s': 0.21702, 'median_ibi_s': 0.73333, 'cv': 0.29697, 'rmssd_ms': 297.43, 'pnn50_pct': 84.37, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.56667, 'implied_bpm': 82.1}

- autocorrelation: {'acf_peak_value': 0.2085, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1171}

## ROI: `cheek_right` (source: Subject_20_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.45 dB, spectral concentration=0.074, ACF regularity=0.135 (peak 0.217 @ 69.2 BPM)
- legacy detector: 703 peaks, IBI CV=0.273, implied BPM=70.3; FFT BPM=132.0
- posterior detector: 807 peaks, IBI CV=0.297; regularity legacy=67.2% posterior=12.8%
- motion proxy: frame-diff mean=0.1061 p95=0.3477; low-frequency/cardiac power ratio=14.166; exposure drift=n/a; brightness mean=94.0 std=4.3; saturated=0.000; flat=0.000
- ground truth: 687 true beats, 703 detected, matched=308, missed=379, false=395, sensitivity=0.448, precision=0.438, mean |interval error|=0.0785 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.45 |
| spectral_concentration | 0.0744 |
| n_peaks_legacy | 703 |
| n_peaks_posterior | 807 |
| regularity_legacy_pct | 67.2 |
| regularity_posterior_pct | 12.8 |
| sqi_legacy | 39.1 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 94.0 |
| brightness_std | 4.29 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1061 |
| frame_diff_p95 | 0.3477 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 702, 'mean_ibi_s': 0.85304, 'std_ibi_s': 0.23287, 'median_ibi_s': 0.83333, 'cv': 0.27299, 'rmssd_ms': 326.64, 'pnn50_pct': 87.3, 'min_ibi_s': 0.5, 'max_ibi_s': 1.66667, 'implied_bpm': 70.34}
- posterior detector IBI: {'n_intervals': 806, 'mean_ibi_s': 0.74367, 'std_ibi_s': 0.22084, 'median_ibi_s': 0.73333, 'cv': 0.29695, 'rmssd_ms': 298.75, 'pnn50_pct': 86.21, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.63333, 'implied_bpm': 80.68}

- autocorrelation: {'acf_peak_value': 0.2173, 'acf_peak_lag_s': 0.8667, 'acf_peak_bpm': 69.23, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1345}

## Notes

- Subject 20 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_20_ECG.npy - 687 R-peaks, mean HR 68.8 BPM, SDNN 46.2 ms, ECG inter-beat CV 0.053.
- Detector IBI CV across ROIs: 0.273-0.281 (ECG inter-beat CV 0.053). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [108.0, 132.0, 144.00000000000003]; detector beat-implied BPM: [70.7, 71.0, 70.3]; ECG mean HR 68.8 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
