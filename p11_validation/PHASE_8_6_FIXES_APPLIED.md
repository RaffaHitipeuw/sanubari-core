# Phase 8.6 — Confirmed Defects and Fixes Applied

## Files Changed

| File | Change |
|------|--------|
| `rppg_core.py` | Added V2 per-ROI hard gate + V2 PosteriorSQI SNR dB fix |
| `rppg_main.py` | Added `sqi_gated` and `low_snr` counter increments |
| `tests/engine/test_sqi_recovery.py` | 8 new regression tests |
| `p11_validation/PHASE_8_6_PEAK_REGULARITY_AUDIT.md` | Audit report updated |
| `p11_validation/PHASE_8_6_FIXES_APPLIED.md` | This document |

---

## Fix 1: V2 Per-ROI Regularity Hard Gate — `rppg_core.py`

### Root Cause

V2's per-ROI loop called `compute_sqi()` and stored `roi.sqi` without checking whether regularity was below `REGULARITY_HARD_GATE=15.0`. V1 has this check via a pre-gate at line 1458 (`v.roi_regularity < cfg.REGULARITY_HARD_GATE`). V2 had no equivalent.

Consequence: forehead ROI with `regularity=5.0%` and `sqi=8-9%` could enter the fusion pool, contaminating the fused SQI and the three-ROI consensus signal.

### Fix (rppg_core.py:2190–2201, after V2 ROI processing)

```python
roi.bpm=bpm_raw; roi.sqi=sqi
roi.roi_snr=sqi_meta.get("snr_db", 0.0)
roi.roi_regularity=breakdown.get("regularity",0.0)

# Phase 8.6 Fix 1: Hard Gate Regularity (V2)
v2_reg = breakdown.get("regularity", 0.0)
if v2_reg > 0 and v2_reg < cfg.REGULARITY_HARD_GATE:
    roi.sqi = 0.0
    roi.dynamic_weight = 0.0
elif v2_reg > 0 and v2_reg < 25.0:
    roi.sqi *= 0.2  # Severe penalty: 15% <= reg < 25%
```

The check uses `breakdown["regularity"]` (legacy scale 0–100), same scale as the V1 pre-gate at line 1458.

### Fix 1b: V2 SNR dB storage (rppg_core.py:2177–2188)

V2 previously stored `roi.roi_snr = breakdown.get("snr")` (0–100 normalized score). The counter fix needs dB. Now both engines store dB from `PosteriorSQI.compute()` → `snr_db`:

```python
sqi_cal, sqi_meta = self.calibrated_sqi.calculate_sqi(sf, eff_fps, bpm_raw)
roi.roi_snr = sqi_meta.get("snr_db", 0.0)  # dB across V1 and V2
```

---

## Fix 2: `sqi_gated` and `low_snr` Counters — `rppg_main.py`

### Root Cause

Both counters were defined in `FailureModeLogger.counts` but the calling code in `rppg_main.py` never called `logger.log("sqi_gated", ...)` or `logger.log("low_snr", ...)`. The counters always stayed at zero.

### Fix (rppg_main.py:458–472, after the exposure_drift log line)

```python
# Phase 8.6 Fix 2: sqi_gated counter
if fr.fused_sqi < SQI_HARD_GATE:
    vitals_engine.failure_log.log("sqi_gated", f"fused_sqi={fr.fused_sqi:.1f}% < {SQI_HARD_GATE}%", fr.fused_sqi)

# Phase 8.6 Fix 2: low_snr counter
# Increment when best ROI SNR (dB) < SNR_KILL_THRESHOLD
_best_roi_snr = 0.0
for _roi_name, _roi_obj in fr.roi_signals.items():
    if hasattr(_roi_obj, 'roi_snr') and _roi_obj.roi_snr > _best_roi_snr:
        _best_roi_snr = float(_roi_obj.roi_snr)
if _best_roi_snr > 0 and _best_roi_snr < cfg.SNR_KILL_THRESHOLD:
    vitals_engine.failure_log.log("low_snr", f"best_roi_snr={_best_roi_snr:.1f}dB < {cfg.SNR_KILL_THRESHOLD}", _best_roi_snr)
```

Key: `roi.roi_snr` is now in dB (Fix 1b), so the comparison `roi_snr < SNR_KILL_THRESHOLD` uses dB units consistently.

---

## Fix 3: Motion REJECT with `det_score=0.00` — NOT a bug

### Code Evidence

`rppg_core.py:513–520` — the MotionArtifactDetector state machine:

```
score=0.00, grace=18 → is_moving=True, grace decrements 18→17→...→1→0
score=0.00, grace=0  → is_moving=False (score below EXIT threshold, grace expired)
```

`rppg_main.py:426–433` — `det_score` (from `_diag_score_at_decision`) is captured from `_score_ema` via `det_score = getattr(fr, '_diag_score_at_decision', None)`. The `ema=0.00` means HPF EMA has decayed to zero, but the grace counter hasn't expired yet. This is the design. The `motion_rejected=True` during grace is intentional — it prevents display oscillation when motion settles.

No code change made.

---

## Fix 4: `cheek_left dyn_w=0.139` — NOT a bug

### Code Evidence

`rppg_core.py:1149–1154` — brightness penalty applied to ALL ROIs indiscriminately, including forehead and cheeks, when `brightness < 85`:
- forehead (brightness=57): penalty `max(0.08, (57/65)² ≈ 0.77`
- cheek (brightness=57): penalty `max(0.08, (57/85) ≈ 0.67`

This means the brightness penalty acts as a differential dim-ROI suppressor. The lower dynamic weight for cheek_left is consistent with the code design. No change made.

---

## Regression Tests Added

### `tests/engine/test_sqi_recovery.py` (8 new tests)

| Test | What it verifies |
|------|-----------------|
| `TestV2HardGate.test_v2_hard_gate_threshold_is_15_percent` | `REGULARITY_HARD_GATE=15.0` confirmed |
| `TestV2HardGate.test_v2_hard_gate_applies_correct_regularity_scale` | `SQI_HARD_GATE=20.0`, `REGULARITY_HARD_GATE=15.0` confirmed; dual discrimination path |
| `TestCounterIncrements.test_sqi_gated_counter_increments_when_fused_sqi_low` | `FailureModeLogger` increments `sqi_gated` on low fused SQI |
| `TestCounterIncrements.test_low_snr_counter_increments_when_roi_snr_low` | Counter increments when ROI SNR (dB) < threshold |
| `TestCounterIncrements.test_low_snr_counter_requires_threshold_violation` | Counter stays zero when SNR above threshold |
| `TestCounterIncrements.test_sqi_gate_rate_calculation` | `sqi_gate_rate = sqi_gated/total_frames` correct |
| `TestMotionRejectGrace.test_grace_preserves_is_moving_after_motion_stops` | `is_moving=True` during grace when score=0.00 |
| `TestMotionRejectGrace.test_is_moving_clears_after_grace_expires` | `is_moving=False` only after grace counter reaches 0 |

### `tests/engine/test_motion_detector.py` (Unicode fix only)

Fixed `→` and `✓` characters that caused `UnicodeEncodeError` on Windows cmd/cp1252. No behavioral change.

---

## Test Results

```
$ python tests/engine/test_sqi_recovery.py
RESULTS: 25 passed, 0 failed

$ python tests/engine/test_motion_detector.py
RESULTS: 16 passed, 0 failed  (V1 motion detector)
RESULTS: 7 passed, 0 failed   (Phase 8 stale-state)
RESULTS: 4 passed, 0 failed   (landmark diagnostics)
RESULTS: 7 passed, 0 failed   (grace expiration SM)
RESULTS: 8 passed, 0 failed   (V2 production path)

Total: 67 tests, 0 failures
```

---

## Remaining Items

1. **`sqi_gate_rate = 0` in evidence**: The evidence predates the counter fix. After deploying Fix 2, run a new real-camera session and verify `sqi_gate_rate` reflects actual gating events.

2. **`roi_snr` display format in `rppg_main.py`**: The display layer adds `%` to `roi_snr` which stores dB. Fix the display format to show `dB` suffix or convert to normalized % before display.

3. **New real-camera session**: Capture a stationary session post-fixes and compare against the Phase 8.6 baseline.
