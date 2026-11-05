# Phase 9.0 — Signal validation: Subject 9

## ROI: `forehead` (source: Subject_9_Forehead_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.53 dB, spectral concentration=0.057, ACF regularity=0.125 (peak 0.213 @ 72.0 BPM)
- legacy detector: 704 peaks, IBI CV=0.273, implied BPM=70.4; FFT BPM=144.0
- posterior detector: 815 peaks, IBI CV=0.291; regularity legacy=67.2% posterior=13.8%
- motion proxy: frame-diff mean=0.1642 p95=0.5200; low-frequency/cardiac power ratio=40.372; exposure drift=n/a; brightness mean=85.5 std=8.6; saturated=0.000; flat=0.000
- ground truth: 905 true beats, 704 detected, matched=380, missed=525, false=324, sensitivity=0.420, precision=0.540, mean |interval error|=0.0746 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | chrom |
| bpm_fft | 144.0 |
| snr_db | -1.53 |
| spectral_concentration | 0.057 |
| n_peaks_legacy | 704 |
| n_peaks_posterior | 815 |
| regularity_legacy_pct | 67.2 |
| regularity_posterior_pct | 13.8 |
| sqi_legacy | 40.0 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 85.54 |
| brightness_std | 8.61 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.1642 |
| frame_diff_p95 | 0.52 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 703, 'mean_ibi_s': 0.85263, 'std_ibi_s': 0.2331, 'median_ibi_s': 0.8, 'cv': 0.27339, 'rmssd_ms': 331.31, 'pnn50_pct': 87.04, 'min_ibi_s': 0.5, 'max_ibi_s': 1.8, 'implied_bpm': 70.37}
- posterior detector IBI: {'n_intervals': 814, 'mean_ibi_s': 0.73636, 'std_ibi_s': 0.21456, 'median_ibi_s': 0.73333, 'cv': 0.29137, 'rmssd_ms': 297.86, 'pnn50_pct': 86.96, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.8, 'implied_bpm': 81.48}

- autocorrelation: {'acf_peak_value': 0.2127, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.1254}

## ROI: `cheek_left` (source: Subject_9_Cheek1_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-1.28 dB, spectral concentration=0.065, ACF regularity=0.064 (peak 0.182 @ 72.0 BPM)
- legacy detector: 701 peaks, IBI CV=0.274, implied BPM=70.1; FFT BPM=132.0
- posterior detector: 811 peaks, IBI CV=0.299; regularity legacy=67.1% posterior=8.0%
- motion proxy: frame-diff mean=0.2250 p95=0.8250; low-frequency/cardiac power ratio=30.344; exposure drift=n/a; brightness mean=89.0 std=9.0; saturated=0.000; flat=0.000
- ground truth: 905 true beats, 701 detected, matched=367, missed=538, false=334, sensitivity=0.406, precision=0.524, mean |interval error|=0.0765 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | pos |
| bpm_fft | 132.0 |
| snr_db | -1.28 |
| spectral_concentration | 0.0645 |
| n_peaks_legacy | 701 |
| n_peaks_posterior | 811 |
| regularity_legacy_pct | 67.1 |
| regularity_posterior_pct | 8.0 |
| sqi_legacy | 38.8 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 88.96 |
| brightness_std | 9.0 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.225 |
| frame_diff_p95 | 0.825 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 700, 'mean_ibi_s': 0.85619, 'std_ibi_s': 0.23496, 'median_ibi_s': 0.83333, 'cv': 0.27443, 'rmssd_ms': 326.38, 'pnn50_pct': 85.69, 'min_ibi_s': 0.5, 'max_ibi_s': 1.83333, 'implied_bpm': 70.08}
- posterior detector IBI: {'n_intervals': 810, 'mean_ibi_s': 0.73992, 'std_ibi_s': 0.22126, 'median_ibi_s': 0.73333, 'cv': 0.29903, 'rmssd_ms': 308.0, 'pnn50_pct': 85.66, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.66667, 'implied_bpm': 81.09}

- autocorrelation: {'acf_peak_value': 0.1821, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0642}

## ROI: `cheek_right` (source: Subject_9_Cheek2_.avi)

**Verdict: A - Genuinely poor signal quality (acquisition-side contributors present)** (confidence: high)

Evidence:
- SNR=-0.68 dB, spectral concentration=0.068, ACF regularity=0.057 (peak 0.179 @ 72.0 BPM)
- legacy detector: 716 peaks, IBI CV=0.276, implied BPM=71.6; FFT BPM=132.0
- posterior detector: 810 peaks, IBI CV=0.293; regularity legacy=66.8% posterior=8.0%
- motion proxy: frame-diff mean=0.2079 p95=0.8963; low-frequency/cardiac power ratio=30.669; exposure drift=n/a; brightness mean=89.8 std=8.7; saturated=0.000; flat=0.000
- ground truth: 905 true beats, 716 detected, matched=366, missed=539, false=350, sensitivity=0.404, precision=0.511, mean |interval error|=0.0766 s
- The optical signal itself does not carry a usable pulse (weak SNR / spectral concentration / ACF periodicity).
- Acquisition-side indicators are ALSO degraded (low-frequency / illumination dominance, exposure, saturation or a flat ROI), so the upstream cause is very likely the acquisition or the ROI crop, not the detector.

Caveats:
- Irregular detected intervals describe the detector's output, not a measured heart rhythm; no arrhythmia conclusion is drawn.

| metric | value |
| --- | --- |
| n_samples | 18000 |
| method | green |
| bpm_fft | 132.0 |
| snr_db | -0.68 |
| spectral_concentration | 0.0681 |
| n_peaks_legacy | 716 |
| n_peaks_posterior | 810 |
| regularity_legacy_pct | 66.8 |
| regularity_posterior_pct | 8.0 |
| sqi_legacy | 38.4 |
| sqi_posterior | 0.0 |
| motion_score | nan |
| exposure_drift | nan |
| mean_brightness | 89.79 |
| brightness_std | 8.7 |
| saturation_fraction | 0.0 |
| frame_diff_mean | 0.2079 |
| frame_diff_p95 | 0.8963 |
| flat_fraction | 0.0 |

- legacy detector IBI: {'n_intervals': 715, 'mean_ibi_s': 0.838, 'std_ibi_s': 0.23161, 'median_ibi_s': 0.8, 'cv': 0.27638, 'rmssd_ms': 314.85, 'pnn50_pct': 85.29, 'min_ibi_s': 0.5, 'max_ibi_s': 1.73333, 'implied_bpm': 71.6}
- posterior detector IBI: {'n_intervals': 809, 'mean_ibi_s': 0.74063, 'std_ibi_s': 0.21722, 'median_ibi_s': 0.73333, 'cv': 0.2933, 'rmssd_ms': 290.27, 'pnn50_pct': 85.02, 'min_ibi_s': 0.43333, 'max_ibi_s': 1.73333, 'implied_bpm': 81.01}

- autocorrelation: {'acf_peak_value': 0.1787, 'acf_peak_lag_s': 0.8333, 'acf_peak_bpm': 72.0, 'acf_peak_is_local': True, 'acf_peak_hits': 1, 'acf_regularity': 0.0575}

## Notes

- Subject 9 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- ECG reference: Subject_9_ECG.npy - 905 R-peaks, mean HR 90.9 BPM, SDNN 63.2 ms, ECG inter-beat CV 0.095.
- Detector IBI CV across ROIs: 0.273-0.276 (ECG inter-beat CV 0.095). A detector CV far above the ECG CV means the irregularity is produced by the detector.
- Production FFT BPM: [132.0, 132.0, 144.00000000000003]; detector beat-implied BPM: [70.4, 70.1, 71.6]; ECG mean HR 90.9 BPM.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
