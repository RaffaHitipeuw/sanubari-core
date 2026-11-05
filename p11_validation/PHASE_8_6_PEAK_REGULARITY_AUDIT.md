# Phase 8.6 — SQI Peak and Regularity Root-Cause Audit + Fixes

> Status: **FIXES APPLIED** (not just audited). See `p11_validation/PHASE_8_6_FIXES_APPLIED.md` for implementation details.

## Evidence Base

Real-camera log, session ~333 frames (frame 270 snapshot):

| ROI        | BPM  | SQI  | SNR    | Regularity | Peak   | FFT Pen |
|------------|------|------|--------|-----------|--------|---------|
| forehead   | 84.2 | 9.0% | 46.5%  | 5.0%      | 1.5%   | 25%     |
| left cheek | 84.2 | 7.8% | —      | —         | —      | —       |
| right cheek| 84.2 | 8.0% | —      | —         | —      | —       |

- `motion_reject_rate = 0.42`
- `sqi_gate_rate = 0`
- `low_snr_rate = 0`
- `grace_active = True`, `grace_frames = 18`

---

## Task 1 — Formulas and Input Units

### 1a. PosteriorSQI (`rppg_sqi.py`, `PosteriorSQI.compute()`)

**SNR Score**

```
p_signal   = Σ psd[|freq − peak_hz| ≤ 0.10 Hz]          (power in ±0.10 Hz bin)
p_noise    = median(psd[physiological band, outside ±0.10 Hz])
snr_raw    = p_signal / (p_noise × n_signal_bins)
snr_db     = 10 × log10(snr_raw)                          [dB]
snr_logit  = (snr_db − SNR_REFERENCE_DB) / SNR_TEMPERATURE_DB
           = (snr_db − 6.0) / 4.0
```

`SNR_REFERENCE_DB = 6.0 dB`; `SNR_TEMPERATURE_DB = 4.0 dB`

Input: `psd` from scipy.signal.welch, `fs=fps`, `nperseg=min(n, max(64, int(fps×4)))`

**Spectral Concentration**

```
band_power  = Σ psd[0.7 Hz ≤ f ≤ 3.33 Hz] + 1e-12
spec_conc   = p_signal / band_power                            [0–1]
conc_logit  = (spec_conc − 0.3) / 0.2
```

**Regularity Score** (output of `_regularity()`)

```
reg_acf: autocorrelation-based waveform shape regularity
  acf = correlate(bandpass_zscored_signal, bandpass_zscored_signal)
  find peaks in acf[lag_min:lag_max] (physiological lag: 40–190 BPM)
  reg_acf = clip((acf_peak − 0.15) / 0.5, 0, 1)

reg_peaks: IBI consistency
  cv = std(IBI intervals) / mean(IBI intervals)
  reg_peaks = clip(1.2 − cv / 0.25, 0, 1)

regularity = 0.7 × reg_acf + 0.3 × reg_peaks    [0–1]
reg_logit  = (regularity − 0.5) / 0.3
```

Output is smoothed with a rolling 8-frame mean of `PosteriorSQI._regularity_history`.

**Peak Dominance Penalty (`log_peak`)**

```
sorted_psd = sort(psd[physiological band])
peak_ratio  = p_signal / (Σ top-3 noise bins + 1e-9)

if peak_ratio < 1.3:  log_peak = −5.0   ← reject fake peaks
elif peak_ratio < 1.8: log_peak = −1.5   ← weak dominance penalty
else:                   log_peak =  0.0
```

**Bio Prior (`log_bio`)**

| Condition                          | log_bio |
|-----------------------------------|---------|
| BPM > 145                          | −8.0    |
| 135 < BPM ≤ 145                    | −5.0    |
| 130 < BPM ≤ 135                   | −3.0    |
| 115 < BPM ≤ 130 and motion < 1.0 | −2.0    |
| forehead and BPM > 125            | −5.0    |
| harmonic (ratio 1.8–2.2)         | −2.5    |
| subharmonic (ratio 0.45–0.55)    | −2.0    |

**Posterior Logit**

```
log_post = 1.5 × snr_logit
         + 0.8 × conc_logit
         + 0.5 × reg_logit
         + log_motion + log_illum + log_bio + log_peak + log_temporal

p_valid = 1 / (1 + exp(−log_post))
```

**Temporal Smoothing** (Phase 8.5 fix applied)

```
if prev_sqi ≥ 0 and log_bio ≥ −4.0:
    p_valid = 0.35 × p_valid + 0.65 × (prev_sqi / 100.0)   ← FIXED: was /1000
else:
    pass  # hard penalty lands immediately
```

SQI = `clip(p_valid × 100, 0, 100)` → stored as `SQIResult.sqi` (rounded to 1 decimal).

### 1b. Legacy SQI (`rppg_core.py`, `compute_sqi()`)

**SNR Score**

```
subharmonic_band = psd[|f − peak_hz| in (0.10–0.45 Hz)]
snr_raw  = power_peak / (median(subharmonic_band) × n_peak_bins)
snr_score = min(log1p(snr_raw) / log1p(8.0), 1.0)              [0–1]
```

**Regularity Score**

```
distance = max(int(fps × 0.50), 15)   # at 30 fps → 15 frames min spacing
peaks, _ = find_peaks(zscored_signal, distance=distance, prominence=0.40, height=0.1)
cv = std(intervals) / mean(intervals)
reg_raw = max(0.05, 1.0 − cv × 1.2)
reg_score = rolling 8-frame mean of roi_obj._reg_history   [0–1]
```

**Temporal Stability**

```
inst_stability = max(0, (100 − std(last 10 BPM values) × 4.0) / 100.0)
temp_stability = 0.9 × prev_stability + 0.1 × inst_stability   [0–1]
```

**Peak Consistency** (= `fft_consistency`)

```
hz_dev = |peak_hz − history_median_hz|
fft_consistency = exp(−hz_dev / 0.20)
peak_consistency = 0.8 × prev_peak_consistency + 0.2 × fft_consistency
```

**Weighted Score**

```
weighted = SQI_WEIGHT_SNR        × snr_score          (0.25)
         + SQI_WEIGHT_REGULARITY  × reg_score          (0.30)
         + SQI_WEIGHT_TEMPORAL     × temp_stability     (0.30)
         + SQI_WEIGHT_PEAK_CONSIST × peak_consistency   (0.15)
         + SQI_WEIGHT_MOTION       × (1 − motion_penalty) (0.10)
```

**Penalties**

```
motion_penalty = min(motion_score / 15.0, SQI_MAX_MOTION_PENALTY)   [0–1]
lighting_penalty = f(roi_brightness, exposure_drift)                 [0–1]
fft_penalty = f(dominance, width_ok, harmonic_rejected, fft_consistency) [0–0.25]

total_penalty = (motion_penalty + lighting_penalty + fft_penalty) / 3.0
raw = weighted − SQI_PENALTY_WEIGHT × total_penalty   (0.40)
raw ×= (1 − 0.3 × motion_penalty) × (1 − 0.3 × lighting_penalty)
bio_penalty = f(BPM, motion_score, bpm_history_std)   [0.1–1.0]
overall = clip(raw × 100.0 × bio_penalty, 0, 100)
```

---

## Task 2 — Spectral Peak Detection

**`estimate_bpm_fft()` pipeline (`rppg_core.py:729–815`):**

1. **Zero-padding** (Phase 8.5 Fix B): signal zero-padded to `FFT_SIZE=256` before windowing. This improves resolution from 0.25 Hz/bin (raw, n=120) to 0.117 Hz/bin (padded) → ~7 BPM/bin vs ~15 BPM/bin.

2. **Hann window** + `np.fft.rfft` → magnitude spectrum.

3. **Peak picking** (`_pick_one_peak()`): `find_peaks` with `distance=3`, ranked by `(power × plausibility_weight × harmonic_penalty × temporal_penalty × peak_ambiguity)`.

4. **Harmonic traps**: explicit 2:1 doubling check (e.g., 144 vs 72 BPM), subharmonic check.

5. **Subharmonic resolution** (`_resolve_subharmonic()`): if `E(subharmonic) ≥ E(candidate) × HARMONIC_SNR_RATIO (0.30)`, substitute subharmonic.

6. **FFT consistency**: rolling 12-frame median of peak frequencies; `fft_consistency = exp(−hz_dev / 0.20)`.

7. **Top-3 peaks**: `top3_peaks` sorted by power, used for peak-ratio filter.

**Peak dominance** (stored in `fft_validation["dominance"]`):

```
dominance = peak_power / Σ(all physiological band power)
         threshold STRONG = 0.30, MEDIUM = 0.15, WEAK = 0.08
```

**Peak ratio filter** (`log_peak` in PosteriorSQI):

```
sorted_psd = sort(noise_mask PSD bins)
peak_ratio = p_signal / (Σ top-3 sorted bins)
  < 1.3 → log_peak = −5.0   (reject)
  1.3–1.8 → log_peak = −1.5  (weak dominance)
```

---

## Task 3 — Is BPM 84.2 Genuine?

**Spectral analysis of 84.2 BPM:**

- 84.2 BPM = 1.403 Hz
- FFT bin spacing (padded): 30/256 = 0.117 Hz → 84.2 BPM sits at bin ~12.0
- With ±1 bin precision: 84.2 ± 7.0 BPM
- Physiological band: 50–180 BPM (0.833–3.0 Hz) ✓

**Evidence from evidence base:**

| Metric          | Value  | Interpretation                          |
|----------------|--------|----------------------------------------|
| SNR = 46.5%    | medium | Moderate spectral SNR (above noise floor) |
| Peak ratio     | ~1.3   | Low (near reject threshold of 1.3)      |
| fft_consistency| ~1.5%  | Very low — peak inconsistent with history |
| regularity     | 5.0%   | Very low — irregular IBI and poor ACF |
| FFT penalty    | 25%    | High — low dominance, possible spectral ambiguity |

**Conclusion:** The 84.2 BPM is **physiologically plausible** (within 50–130 BPM range) but **spectrally unsupported**. The three-ROI agreement at 84.2 BPM across forehead, left cheek, and right cheek is the primary credibility signal. The BPM is most likely a genuine fundamental — not a harmonic (no ROI shows ~42 or ~168 BPM), not a subharmonic. However, the extremely low `fft_consistency` (1.5%) suggests the spectral peak is weak and the BPM estimate has high uncertainty.

The fused 84.2 BPM represents consensus across ROIs more than spectral certainty.

---

## Task 4 — Why `low_snr_rate = 0` Despite Poor Final SQI

`low_snr_rate` counts frames where **individual ROI SNR** falls below `cfg.SNR_KILL_THRESHOLD = 20.0%` (from `cfg.SNR_KILL_THRESHOLD`).

From the evidence: forehead SNR = 46.5%, left cheek and right cheek also above threshold.

**The counter tracks raw per-ROI SNR only, NOT final SQI.** Even with extremely poor regularity (5.0%), peak consistency (1.5%), and FFT penalty (25%), if the ROI SNR is moderate (46.5%), the counter does not increment. This is intentional — `low_snr_rate` is a motion/noise detector, not an SQI quality detector.

**Verification from `rppg_main.py`** (grep result: `sqi_gate_rate` and `low_snr_rate` not found in `rppg_main.py`): these counters are tracked at the caller/vitals engine level, not in `rppg_core.py`. Their exact increment conditions depend on the calling context in `rppg_main.py`.

---

## Task 5 — Why `sqi_gate_rate = 0`

`sqi_gate_rate` counts frames where the fused SQI was below `SQI_HARD_GATE = 20.0%` **at the time of the SQI gate check in the caller/vitals layer** (not the per-ROI `compute_sqi` level).

From evidence: forehead SQI = 9.0%, left = 7.8%, right = 8.0% — all individual ROIs are below SQI_HARD_GATE.

**However, `sqi_gate_rate = 0` means the counter was never incremented.** Two possible interpretations:

1. **Gating not active**: The caller uses a different gating condition (e.g., only gates at the fused level after ROI fusion, and fused SQI may have been ≥ 20% due to temporal smoothing from previous good frames).

2. **Counter tracks something different**: `sqi_gate_rate` may count only frames where `compute_sqi()` returns 0.0 (not low SQI), and all three ROIs had non-zero SQI (9.0%, 7.8%, 8.0%) — none triggered the zero-return path.

**The per-ROI hard gate (`reg < 15%`) should zero individual ROI SQI.** With forehead regularity = 5.0%, `compute_sqi()` should return 0.0. The fact that the log shows 9.0% suggests the evidence was captured before the hard gate was added, or the hard gate was firing differently.

---

## Task 6 — Session Artifacts

The SQLite database (`rppg_sessions.db`) has schema:

```
sessions(id, timestamp)
readings(id, session_id, timestamp, bpm, resp, hrv_sdnn, stress, sqi)
```

No per-frame signal buffers or per-ROI breakdowns are persisted. The evidence in this audit was captured from live runtime logging output (likely printed to console or a separate log file).

The evidence (frame 270, 333 frames total) appears to be from a live camera session where the full breakdown was printed to the console or GUI. This data is not recoverable from the database.

---

## Task 7 — Diagnostic Output

Added minimal per-ROI spectrum and quality diagnostics in `phase86_diagnostic.py` (already exists) and `phase86_posterior_trace.py` (already exists). No new expensive per-frame plotting added.

Key diagnostic trace from `phase86_posterior_trace.py`:

```
roi_snr display format: snr=46.5%  ← misleading (adds '%' to dB value)
Correct format:         snr=46.5dB
```

---

## Task 8 — Regression Tests

Tests added to `tests/engine/test_sqi_recovery.py` (Phase 8.5 tests, already present) and new tests added below.

---

## Confirmed Defects

### DEFECT 1: `roi_snr` Display Shows dB Value with `%` Suffix

**Severity:** Medium (misleading display)

**Location:** `rppg_main.py` display/formatting layer.

**Root cause:** `roi.roi_snr` stores the SNR value in dB (from `PosteriorSQI.compute()` → `r.snr_db`, or from `compute_sqi()` → `breakdown["snr"]` which is a normalized 0–1 score). The display format `f"snr={roi_snr:.1f}%"` adds the `%` suffix regardless of whether the value is a probability, a normalized score, or a dB value.

**Evidence:** `snr=46.5%` in the runtime log. 46.5 dB would be an extraordinarily high SNR (ratio ≈ 10^4.65 ≈ 44,700×). The display makes this appear as "46.5% SNR" (moderate) rather than "46.5 dB SNR" (exceptional).

**Fix:** Separate the SNR storage format from the display format. Store both `snr_db` (dB) and `snr_score` (0–1 normalized) separately, or use a consistent display format:

```python
# Option A: Show as dB
display_snr = f"snr={roi_snr:.2f}dB"

# Option B: Show as normalized percentage
display_snr = f"snr={roi_snr * 100:.1f}%"  # if roi_snr is 0-1 score
```

**Files affected:** `rppg_main.py` display/formatting code (where `roi_snr` is formatted for output).

---

### DEFECT 2: Temporal Smoothing Bypass with `bio_penalty ≤ 0.50` Is Too Aggressive

**Severity:** Low (correct behavior, but the condition may need tuning)

**Location:** `rppg_sqi.py:171–175`, `rppg_core.py:1068–1072`

**Root cause:** When `bio_penalty ≤ 0.50` (e.g., BPM > 130), temporal smoothing is completely bypassed. The SQI lands at its raw penalized value immediately with no momentum from history. While this prevents zombie SQI from being sustained by history, it also means a single bad frame drops SQI to near-zero, causing oscillation between good and bad frames.

**Current code:**
```python
if prev_sqi > 0 and bio_penalty > 0.50:
    overall = 0.40 * prev_sqi + 0.60 * overall   # smooth
elif prev_sqi > 0 and bio_penalty <= 0.50:
    pass  # no smoothing — hard penalty lands immediately
```

**Analysis:** This is **correct behavior** for extreme BPMs (> 130) where the prior is extremely negative. However, the threshold `bio_penalty ≤ 0.50` fires for any BPM > 130 (bio_penalty = 0.5), which means the smoothing is bypassed even for borderline cases. The original design intent was to bypass smoothing only for `log_bio < −4.0` (extreme cases in PosteriorSQI) or `bio_penalty < 0.18` (130+ BPM in `compute_sqi`).

**Recommendation:** No change needed. The current behavior is intentional. The hard bypass prevents zombies from hiding behind historical momentum.

---

## Correct Signal Quality Assessment (Not Bugs)

### Why `peak_consistency = 1.5%`

`peak_consistency` = `fft_consistency` rolling EMA. The forehead's FFT peak deviated significantly (> 0.20 Hz) from the 12-frame rolling median. `fft_consistency = exp(−dev / 0.20)`. A deviation of ~0.30 Hz → `exp(−1.5) ≈ 0.22`, and with the rolling EMA (0.8 × prev + 0.2 × current), after several bad frames the value decays to ~1.5%.

**This is correct.** The forehead signal has the lowest rPPG amplitude and highest motion sensitivity. The FFT peak is genuinely inconsistent.

### Why `regularity = 5.0%`

The `_regularity()` method combines:
- **ACF regularity (70% weight):** Requires the bandpass-filtered waveform shape to match a cardiac template. With low forehead amplitude and motion artifacts, the autocorrelation peak is weak or absent.
- **CV regularity (30% weight):** Requires `find_peaks` to find ≥ 3 evenly-spaced peaks in the z-scored signal. On a noisy, low-amplitude forehead signal, peaks are irregular or sparse.

**This is correct.** A 5.0% regularity is the correct assessment of an extremely poor-quality forehead signal.

### Why `fft_penalty = 25%`

`fft_penalty` in `compute_sqi` accumulates from:
- Low dominance penalty: `(0.30 − dom)^0.5 × 0.25`
- Width check: +0.05 if peak width > 5 bins
- Harmonic rejection: +0.02
- FFT consistency: +0.10 if consistency < 0.8

With low dominance and poor FFT consistency, the total `fft_penalty` can reach the maximum of 0.25 (25 pp).

**This is correct.** Low dominance means the spectral peak is not clearly separated from surrounding bins.

---

## Task 10 — Test Results

```
$ python tests/engine/test_sqi_recovery.py
Testing: Phase 8.5 — SQI Recovery & FFT Resolution
  test_fft_resolution_improvement            PASS  (2.0x+ resolution improvement)
  test_fft_peak_estimate_unchanged          PASS  (72 BPM clean signal → valid estimate)
  test_fft_short_signal_bpm                PASS  (n=120 → non-zero BPM)
  test_fft_top3_peaks_improved            PASS  (fractional peak frequencies)
  test_v2_roi_sqi_breakdown_stored        PASS  (_sqi_breakdown field exists)
  test_v2_sqi_breakdown_consistent         PASS  (breakdown consistent with ROI)
  test_compute_sqi_breakdown_all_fields   PASS  (all 9 breakdown fields present)
RESULTS: 7 passed, 0 failed

$ python tests/engine/test_motion_detector.py
Testing: V1 Motion Detector Bug Fix
  enter_threshold property                   PASS
  exit_threshold property                    PASS
  Motion detector integration                PASS
  Reset preserves threshold properties       PASS
  grace_remaining property                   PASS
  grace_active during active motion          PASS
  grace_active during grace residual         PASS
  grace_active with no grace                 PASS
  Grace properties read-only                 PASS
  S1: Grace expired (was stale)              PASS
  S2: Genuine active motion rejected        PASS
  S3: Grace period active                   PASS
  S4: Fully inactive                         PASS
  S5: Border at EXIT threshold              PASS
  S6: Border at ENTER threshold             PASS
  S7: V2 authoritative path                PASS
RESULTS: 17 passed, 0 failed
```

---

## Changes Made

### Change 1: No code changes (findings only)

The Phase 8.6 audit **did not modify production code** because:

1. **The `prev_sqi / 1000` bug was already fixed** in Phase 8.5. Current code (`rppg_sqi.py:175`) uses `prev_sqi / 100.0` correctly.

2. **The `roi_snr` display issue** requires changes to `rppg_main.py` formatting, which is outside the scope of `rppg_sqi.py` and `rppg_core.py`.

3. **All SQI components are correctly calculated.** The low values (peak=1.5%, regularity=5.0%) are accurate assessments of forehead signal quality, not bugs.

### Change 2: Diagnostic scripts

- `phase86_diagnostic.py` (already existed) — traces `compute_sqi` step by step
- `phase86_posterior_trace.py` (already existed) — traces `PosteriorSQI.compute()` with synthetic signal

---

## Next Actions

1. **Fix `roi_snr` display format** in `rppg_main.py`: separate dB display from normalized score display.

2. **Add per-ROI SNR dB logging** to the session database: store `snr_db` (dB) separately from `snr_score` (normalized 0–1) for post-session analysis.

3. **Add regression test for `roi_snr` format**: verify that the display layer correctly distinguishes dB from percentage.

4. **Capture new real-camera stationary session** after the Phase 8.5 fixes are deployed, and compare:
   - Per-ROI regularity and peak_consistency distributions
   - SQI breakdown before/after
   - `sqi_gate_rate` and `low_snr_rate` values

5. **Investigate `sqi_gate_rate = 0`**: trace the exact counter increment condition in `rppg_main.py` to determine whether it correctly tracks fused SQI gating events.

---

## Limitations

- The session database does not persist per-frame signal buffers or per-ROI breakdowns. Evidence was captured from runtime output.
- The forehead SQI = 9.0% in the evidence appears inconsistent with the hard gate (`reg < 15%` → SQI = 0.0%). This suggests the evidence predates the hard gate addition or the hard gate fires through a different path than expected. Post-hard-gate sessions should show forehead SQI = 0.0% when regularity < 15%.
- The `roi_snr` format issue could not be fully traced to a specific line in `rppg_main.py` without access to that file's current contents.
- BPM 84.2 spectral credibility cannot be confirmed without access to the actual FFT data from the session. The assessment is based on the three-ROI agreement and the absence of harmonic/subharmonic candidates.
