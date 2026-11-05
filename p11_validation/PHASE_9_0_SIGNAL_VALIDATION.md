# Phase 9.0 — rPPG Signal Validation

**Status:** complete — diagnostic only, **no production code was changed**
**Repository:** `D:\main\Projects\Health`

---

## 1. Question this phase answers

> Is a low regularity / low SQI reading caused by (A) a genuinely poor optical
> pulse signal, (B) a failure of the peak detector, (C) a preprocessing / ROI
> artifact, or (D) something that cannot be decided without a reference sensor?

**It does not** answer whether any subject has an irregular heart rhythm. Every
interval statistic in this report describes *the detector's output on a
recording*, never a measured cardiac rhythm.

## 2. What was built

| Artefact | Path | Purpose |
| --- | --- | --- |
| Offline validation library | `signal_validation/` | Per-ROI signal extraction, production-identical preprocessing + peak detection, metrics, ground-truth matching, A/B/C/D classifier, signal export |
| CLI entry point | `phase90_signal_validation.py` | `synthetic` / `video` / `subject` / `session` sub-commands |
| Sweep summariser | `phase90_sweep_all.py` | Aggregates the per-subject reports into `sweep_summary.csv` / `.md` |
| BPM harmonic audit | `phase90_bpm_harmonic_audit.py` | Isolates where the production FFT BPM estimate goes wrong (see §7.1) |
| Tests with known ground truth | `tests/engine/test_signal_validation.py` | **40 tests**: metrics, ground-truth matching, detector scoring, classifier regression, reference comparison, signal export |
| Outputs | `validation_output/` | `synthetic_results.json`, `subject_<N>_report.md` (×27), `sweep_summary.csv`, `sweep_summary.md`, `signals/` (raw + filtered + peaks export), `raw_signals_demo.csv` |

The library **imports** production code (`rppg_core`, `rppg_sqi`) and calls it
read-only, so the numbers it reports are the numbers the live pipeline
produces. It re-implements only the *observation* layer (signal extraction,
peak timestamps, metrics), which production does not expose. It lives outside
the production tree and **no threshold in `rppg_config.py` was touched**.

### Production-identical signal path

```
raw ROI RGB  ->  MethodArbitrator.select_best()      (chrom / POS / green blend)
              ->  linear detrend
              ->  ExposureCompensator.normalize_roi_signal()
              ->  RespiratoryArtifactSuppressor.suppress()
              ->  bandpass_filter()                   (0.833-3.0 Hz, order 4, sosfilt)
              ->  z-normalisation
              ->  peak detection (BOTH production detectors, see below)
```

Both production peak detectors are evaluated, because they are **not**
identical and they feed different production numbers:

| Detector | Formula | Production consumer |
| --- | --- | --- |
| `legacy` | `find_peaks(sig_norm, distance=int(fps*0.50), prominence=cfg.PEAK_PROMINENCE_MIN, height=0.1)` | `rppg_core.compute_sqi()` → `breakdown["regularity"]` |
| `posterior` | `find_peaks(sig_z, distance=max(int(fps*0.45),5), prominence=0.35)` | `rppg_sqi.PosteriorSQI.compute()` → `regularity_score` |

The BPM estimate itself comes from an FFT (`estimate_bpm_fft`), **not** from
peak detection, so a peak-detector failure degrades regularity/SQI without
corrupting the BPM number by itself.

### Where the data comes from

| Source | What it gives | Used by |
| --- | --- | --- |
| `Dataset_rPPG-10/Subject_N/*.avi` | 30 fps, 64×64 ROI crops of one face region, 18 000 frames (600 s) | `video`, `subject` modes |
| `Dataset_rPPG-10/Subject_N/Subject_N_ECG.npy` | 1000 Hz ECG, 600 000 samples (600 s) — **a real reference, already in the repo** | beat and HR-trace comparison |
| `ReproducibilityLogger` `raw_signals.csv` export | live-session per-frame ROI channels (timestamp, roi_name, r, g, b, bpm, sqi) | `session` mode |
| `--export-signals DIR` | writes raw r/g/b, the filtered signal, both peak-timestamp lists and the metrics as CSV/JSON | offline inspection of any recording |

---

## 3. Reproduction

```bash
# interpreter with numpy / scipy / opencv (the env used for these results)
PY=/c/miniconda3/envs/rppg_env/python.exe

# 1. Controlled synthetic suite with known ground truth
$PY phase90_signal_validation.py --out validation_output synthetic

# 2. One ROI video against that subject's ECG (offset search = hypothesis)
$PY phase90_signal_validation.py --out validation_output video \
    --video Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi \
    --ecg  Dataset_rPPG-10/Subject_1/Subject_1_ECG.npy \
    --roi forehead --search-offset

# 3. All three ROI videos of one subject, against that subject's ECG
$PY phase90_signal_validation.py --out validation_output subject --subject 1 --search-offset

# 4. Whole dataset sweep (27 subjects, ~20 s each)
for s in $(seq 1 27); do
  $PY phase90_signal_validation.py --out validation_output subject --subject $s --search-offset
done

# 5. Aggregate the sweep
$PY phase90_sweep_all.py --dir validation_output

# 6. Export raw / filtered signals and peak timestamps for offline inspection
$PY phase90_signal_validation.py --out validation_output \
    --export-signals validation_output/signals video \
    --video Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi --roi forehead

# 7. A live session export (ReproducibilityLogger raw_signals.csv)
$PY phase90_signal_validation.py --out validation_output session --csv <path>/raw_signals.csv

# 8. BPM harmonic audit (§7.1)
$PY phase90_bpm_harmonic_audit.py \
    --video Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi \
    --ecg  Dataset_rPPG-10/Subject_1/Subject_1_ECG.npy

# 9. Tests
$PY -m pytest tests/engine/test_signal_validation.py -q      # 40 passed
$PY -m pytest tests/ -q                                      # 254 passed (incl. the 40)
```

---

## 4. Part 1 — Synthetic ground truth: is the detector at fault?

The synthetic suite (`signal_validation/synthetic.py`) generates pulses whose
peak times are known exactly. `clean` is the control; the other six cases each
inject one specific failure mode. The production filter is causal, so the
filtered waveform lags the true pulse by the filter group delay; every
comparison therefore uses `match_peaks_with_latency()`, which estimates that
delay robustly (median offset over all candidate pairings, not an argmax that
a corrupted region could hijack).

Results (`validation_output/synthetic_results.json`):

| case | detector | true | detected | matched | missed | false | sens | prec | latency s | IBI CV | ACF reg | SNR dB | verdict | expected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| clean | legacy | 36 | 36 | 36 | 0 | 0 | 1.00 | 1.00 | 0.28 | 0.020 | 1.00 | 23.74 | OK | OK |
| clean | posterior | 36 | 36 | 36 | 0 | 0 | 1.00 | 1.00 | 0.28 | 0.020 | 1.00 | 23.74 | OK | OK |
| noisy | legacy | 36 | 36 | 34 | 2 | 2 | 0.94 | 0.94 | 0.28 | 0.113 | 1.00 | 5.59 | A | A |
| noisy | posterior | 36 | 36 | 34 | 2 | 2 | 0.94 | 0.94 | 0.28 | 0.113 | 1.00 | 5.59 | A | A |
| motion | legacy | 36 | 36 | 36 | 0 | 0 | 1.00 | 1.00 | 0.28 | 0.032 | 1.00 | 20.51 | C | C |
| motion | posterior | 36 | 36 | 36 | 0 | 0 | 1.00 | 1.00 | 0.28 | 0.032 | 1.00 | 20.51 | C | C |
| missing_peaks | legacy | 36 | 36 | 31 | 5 | 5 | 0.86 | 0.86 | 0.28 | 0.128 | 1.00 | 17.57 | B | B |
| missing_peaks | posterior | 36 | 36 | 31 | 5 | 5 | 0.86 | 0.86 | 0.28 | 0.128 | 1.00 | 17.57 | B | B |
| extra_peaks | legacy | 25 | 29 | 19 | 6 | 10 | 0.76 | 0.66 | 0.18 | 0.216 | 1.00 | 22.59 | B | B |
| extra_peaks | posterior | 25 | 29 | 19 | 6 | 10 | 0.76 | 0.66 | 0.18 | 0.216 | 1.00 | 22.59 | B | B |
| flat | legacy | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0.00 | n/a | 0.00 | -90.0 | A | A |
| flat | posterior | 0 | 0 | 0 | 0 | 0 | n/a | n/a | 0.00 | n/a | 0.00 | -90.0 | A | A |
| white_noise | legacy | 0 | 36 | 0 | 0 | 36 | n/a | 0.00 | 0.00 | 0.290 | 0.18 | 2.67 | A | A |
| white_noise | posterior | 0 | 39 | 0 | 0 | 39 | n/a | 0.00 | 0.00 | 0.298 | 0.18 | 2.67 | A | A |

**Reading the table**

* `clean` → **the detector is not broken.** With a real pulse present, both
  production detectors find every beat (sensitivity = precision = 1.00) with
  a mean absolute interval error of ~6 ms. Any "the detector is wrong" claim
  has to survive this control.
* `flat` and `white_noise` → the correct behaviour is to find **no** beats.
  `flat` finds none. `white_noise` finds ~36 "beats" that are noise — the
  *reported* regularity collapses, which is the intended behaviour (no pulse,
  no periodicity).
* `missing_peaks` (a 5-beat motion burst that fully masks the pulse) → 5 beats
  are genuinely gone and the detector reports exactly that: 5 missed.
* `extra_peaks` (a superimposed ~1.8× oscillation, e.g. flickering light or
  tremor) → the detector latches onto the oscillation: 10 false beats,
  precision 0.66. **This is the mechanism that produces "irregular intervals"
  in a real recording without any physiological irregularity.**
* `noisy` (noise power above pulse power) → SNR 5.6 dB, the pulse is only
  marginally recoverable: category A.
* `motion` (respiratory wander + a noise burst) → the pulse is still fully
  recovered (sensitivity 1.00, SNR 20.5 dB) but the acquisition environment
  degrades the measurement: category C.

**Conclusion for the detector:** on signals that actually contain a pulse, the
production peak detectors are accurate. Their error is confined to
(i) signals with no pulse (they report beats from noise), and (ii) signals
where a strong non-cardiac oscillation competes with the pulse.

## 5. Part 2 — Real recordings (rPPG-10, 27 subjects, ECG reference)

The rPPG-10 dataset in this repository ships **synchronised ECG**
(`Subject_X_ECG.npy`, 1000 Hz, 600 000 samples = 600 s) next to three 30 fps
64×64 ROI videos of the same subject (`Subject_X_Forehead_.avi`,
`Subject_X_Cheek1_.avi`, `Subject_X_Cheek2_.avi`, 18 000 frames = 600 s). A
real reference therefore exists — **no reference data was invented**.

**Offset caveat (important).** The dataset does not publish the ECG↔video
start offset; the rPPG-10 paper quotes ±500 ms synchronisation uncertainty.
Every beat-level number below is therefore computed at a **searched** offset
and is a *hypothesis*, not a verified synchronisation. The HR-trace comparison
(much weaker than a beat match) is unaffected by a constant offset and is the
more trustworthy of the two.

### 5.1 Whole-dataset sweep

27 subjects × 3 ROI videos = **78 ROI analyses** (`validation_output/sweep_summary.md`,
`sweep_summary.csv`, and one markdown report per subject).

**Verdict distribution**

| verdict | count | meaning |
| --- | --- | --- |
| A | 76 | genuinely poor signal quality (all with acquisition-side contributors) |
| B | 2 | peak-detection failure |
| C | 0 | preprocessing/ROI artifact with a still-usable pulse |
| D | 0 | inconclusive (no case without a reference) |

**Metric ranges (min / median / max over the 78 ROIs)**

| metric | min / median / max |
| --- | --- |
| SNR (dB) | −1.63 / −0.07 / 7.72 |
| spectral concentration | 0.06 / 0.08 / 0.31 |
| ACF regularity | 0.00 / 0.06 / 0.37 |
| low-frequency / cardiac power ratio | 0.88 / 7.23 / 138.89 |
| ECG beat sensitivity | 0.37 / 0.43 / 0.67 |
| ECG beat precision | 0.36 / 0.48 / 0.61 |
| ECG mean HR (BPM) | 57.4 / 81.6 / 102.6 |
| ECG inter-beat CV (physiological) | 0.04 / 0.08 / 0.24 |
| Detector IBI CV (as measured) | 0.26 / 0.28 / 0.29 |
| Production FFT BPM | 60.0 / 120.0 / 144.0 |
| Detector beat-implied BPM | 66.8 / 70.6 / 72.9 |
| Production legacy regularity (%) | 64.7 / 66.6 / 69.0 |
| Production posterior regularity (%) | 1.4 / 7.3 / 25.4 |
| Production legacy SQI | 37.8 / 42.3 / 93.2 |
| Production posterior SQI | 0.0 / 0.0 / 0.9 |

**Offset-independent check — the production HR trace vs the ECG HR trace**
(this comparison does not depend on the ECG↔video offset at all):

| ROI | ECG mean HR | video-vs-ECG HR MAE | bias | Pearson r | searched beat offset |
| --- | --- | --- | --- | --- | --- |
| Subject 1, forehead | 57.4 | 33.09 BPM | +32.45 | 0.064 | +1.60 s |
| Subject 1, cheek 1 | 57.4 | 37.40 BPM | +36.82 | 0.092 | +1.60 s |
| Subject 5, cheek 2 | 81.7 | 26.48 BPM | +16.37 | 0.075 | −3.15 s |
| Subject 9, forehead | 90.9 | 24.43 BPM | +3.35 | −0.083 | +0.20 s |
| Subject 13, forehead | 67.7 | 27.08 BPM | +23.76 | −0.044 | +1.15 s |

The production FFT HR trace has essentially **no correlation** with the ECG
HR trace (r ≈ 0) and overestimates the rate by 3-37 BPM. Note also that the
searched beat offsets differ from subject to subject (+1.60, −3.15, +0.20,
+1.15 s) — there is no common offset, which is further evidence that the
searched offsets are fit artefacts rather than a property of the dataset.

### 5.2 Subject 1, in detail

Full report: `validation_output/subject_1_report.md`.

**ROI `forehead` — verdict A: genuinely poor signal quality (acquisition-side
contributors present), confidence high**

```
- SNR=-0.07 dB, spectral concentration=0.074, ACF regularity=0.229 (peak 0.265 @ 60.0 BPM)
- legacy detector: 676 peaks, IBI CV=0.267, implied BPM=67.6; FFT BPM=120.0
- posterior detector: 774 peaks, IBI CV=0.311; regularity legacy=68.0% posterior=14.8%
- motion proxy: frame-diff mean=0.1745 p95=0.6875; low-frequency/cardiac power
  ratio=1.529; exposure drift=n/a; brightness mean=103.8 std=2.1;
  saturated=0.000; flat=0.000
- ground truth: 574 true beats, 676 detected, matched=341, missed=233,
  false=335, sensitivity=0.594, precision=0.504, mean |interval error|=0.0720 s
```

Subject-level reference (`validation_output/subject_1_report.md`, notes):

```
- ECG reference: Subject_1_ECG.npy - 574 R-peaks, mean HR 57.4 BPM,
  SDNN 103.6 ms, ECG inter-beat CV 0.099.
- Detector IBI CV across ROIs: 0.267-0.311 (ECG inter-beat CV 0.099).
- Production FFT BPM: [120.0, 120.0, 120.0]; detector beat-implied BPM:
  [67.6, 69.1, 69.9]; ECG mean HR 57.4 BPM.
```

Read together:

* the ECG's own rhythm on this recording has an inter-beat CV of **0.099**;
* the detector reports an IBI CV of **0.267-0.311** on the same recording —
  **2.7-3.1× the physiological irregularity**;
* the two production detectors disagree with each other (676 vs 774 peaks,
  77 vs 68 BPM implied);
* and the production FFT says **120 BPM** where the ECG says **57.4 BPM**.

None of these numbers is a statement about the subject's heart. They are
statements about a detector running on a 64×64 crop that does not carry a
usable pulse.

## 6. Findings

### A. Genuinely poor signal quality — **the dominant finding on this dataset**

76 of the 78 ROI analyses of the 27-subject sweep fall in category A. The ROI
videos of rPPG-10 carry a measurable pulse, but it sits at or below the noise
floor *after the production preprocessing chain*: SNR −1.63 … +7.72 dB
(median −0.07), spectral concentration 0.057 … 0.312 (median 0.08), ACF
regularity 0.00 … 0.372 (median 0.06). Scored against the subject's ECG, the
detector's beats reach only 0.374 … 0.670 sensitivity and 0.365 … 0.608
precision — roughly half of the beats it reports are not in the ECG, and more
than half of the ECG beats are never found.

This is **not** a peak-detector bug: the same detector scores 1.00 / 1.00 on
the synthetic `clean` control. The signal simply does not carry enough
cardiac information for a reliable beat stream.

### B. Peak-detection failure — **confirmed as a mechanism, and demonstrated on the two ROIs where the signal is good enough to judge**

Three independent pieces of evidence:

1. **Synthetic `extra_peaks`** — a superimposed oscillation produces 10 false
   beats in 36 detected (precision 0.66) with a strong underlying pulse
   (SNR 22.6 dB). This is the classic recipe for a "low regularity / high
   BPM" reading.
2. **The two category-B ROIs** (Subject 13, SNR 6.26 dB; Subject 25,
   SNR 7.72 dB) are precisely the recordings where the signal is good enough
   for the detector to be judged — and there the detector still disagrees with
   the ECG (sensitivity 0.496 / 0.670, precision 0.495 / 0.608). Where the
   signal is usable, the beats are still wrong.
3. **Real recordings at large** — the detector reports 668-728 beats where the
   ECG has 574-1026, with 254-410 of them matching, and its beat-implied rate
   (66.8-72.9 BPM, median 70.6) sits far below the ECG mean rate (median
   81.6 BPM). The extra beats are not physiology; they are the detector firing
   on noise and on the second harmonic of the pulse.

The two production detectors also disagree with each other by 10-20 % on the
same input (e.g. 676 vs 774 peaks on Subject 1 forehead) — itself a detector
instability signal.

### C. Preprocessing / ROI artifact — **present, and the actionable upstream cause**

Category C is the right home for a recording in which a usable pulse survives
but the environment degrades it (the synthetic `motion` case is the reference
example: sensitivity 1.00, SNR 20.5 dB, but a low-frequency/cardiac power
ratio of 0.59).

On the real rPPG-10 ROI crops the acquisition-side indicators are also
degraded — the low-frequency / cardiac power ratio is **0.88 … 138.9 (median
7.2)**, i.e. the channel is dominated by slow illumination change and noise
rather than by the pulse — but there the signal is simultaneously unusable, so
the verdict is A with the acquisition indicators reported as contributors.

The actionable lever is therefore the **acquisition**, not the detector:

* the ROI is a 64×64 crop (the whole frame is treated as the ROI — no face
  localisation, no sub-region selection);
* the recordings are 10-minute, mostly static captures in which a tiny
  perfusion change has to be separated from compression noise, illumination
  drift and sensor noise;
* the cardiac band ends up with ~0 dB SNR *after* detrend, exposure-trend
  removal and respiratory notch suppression have already removed what they
  can.

### D. Inconclusive — the cases that need a reference sensor

In the sweep itself no ROI landed in D, because every rPPG-10 ROI has an ECG
reference to be judged against. D is the verdict for recordings **without** a
reference, which is the normal case for a live session:

* A **live session** (no `raw_signals.csv` export exists in the repository
  yet) has no ground truth, so every such ROI is category D by construction.
  A worked example on a 60 s excerpt of Subject 1's forehead is included as
  `validation_output/raw_signals_demo.csv` (verdict: A, confidence medium —
  the signal itself is unusable, but without a reference no beat-level
  statement is possible).
* Any ROI whose signal is marginal *and* whose detection disagrees with the
  reference is reported as "B (signal marginal)" with **low** confidence.
* Beat-level comparisons against the rPPG-10 ECG remain hypothesis-level
  because the start offset is unpublished — and the per-subject searched
  offsets are mutually inconsistent (+1.60, −3.15, +0.20, +1.15 s), so they
  cannot be treated as a dataset property. The HR-trace comparison does not
  depend on the offset, and is reported alongside it.

## 7. Two concrete, demonstrated defects worth noting

These were found by the audit and are **not** fixed here (no production
changes were made in this phase). They are reported so they can be scheduled.

### 7.1 The production FFT BPM estimate reports exactly 2× the real heart rate

`phase90_bpm_harmonic_audit.py` on Subject 1, forehead ROI:

```
window votes   : 119 windows of 10 s
  BPM histogram: 55:35, 60:40, 65:13, 70:7, 80:5, 85:8, 90:5, 100:2, 110:1, 115:3
voted peak     : 1.0000 Hz = 60.0 BPM (cluster 40/119 votes)
after _resolve_subharmonic: 2.0000 Hz = 120.0 BPM (changed=True)
  band energy at candidate 1.000 Hz : 4.991e+04
  band energy at double   2.000 Hz : 2.276e+04 (ratio 0.456, threshold 0.40)
ECG reference  : 574 R-peaks, mean HR 57.4 BPM
```

The estimator's **own** windowed vote is 60 BPM and the ECG says 57.4 BPM —
they agree. The final answer is 120 BPM because the "promote to the double"
branch of `rppg_core._resolve_subharmonic()` fires: the second harmonic
carries 45.6 % of the fundamental's energy, above the hard-coded 0.40
promotion threshold. In a noisy PPG the second harmonic routinely reaches
that level, so the reported BPM is doubled.

Across the 27-subject sweep the production FFT BPM is 60-144 BPM
(median **120**), while the ECG mean rate is 57-103 BPM (median **81.6**) and
the detector's own beat-implied rate is 66.8-72.9 BPM (median **70.6**).

The offset-independent cross-check agrees: the production HR trace versus the
ECG HR trace gives MAE 24-37 BPM with a positive bias of +3 to +37 BPM and a
Pearson correlation of −0.08 … +0.09 across the five ROIs spot-checked in
§5.1. The trace is essentially uncorrelated with the truth and biased high.

*This is not a property of the data*: the same estimator returns exactly
72.0 BPM on the synthetic 72 BPM pulse. A minimal, well-tested fix is needed
(e.g. only promote to the double when the fundamental is demonstrably weaker
than the noise floor, or cross-check the FFT peak against the beat-implied
rate), but changing live BPM output is a production decision that was out of
scope for this audit phase.

### 7.2 The legacy regularity metric is noise-blind

`compute_sqi()`'s `breakdown["regularity"]` reports **64.7-69.0 %** (median
66.6) on recordings whose ACF regularity is 0.06-0.37 and whose ECG-scored
precision is ≈ 0.4-0.5, while the ACF-based `PosteriorSQI` reports
**1.4-25.4 %** (median 7.3) on the same input. The legacy CV-based
regularity is computed over an IBI sequence that the detector produced from
noise; it cannot distinguish "irregular heart" from "irregular detector
output" and therefore must not be presented as a physiological quantity.

The decisive number is the direct comparison against the reference:

| quantity | median | range |
| --- | --- | --- |
| ECG inter-beat CV (physiological irregularity) | **0.08** | 0.04 - 0.24 |
| Detector IBI CV (what production reports) | **0.28** | 0.26 - 0.29 |

The detector reports ~3.5× the physiological irregularity, and the excess is
constant across subjects (0.26-0.29) regardless of how regular the ECG is.
**The "irregular intervals" are a property of the detector, not of the
recorded heart rhythm.**

## 8. Constraints honoured

* **No production file was modified.** The pre-existing local modifications
  (`rppg_core.py`, `rppg_sqi.py`, `rppg_config.py`, `rppg_main.py`,
  `tests/engine/test_motion_detector.py`, …) were left exactly as they were;
  `git status` shows only additions for this phase.
* No quality threshold was lowered and no production behaviour was altered.
* The diagnostic code lives outside the production tree and only *reads*
  production modules.
* No irregular detected interval is interpreted as evidence of an irregular
  human heartbeat — every report carries that caveat explicitly and the
  classifier emits it on every ROI.
* No reference data was invented: the ECG reference is the one shipped with
  rPPG-10, and its unverifiable offset is flagged everywhere it is used.

## 9. Known limitations

* The rPPG-10 ROI videos are 64×64 crops; the whole frame is treated as the
  ROI, so a true face-ROI extraction could change the SNR numbers.
* The ECG↔video offset is unverified; beat-level agreement numbers are
  hypothesis-level.
* The sweep covers 27 subjects; `Subject_4` ships **0-byte** videos and is
  skipped with a note (the CLI no longer aborts on it).
* The synthetic pulse train is a fundamental + 2nd harmonic, not a real
  PPG morphology; it is sufficient for detector scoring but not a substitute
  for physiological waveforms.
* The classifier thresholds (SNR 3/6 dB, ACF 0.15, spectral concentration
  0.10, LF/cardiac ratio 0.40) are documented constants of this diagnostic
  package, not production thresholds. Changing them changes the verdicts.
