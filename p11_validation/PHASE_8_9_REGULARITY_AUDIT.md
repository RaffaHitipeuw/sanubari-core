# Phase 8.9 — ROI Regularity Root-Cause Audit: Final Report

> **Status:** AUDIT COMPLETE — no production code changes required.

## 1. Raw Regularity Metric and Units

The system uses **two independent regularity metrics** (different formulas, different purposes):

### Metric A — Legacy (compute_sqi, `rppg_core.py:880–897`)

| Property | Value |
|---|---|
| Formula | `reg_raw = max(0.05, 1.0 - cv × 1.2)` |
| Input | IBI intervals from `find_peaks(zscored_signal)` |
| Peak distance | `max(int(fps × 0.50), 15)` frames |
| Peak prominence | 0.40 |
| Range | `[0.05, 1.0]` (dimensionless normalized score) |
| Floor | **0.05 (= 5.0%)** when `cv ≥ 0.7917` or `peaks < 3` |
| Branches | `peaks ≥ 3` → CV-based; `peaks = 2` → 0.25; `peaks < 2` → 0.10 |
| History smoothing | 8-frame rolling mean of `roi._reg_history` |
| Used in | `breakdown["regularity"]`, V2 display, V2 hard gate |

### Metric B — PosteriorSQI (`rppg_sqi.py:197–262`)

| Property | Value |
|---|---|
| Formula | `regularity = 0.7 × reg_acf + 0.3 × reg_peaks` |
| reg_acf | ACF peak in physiological lag (40–190 BPM range), clipped `(peak−0.15)/0.5` |
| reg_peaks | IBI CV in `[0,1]`: `clip(1.2 − cv/0.25, 0, 1)` |
| Range | `[0.0, 1.0]` |
| History | 8-frame rolling mean of `PosteriorSQI._regularity_history` |
| Logit transform | `(regularity − 0.5) / 0.3` then `0.5 × reg_logit` weight in posterior |
| Used in | `sqi_meta["regularity_score"]`, PosteriorSQI posterior calculation |

---

## 2. Normalization Formula

**Legacy (display):** `display_pct = reg_score × 100`
- `reg_score` = mean(`roi._reg_history`) ∈ [0.05, 1.0]
- Display: `f"{reg_score * 100:.1f}%"` → e.g., `5.0%`

**PosteriorSQI (SQI weight):** `reg_logit = (regularity − 0.5) / 0.3`
- Then `REGULARITY_WEIGHT × reg_logit` where `REGULARITY_WEIGHT = 0.5`
- Final SQI: `1 / (1 + exp(−log_post))`

---

## 3. First Point Where Value Becomes Approximately 5%

**Source expression:** `rppg_core.py:887`
```python
reg_raw = max(0.05, 1.0 - cv * 1.2)
```

**Condition for exact 5.0%:** `cv ≥ 0.7917`

The `max(0.05, ...)` expression is a **hard floor**. Any of these conditions fires it:
- `cv ≥ 0.7917` (highly irregular IBI intervals)
- `peaks < 3` → `else: reg_raw = 0.10` (10%, not 5%)

So 5.0% is produced by **two paths**:
1. ≥3 peaks with `cv ≥ 0.7917` (irregular timing) → `max(0.05, ...)` floors
2. The floor `0.05` is the minimum per-frame value; the 8-frame rolling mean converges to it when all recent frames are at the floor.

**Note:** 5.0% cannot come from the `< 2 peaks` branch (produces 10.0%) or `peaks = 2` (produces 25.0%).

---

## 4. Test Results and Evidence

### All 28 integration tests: PASS

| Test class | Finding |
|---|---|
| Insufficient samples | `len < 30` → SQI = 0.0, no stale state in `_reg_history` |
| Constant signals | ACF metric → near-0%; legacy → 10.0% baseline (not stale) |
| Clean periodic | Both metrics: > 50% for clean 60–130 BPM signals |
| Noisy signals | ACF degrades monotonically; legacy is noise-blind |
| Exact floor | Constructed signal with `cv = 0.90` → legacy = 5.0% ✓ |
| 8-frame history | Bounded at 8; mean tracks rolling history; cleared on `roi.clear()` |
| Poor vs bug discrimination | Both metrics flag genuinely poor signals; clean signals pass |
| Diagnostic = gate value | V2 display (`roi.roi_regularity`) and gate both use `breakdown["regularity"]` |
| V1/V2 discrepancy | Documented: V1 uses ACF, V2 uses CV; both flag poor signals correctly |

### Evidence table

| Signal type | Legacy reg | Posterior reg | Hard gate fires? |
|---|---|---|---|
| Clean 72 BPM periodic | 100.0% | 100.0% | No |
| Noisy periodic (0.05 noise) | 96.6% | 100.0% | No |
| Noisy periodic (0.50 noise) | 91.0% | 76.1% | No |
| Irregular IBI (CV=0.90) | **5.0%** | 49.2% | Yes (legacy) |
| Constant signal (flat) | 10.0% | <15% | No |
| Insufficient (< 30 frames) | 0.0% (early return) | — | No |
| Flat + 0.001 randn | 78.2% | 14.2% | No |

---

## 5. Root Cause: Legitimate Low-Quality Signal

### Finding: NOT a code or state-management bug.

The observed ~5% regularity is an **accurate assessment of genuinely poor signal quality**:

- **CV ≥ 0.7917** means inter-beat intervals vary by ≥79% relative to the mean. This is physiologically extreme arrhythmia-level irregularity.
- The floor prevents zero regularity for marginally-detectable signals (giving a "poor but present" indicator rather than a hard zero).
- The **hard gate** at `REGULARITY_HARD_GATE = 15.0%` correctly zeroes the ROI SQI when regularity is below 15%.
- Both metrics (legacy and ACF) independently flag a poor signal as low quality.
- Clean signals (>50 BPM) score >50% in both metrics; the metric is **not pinned** at 5%.
- No stale state, no global state leakage, no per-frame accumulation bug.
- The 8-frame rolling mean provides temporal inertia — a single bad frame does not immediately drop the value to the floor; it converges gradually.

### Known metric limitation (not a bug)
The legacy CV metric is **noise-blind**: pure white noise can score ~80% because randomly-spaced local maxima happen to be quasi-evenly spaced under the `distance=15` constraint. The ACF-based PosteriorSQI correctly scores the same noise as near-0%. This does NOT cause the ~5% observation; it means the legacy metric can be optimistic for noisy signals. The ~5% observation is the opposite direction (too low, not too high).

---

## 6. Diagnostic Log vs Quality Gate Consistency

**V2 (used by rppg_main):** Both the display and the gate use `breakdown["regularity"]`:
- Display (`rppg_main.py:571`): `reg={roi.roi_regularity:.1f}%` → `roi.roi_regularity = breakdown.get("regularity", 0.0)` (`rppg_core.py:2200`)
- Gate (`rppg_core.py:2207`): `v2_reg = breakdown.get("regularity", 0.0)` → hard gate fires at `< 15%`

**These are the same source expression. The diagnostic log shows exactly the value the gate uses.**

**V1:** Uses `sqi_meta["regularity_score"] × 100` (ACF-based) for `roi.roi_regularity`. This is a documented discrepancy: V1 and V2 report different regularity values for the same signal. Both independently flag poor quality, so the quality decision is consistent.

---

## 7. Frozen BPM and Low Regularity Coexistence

**Verified:** Frozen BPM can coexist with ~5% regularity.

**Mechanism:** BPM freeze is triggered by SQI/agreement conditions (`rppg_core.py:1803–1821`), not by regularity directly. The sequence:
1. Good-quality window: BPM stabilizes, SQI=60, `_frozen_bpm` set.
2. Motion/lighting degrades signal: regularity drops to ~5%.
3. SQI drops below `SQI_HARD_GATE = 20%` or agreement deteriorates.
4. Freeze condition fires (BPM already frozen, or new freeze).
5. Display shows: BPM=72.0 (locked), reg=5.0%.

This is expected and correct: freeze preserves the last known good BPM while regularity flags the degraded quality.

---

## 8. Smallest Justified Fix

**None required.** The ~5% regularity is:
1. An accurate assessment of a genuinely poor signal.
2. Correctly rejected by the hard gate (`reg < 15%` → `sqi = 0.0`).
3. Not a metric calculation bug.
4. Not a state-management bug.
5. Not a display-vs-gate discrepancy.

**Optional cosmetic improvement** (not required by constraints):
Add a label to the GUI warning when `reg < REGULARITY_HARD_GATE`:
```
if roi.roi_regularity < cfg.REGULARITY_HARD_GATE:
    why_parts.append("reg<15%")
```
This clarifies that the ROI is being rejected, not merely flagged. This is a one-line logging change in `rppg_main.py:641`.

---

## 9. Files Changed

| File | Change |
|---|---|
| `phase89_regularity_audit.py` | **New** — standalone diagnostic runner |
| `tests/engine/test_regularity_audit.py` | **New** — 28 integration tests, all pass |

**No production code modified.** All existing local changes preserved.
