# Phase 9.1 — Production Baseline Freeze

**Status:** complete — documentation only. **No production code was changed by this task.**
**Freeze date:** 2026-10-23 14:52 (SEAST)
**Repository:** `D:\main\Projects\Health`
**Branch:** `main`

---

## A. Freeze metadata

| Item | Value |
| --- | --- |
| Freeze date | 2026-10-23 |
| Repository path | `D:\main\Projects\Health` |
| Branch | `main` |
| HEAD commit | `1bf1c3b35fcb5598860964403ffd80eaec65bad5` ("Initial commit - Clean code version", 2026-10-13 10:28:51 +0700) |
| Upstream | `origin/main` at the same commit `1bf1c3b` |
| Commits created by this freeze | **none** |
| Branch created by this freeze | **none** |
| Files added by this freeze | `p11_validation/PHASE_9_1_FREEZE.md` only |

### Nature of this freeze

**This is a local working-tree freeze, not a committed and not necessarily a reproducible Git snapshot.**

- All of the Phase 9.0 / Phase 9.1 work described below lives in the **working tree only**. The last commit (`1bf1c3b`) predates it entirely; it is the "clean code version" baseline from 2026-10-13.
- Because nothing was committed, the frozen state is **not** addressable by a commit id, cannot be checked out, and cannot be restored by `git checkout` from any remote. It is only preserved by the files on disk as they are now.
- The state is **not proven immutable** and **not proven reproducible**: the working tree contains no lockfile of its own (only the untracked `requirements-rppg-env.txt`), and the dataset behind the reported numbers (`Dataset_rPPG-10/`) is not covered by the freeze in any verifiable way.

### Git working-tree status at freeze time

`git status --short` (identical before and after this task — see section F):

```
 M .serena/project.yml
 M rppg_config.py
 M rppg_core.py
 M rppg_main.py
 M rppg_sessions.db
 M rppg_sqi.py
 M tests/engine/test_motion_detector.py
?? .claude/
?? RESEARCH_PROGRESS_REPORT.md
?? null
?? p11_validation/PHASE_8_5_SQI_RECOVERY.md
?? p11_validation/PHASE_8_6_FIXES_APPLIED.md
?? p11_validation/PHASE_8_6_PEAK_REGULARITY_AUDIT.md
?? p11_validation/PHASE_8_9_REGULARITY_AUDIT.md
?? p11_validation/PHASE_9_0_SIGNAL_VALIDATION.md
?? phase81_verify_stale_fix.py
?? phase85_sqi_diagnostic.py
?? phase86_diagnostic.py
?? phase86_posterior_trace.py
?? phase87_sqi_zero_lock_diagnostic.py
?? phase88_fused_sqi_trace.py
?? phase89_regularity_audit.py
?? phase90_bpm_harmonic_audit.py
?? phase90_signal_validation.py
?? phase90_sweep_all.py
?? requirements-rppg-env.txt
?? signal_validation/
?? tests/engine/test_bpm_harmonic_resolution.py
?? tests/engine/test_regularity_audit.py
?? tests/engine/test_signal_validation.py
?? tests/engine/test_sqi_recovery.py
?? validation_output/
```

Tracked modifications (7 files, `+1600 / -66`):

```
 .serena/project.yml                  |   48 +-
 rppg_config.py                       |    4 +
 rppg_core.py                         |  346 +++++++++-
 rppg_main.py                         |   87 ++-
 rppg_sessions.db                     |  Bin 24576 -> 28672 bytes
 rppg_sqi.py                          |    8 +-
 tests/engine/test_motion_detector.py | 1173 +++++++++++++++++++++++++++++++++-
```

### Attribution of the modifications

Not all of the above belongs to Phase 9.x, and this freeze does **not** reclassify any of it:

| Change | Believed origin | Confidence |
| --- | --- | --- |
| `rppg_core.py` — `_resolve_subharmonic()` promotion threshold `0.40 -> 1.0` | **Phase 9.1** (the change this freeze documents) | High — the code comment names the phase |
| `rppg_core.py` — `harmonic_resolution` key added to the `estimate_bpm_fft()` validation dict | **Phase 9.1** | High |
| `rppg_core.py` — zero-padding to `FFT_SIZE = 256` in `estimate_bpm_fft()` | Phase 8.5 Fix B | High (code comment) |
| `rppg_core.py` — Phase 8 / 8.4 / 8.5 / 8.6 / 8.7 changes (authoritative `motion_detector.is_moving`, `_diag_*` fields, EMA bootstrap, SNR dB normalisation in `compute_dynamic_roi_weight()`, V2 regularity hard gate, V2 3-tier candidate cascade, V2 `snr_db` storage) | Phase 8.x | High (code comments) |
| `rppg_core.py` — removal of the V1 pre-fusion `REGULARITY_HARD_GATE` block | Phase 8.x | Medium — the removal is visible in the diff but is not annotated |
| `rppg_sqi.py` — comment/whitespace only (2 insertions, 6 deletions) | Cosmetic | High — no logic change in the diff |
| `rppg_config.py` — comment only (4 inserted lines above `SNR_KILL_THRESHOLD`) | Cosmetic | High — no value change |
| `rppg_main.py` — Phase 8.4E/8.6 diagnostics, `sqi_gated` / `low_snr` counters, `[ROI DEBUG]` cadence 90 -> 30 frames, `snr=` display unit changed to dB | Phase 8.x | High (code comments) |
| `tests/engine/test_motion_detector.py` — +1173 lines | Phase 8.x | Medium — file content not attributed line by line here |
| `rppg_sessions.db` — binary growth 24576 -> 28672 bytes | Runtime artefact of a live session, not a source change | High |
| `.serena/project.yml` — Serena language-server list regenerated | **Unrelated tooling churn** — not a Sanubari phase | High |
| `RESEARCH_PROGRESS_REPORT.md`, `null` (0 bytes), `requirements-rppg-env.txt` | Unrelated / ad-hoc local artefacts | Medium — `null` is a stray empty file at repo root with no known purpose |

---

## B. Current implementation

### B.1 `estimate_bpm_fft()` (verified, current source)

`rppg_core.py:776-870`. Pipeline, in order:

1. `n = len(signal)`; returns `0.0` immediately if `n < 30`.
2. **Zero-padding (Phase 8.5 Fix B):** the signal is padded with zeros to `FFT_SIZE = 256` when shorter, *before* windowing, so the Hann window tapers to zero at the padded end. Bin spacing at 30 fps becomes `0.12 Hz` (about 7 BPM) instead of `0.25 Hz` (about 15 BPM) for a 120-sample window.
3. Full-length Hann window -> `rfft` -> magnitude spectrum; the analysis band is `FREQ_LOW ... FREQ_HIGH` (derived from `BPM_LOW`/`BPM_HIGH`, `rppg_core.py:37-38`).
4. **Windowed vote:** the signal is cut into `cfg.FFT_WINDOW_SEC`-long windows with 50 % hop; each window gets its own `_pick_one_peak()`. If two or more windows voted, the winner is the **median of the largest vote cluster** (tolerance `cfg.FFT_WINDOW_VOTE_TOL`); otherwise the full spectrum is picked once.
5. **History smoothing:** the per-ROI `_peak_freq_history` (deque, maxlen 12) contributes `fft_consistency = exp(-|delta| / 0.20)`, a median-override when the history is tight (`std < 0.08`) and already has as many votes, and a x0.5 consistency penalty when the BPM jump exceeds 15 BPM.
6. `_resolve_subharmonic()` is applied to the winning candidate.
7. The returned validation dict `vi` contains `dominance`, `peak_dominance`, `dominant`, `peak_width_ok`, `harmonic_rejected`, `fft_consistency`, `n_windows`, `is_harmonic`, `resp_interference`, `top3_peaks`, `subharm_corrected`, **`harmonic_resolution`** (new in Phase 9.1: `none` / `halved` / `doubled`), and `bpm_jump_bpm`.

`_pick_one_peak()` (verified, `rppg_core.py:579-669`) is **not** changed by Phase 9.1 and remains as previously documented: the top 5 peaks are scored by power x plausibility weight (0.1 outside `cfg.BPM_PLAUSIBLE_LOW...HIGH`) x harmonic-against-`prev_bpm` penalty x Gaussian proximity to `prev_bpm`; an ambiguity check (second peak > 0.85 x first peak) may switch to the candidate closer to history; explicit 144/72-style doubling and halving traps are handled; and for any winner above 110 BPM a half-rate companion within 8 BPM and above 12 % of the winner power is preferred.

### B.2 `_resolve_subharmonic()` (verified, current source)

`rppg_core.py:684-773`. Band energy uses a +/-0.12 Hz window around the centre frequency, restricted to the analysis band.

- **Halving branch** (candidate >= `FREQ_LOW`): if `E(f/2) >= E(f) x cfg.HARMONIC_SNR_RATIO`, return `f/2` with `changed=True`. The ratio threshold is halved when `prev_bpm < 90` and `bpm_cand > 130`. **Unchanged by Phase 9.1** — deliberately, because energy at the half rate *is* evidence for the fundamental (a 2nd harmonic implies its fundamental).
- **Doubling branch** (only when `candidate_hz < 1.25`, that is candidates below 75 BPM, and the double lies inside the band): **Phase 9.1 changed this.**
  - Before: `promo_thresh = 0.40` (or `0.25` when `prev_bpm > 80` and `bpm_cand < 60`).
  - Now: `promo_thresh = 1.0` (or `0.85` when `prev_bpm > 80` and `bpm_cand < 60`). Promotion to `2f` requires `E(2f) >= E(f)`, that is the double must **dominate** the candidate.
  - Outside the branch, the candidate is returned unchanged.

### B.3 The Phase 9.1 change and its known trade-off

**The defect being fixed (verified in Phase 9.0 artefacts).**
`p11_validation/PHASE_9_0_SIGNAL_VALIDATION.md` section 7.1 and the captured output of `phase90_bpm_harmonic_audit.py` show the production FFT reporting exactly twice the true rate: on rPPG-10 Subject 1 forehead, the windowed vote of the estimator itself was 1.000 Hz = 60.0 BPM and the ECG reference was 57.4 BPM, but the answer was reported as 120.0 BPM because `E(2f)/E(f) = 0.456` exceeded the hard-coded 0.40 promotion threshold.

**The reasoning of the fix (verified from the source comment).**
Energy at `2f` is *not* evidence that the rate should be doubled — a pulse whose fundamental is `f` has its 2nd harmonic at `2f`, so energy at `2f` is precisely the signature of `f` being the fundamental. Doubling is only defensible on positive evidence that the candidate is *not* the fundamental, that is when the double dominates the spectrum.

**The evidence quoted in the code comment (dataset-wide, rPPG-10, 78 ROI videos from 26 subjects, ECG as reference):**

- `E(2f)/E(f)` at the voted candidate spans **0.368 - 0.995**, median **0.577**.
- **76 of 78** ROIs are above the old 0.40 ratio, so the old rule doubled **72 of 78** recordings.
- Mean absolute error against the ECG rate drops from **42.9 BPM to 16.1 BPM** with the new rule.
- **No ROI reaches ratio 1.0** — on this dataset the fixed rule never doubles.

**The known trade-off (stated in the source comment, unresolved).**
When the true rate is fast (ECG about 90-105 BPM) the window vote can settle on a half-rate component (54-60 BPM) whose `E(2f)/E(f)` ratio (0.65-0.99) **overlaps** the slow-subject range (0.37-0.68). A single FFT cannot separate *"2f is the 2nd harmonic of f"* from *"2f is the fundamental and f is a sub-harmonic artefact"*. The new rule breaks that tie **in favour of the lower rate**, which is what the ECG shows for the majority of the dataset — at the cost of under-reporting BPM for genuinely fast subjects. Resolving this requires evidence **outside** the FFT (for example the beat stream) and is explicitly out of scope for Phase 9.1.

### B.4 Current SQI and regularity behaviour relevant to this baseline

These are pre-existing (Phase 8.x) behaviours that the frozen state contains; they are **not** Phase 9.1 work and were not altered by this freeze.

- **Two production regularities coexist and disagree by design.** `compute_sqi()` produces `breakdown["regularity"]`, the legacy CV-based metric on the detected IBI sequence (0-100 scale); `rppg_sqi.PosteriorSQI` reports an ACF-based `regularity_score`. On the rPPG-10 sweep the legacy metric reports 64.7-69.0 % (median 66.6) while the ACF metric reports 1.4-25.4 % (median 7.3) on the same inputs.
- **The legacy regularity is noise-blind** (Phase 9.0 section 7.2): the ECG inter-beat CV is 0.04-0.24 (median 0.08) while the detector IBI CV is 0.26-0.29 (median 0.28) across all subjects — the excess is constant and therefore a property of the *detector*, not of the recorded rhythm. The legacy number must not be presented as a physiological quantity.
- **SNR units were unified on dB** (Phase 8.6 Fix 2b): V2 now stores `roi.roi_snr = sqi_meta["snr_db"]` (dB) instead of a 0-100 normalised score, matching V1 and `cfg.SNR_KILL_THRESHOLD = 20.0` (dB).
- **V2 gained the hard regularity gate and the 3-tier candidate cascade** (Phase 8.6 Fix 1 / Phase 8.7): ROIs with `0 < regularity < cfg.REGULARITY_HARD_GATE` are zeroed, `0 < regularity < 25` are penalised x0.2, and V2 falls back Tier 2 (BPM in range, relaxed SQI) then Tier 3 (BPM in range, no SQI filter) instead of returning empty.
- **`compute_dynamic_roi_weight()` SNR normalisation was corrected**: `roi_snr` is dB, so the score is now `((snr + 20) / 60) ** 1.5` clamped to `[0, 1]` (dB -20 -> 0, +40 -> 1) rather than `(snr / 100) ** 1.5`.
- **`fft_penalty` accumulation** in `compute_sqi()` was changed from a `getattr(locals(), ...)` hack to a properly initialised accumulator.

### B.5 Known limitations and unresolved fundamental-vs-harmonic ambiguity

1. **Fundamental vs. harmonic is not solved.** The Phase 9.1 rule is a *tie-break*, not a resolution. The overlapping-ratio regime (fast true rate, about 90-105 BPM) is still undecided and biased towards the lower rate.
2. **The doubling branch cannot fire above 75 BPM candidates** (`candidate_hz < 1.25` guard). Candidates at or above 75 BPM are never doubled — a documented scope limit, pinned by a test (`test_doubling_branch_only_covers_candidates_below_75_bpm`).
3. **The windowed vote can be captured by a weaker half-rate artefact** while the real pulse dominates the full-spectrum FFT. This is the one case the `promo_thresh = 1.0` rule is meant to catch.
4. **`_pick_one_peak()` history coupling** (`prev_bpm`) makes the estimate path-dependent: the same recording can yield different BPM depending on the preceding frames.
5. **The rPPG-10 signal itself is marginal** (Phase 9.0 section 6A: SNR -1.63 ... +7.72 dB, median -0.07 dB after the production preprocessing chain), so the "mean absolute error 42.9 -> 16.1 BPM" figure describes a corrected *estimator on weak signals*, not a clinically accurate one.
6. **ECG/video offset is unpublished** (about +/-500 ms stated uncertainty; the per-subject searched offsets are mutually inconsistent: +1.60, -3.15, +0.20, +1.15 s). All beat-level agreement numbers are therefore hypothesis-level.
7. **Dataset provenance is unresolved** (rPPG-10 has no published licence).

### B.6 Verified vs. hypothesised

**Verified in this session (read from source, or re-run read-only):**

- The exact current source of `estimate_bpm_fft()` and `_resolve_subharmonic()` (B.1, B.2) — quoted from `rppg_core.py` as it stands.
- The working-tree status and the full diff of all 7 tracked modifications (section A).
- The focused Phase 9.1 test file passes: **13 passed, 18 subtests passed** (section C).
- The full test suite passes: **267 passed, 18 subtests passed, 4 warnings** (section C).
- `rppg_core.py`, `rppg_sqi.py` and `rppg_config.py` in the main working tree are **byte-identical** to their counterparts in the `worktree-rppg-p92` worktree (`diff -q` reported no differences) — that is, no Phase 9.2 production change exists anywhere in the repository.

**Reported but NOT re-verified by this task:**

- Every dataset-level number quoted in the Phase 9.1 source comment (ratio span 0.368-0.995, 76/78 above 0.40, 72/78 doubled, mean absolute error 42.9 -> 16.1 BPM). These come from the Phase 9.0/9.1 sweeps; they were **not** re-run during this freeze (the sweep takes about 20 s per subject over 27 subjects and rewrites `validation_output/`). They are recorded as *claims of the phase*, not as facts independently re-verified here.
- The exact definition of the "16.1 BPM" figure (mean over ROIs? per-subject mean? against ECG mean HR?) is not restated in the source comment and is therefore ambiguous — see section E.

---

## C. Test baseline

### C.1 Focused Phase 9.1 test — re-run read-only during this freeze

Command (run from the repository root):

```bash
/c/miniconda3/envs/rppg_env/python.exe -m pytest tests/engine/test_bpm_harmonic_resolution.py -q -p no:cacheprovider
```

Result:

```
.............                                          [100%]
13 passed, 18 subtests passed in 22.79s
```

The file is `tests/engine/test_bpm_harmonic_resolution.py` (233 lines, untracked). It pins **both** the reported BPM and the harmonic-resolution decision. Covered cases:

- a slow pulse (57.4 / 60 BPM) with a strong 2nd harmonic is **not** doubled — and the test asserts the old 0.40 evidence was genuinely present, so the test cannot silently stop exercising the regression;
- the already-correct 72 BPM case is preserved for `h2` in {0, 0.5, 0.9};
- genuinely fast pulses (110 / 120 / 150 BPM) are neither halved nor shifted;
- a 2nd-harmonic amplitude sweep (`h2` in 0.1 ... 0.9) keeps the fundamental;
- a 3rd harmonic does not trigger doubling;
- moderate noise keeps the fundamental (5 seeds);
- the promotion boundary itself: ratio just below 1.0 -> **not** promoted; ratio >= 1.0 -> promoted;
- the old 0.40 threshold *would* have fired on the same spectrum;
- legitimate halving still works, and a lone fast peak is not halved;
- the doubling branch only covers candidates below 75 BPM;
- a zero candidate is untouched.

### C.2 Full suite — re-run read-only during this freeze

Command:

```bash
/c/miniconda3/envs/rppg_env/python.exe -m pytest tests/ -q -p no:cacheprovider
```

Result:

```
267 passed, 4 warnings, 18 subtests passed in 81.84s (0:01:21)
```

The 4 warnings are `PytestReturnNotNoneWarning` from `tests/benchmark/test_e2e_synthetic.py` (4 test functions return a bool instead of asserting). They are **pre-existing** and unrelated to Phase 9.1.

### C.3 Pre-existing failures vs. failures introduced by Phase 9.1

**There are none — on either the focused file or the full suite.**

- Focused file: 13/13 pass.
- Full suite: 267/267 pass.
- No test was modified, skipped, xfailed, or deleted by this task.
- No test was modified *by Phase 9.1* either: the Phase 9.1 change added `tests/engine/test_bpm_harmonic_resolution.py` as a **new** file; the tracked test file `tests/engine/test_motion_detector.py` was modified during the Phase 8.x work, not by Phase 9.1.

### C.4 Historical baseline for comparison (from Phase 9.0 documentation)

`p11_validation/PHASE_9_0_SIGNAL_VALIDATION.md` section 3 recorded, before the Phase 9.1 production change:

```bash
$PY -m pytest tests/engine/test_signal_validation.py -q      # 40 passed
$PY -m pytest tests/ -q                                      # 254 passed (incl. the 40)
```

The full suite is now **267** passed — the +13 are exactly the new Phase 9.1 harmonic-resolution tests. The Phase 9.0 numbers therefore remain consistent with the current state.

### C.5 Caveats on these results

- The tests were run with `-p no:cacheprovider` and from the repository root; the only filesystem side effects are Python `__pycache__` directories, which are already present and untracked.
- `pytest.ini` sets `testpaths = tests p3_spatial p4_reliability p5_neural p6_temporal p7_self_supervised p8_multitask p9_domain_generalization p10_stress_lab p11_validation`, so a bare `pytest` run would collect more than `pytest tests/`. The command above is the one the Phase 9.0 document used, so the two numbers are directly comparable.
- The suite passing says nothing about physiological accuracy; no test in it asserts accuracy against ECG ground truth.

---

## D. Preserved artifacts

All of the following were left **exactly as found**. Nothing in this list was modified, moved, deleted, staged, stashed, or reverted by this freeze.

### D.1 Phase 9.0 artefacts (diagnostic, read-only against production)

| Path | What it is |
| --- | --- |
| `p11_validation/PHASE_9_0_SIGNAL_VALIDATION.md` | The Phase 9.0 report (455 lines) — the source of the doubling-defect analysis and of the dataset sweep |
| `signal_validation/` | Offline validation library (untracked package): `base.py`, `pipeline.py`, `metrics.py`, `reference.py`, `report.py`, `synthetic.py`, `io.py`, `alignment.py`, `failure.py`, `sync.py`, `rppg10_adapter.py` (32.6 KB), plus `test_validation.py` and `test_rppg10_adapter.py`. Imports production modules read-only; touches no threshold |
| `phase90_signal_validation.py` | CLI entry point (`synthetic` / `video` / `subject` / `session`) |
| `phase90_sweep_all.py` | Sweep summariser -> `sweep_summary.csv` / `.md` |
| `phase90_bpm_harmonic_audit.py` | Isolates the FFT BPM failure; produced the section 7.1 numbers |
| `tests/engine/test_signal_validation.py` | 40 tests with known ground truth (untracked) |
| `validation_output/` | Generated outputs: `synthetic_results.json`, `subject_<N>_report.md` x27, `sweep_summary.csv`, `sweep_summary.md`, `signals/` (raw + filtered + peak exports), `raw_signals_demo.csv`, `session_report.md` |

### D.2 Phase 9.1 artefacts

| Path | What it is |
| --- | --- |
| `rppg_core.py` (`_resolve_subharmonic()`, `promo_thresh`) | The production change itself, with the full rationale in the source comment |
| `rppg_core.py` (`harmonic_resolution` key) | New diagnostic field in the `estimate_bpm_fft()` validation dict |
| `tests/engine/test_bpm_harmonic_resolution.py` | 13 regression tests (untracked) |
| — | **There is no `PHASE_9_1_*.md` document.** The Phase 9.1 rationale lives in the source comment; this freeze file is the first written record of it |

### D.3 Phase 8.x artefacts (context for the frozen state)

| Path | What it is |
| --- | --- |
| `p11_validation/PHASE_8_5_SQI_RECOVERY.md` | Phase 8.5 report |
| `p11_validation/PHASE_8_6_FIXES_APPLIED.md` | Phase 8.6 report |
| `p11_validation/PHASE_8_6_PEAK_REGULARITY_AUDIT.md` | Phase 8.6 peak/regularity audit |
| `p11_validation/PHASE_8_9_REGULARITY_AUDIT.md` | Phase 8.9 regularity audit |
| `phase81_verify_stale_fix.py`, `phase85_sqi_diagnostic.py`, `phase86_diagnostic.py`, `phase86_posterior_trace.py`, `phase87_sqi_zero_lock_diagnostic.py`, `phase88_fused_sqi_trace.py`, `phase89_regularity_audit.py` | Ad-hoc Phase 8.x diagnostic scripts (all untracked) |
| `tests/engine/test_sqi_recovery.py`, `tests/engine/test_regularity_audit.py` | Phase 8.x test files (untracked) |

### D.4 Unrelated / pre-existing local work (preserved untouched)

| Path | Note |
| --- | --- |
| `.serena/project.yml` | Tracked, modified — Serena tooling config regenerated. Unrelated to any Sanubari phase |
| `rppg_sessions.db` | Tracked, modified (binary, 24 576 -> 28 672 bytes) — runtime artefact of a live session, not source |
| `RESEARCH_PROGRESS_REPORT.md` | Untracked, 562 lines — a read-only codebase audit report |
| `requirements-rppg-env.txt` | Untracked — `pip freeze` of the `rppg_env` conda environment (UTF-16 encoded, 1872 package lines) |
| `null` | Untracked, 0 bytes — stray empty file at repository root, purpose unknown |
| `.claude/` | Untracked — contains `worktrees/` (see D.7) |

### D.5 Dependency and dataset requirements to reproduce the baseline

- **Interpreter:** `/c/miniconda3/envs/rppg_env/python.exe` (conda env `rppg_env`). The environment snapshot is `requirements-rppg-env.txt` (UTF-16). The Phase 9.0 report cites NumPy 2.2.6, SciPy 1.15.3, OpenCV 4.13.0.92, MediaPipe 0.10.9, MediaPipe FaceLandmarker 0.10.35.
- **MediaPipe model:** `models/face_landmarker.task` (needed only for live sessions, not for the offline FFT/SQI work).
- **Dataset:** `Dataset_rPPG-10/` — 27 subjects, each with three 30 fps, 64x64, 18 000-frame ROI AVI files and a synchronised `Subject_N_ECG.npy` (1000 Hz, 600 000 samples). **Subject 4 ships 0-byte videos** and is skipped by the CLI.
- **Reproduction of the Phase 9.0 numbers** requires roughly 27 x 20 s of sweep time plus the ECG/video offset search:

```bash
PY=/c/miniconda3/envs/rppg_env/python.exe
for s in $(seq 1 27); do
  $PY phase90_signal_validation.py --out validation_output subject --subject $s --search-offset
done
$PY phase90_sweep_all.py --dir validation_output
$PY phase90_bpm_harmonic_audit.py \
    --video Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi \
    --ecg  Dataset_rPPG-10/Subject_1/Subject_1_ECG.npy
```

**Note:** re-running the sweep **overwrites `validation_output/`**. It was deliberately *not* re-run during this freeze for that reason.

### D.6 Known inconsistency between preserved artefacts (ambiguity, not resolved)

Two mismatches exist in the preserved state. They are recorded here rather than fixed, per the freeze rules.

1. **`validation_output/synthetic_results.json` is stale relative to `signal_validation/synthetic.py`.** The stored JSON records the `noisy` case at `snr_db = 5.59`, `sensitivity = 0.944`, `bpm_fft = 144.0` — the *pre-Phase-9.1* estimator behaviour (144 BPM = 2x the true 72 BPM), with `noise_std = 1.20`. The current untracked `signal_validation/synthetic.py` uses `noise_std = 4.00` for that case, with a comment explaining that 1.20 was calibrated against the doubled-rate estimator and therefore no longer tested what it claimed. **The Phase 9.0 report section 4 table therefore describes the older parameters, and the JSON output has not been regenerated.** The comment in that file is itself labelled *"Phase 9.2 recalibration"*, even though the change it describes is a consequence of the Phase 9.1 production fix — a naming ambiguity.
2. **No committed snapshot exists for any of this.** Every artefact listed above is untracked, so `git status` alone does not distinguish "Phase 9.0 output" from "Phase 9.1 output" from "Phase 8.x output" — only the in-file comments and this document do.

### D.7 Other git worktrees (present, not touched)

`git worktree list` shows four worktrees, all at commit `1bf1c3b`:

| Worktree | Branch | State observed (read-only) |
| --- | --- | --- |
| `D:/main/Projects/Health` | `main` | **the frozen state** |
| `.claude/worktrees/rppg-fixes` | `worktree-rppg-fixes` | modified tracked files, untracked Phase 8.x docs |
| `.claude/worktrees/rppg-p89` | `worktree-rppg-p89` | modified tracked files, untracked Phase 8.9/9.0 artefacts |
| `.claude/worktrees/rppg-p92` | `worktree-rppg-p92` | modified tracked files **plus Phase 9.2 exploratory scripts** (`phase92_harmonic_evidence.py`, `phase92_evaluation_matrix.py`, `phase92_evidence_power.py`, `phase92_fullres_presence.py`, `phase92_ecg_rate_presence.py`) |

A branch `worktree-rppg-bugfix` also exists at `1bf1c3b` without a worktree.

**Important:** the `rppg-p92` worktree contains *exploratory* Phase 9.2 scripts, but its `rppg_core.py`, `rppg_sqi.py` and `rppg_config.py` are **byte-identical to the main working tree** (verified with `diff -q`), and the **main working tree contains no `phase92_*.py` file and no Phase 9.2 production change**. The main working tree therefore remains a clean Phase 9.1 baseline. See section E.

---

## E. Resume point

### Next planned task: **Phase 9.2 — Evidence-Based Fundamental Resolution**

**This is NOT implemented by this freeze.** Nothing in the main working tree implements it, and this task introduced nothing towards it.

The next phase must, **before any production change is approved**:

1. **Evaluate independent time-domain evidence.** The FFT alone cannot separate "2f is the 2nd harmonic of f" from "2f is the fundamental and f is a sub-harmonic artefact". Candidates already available in the codebase are the legacy peak stream (the `find_peaks` series behind `breakdown["regularity"]`) and the ACF-based posterior stream in `rppg_sqi.PosteriorSQI` — that is, the beat stream, which carries the independent evidence the FFT lacks.
2. **Address the harmonic ambiguity explicitly.** The overlapping-ratio regime (true rate about 90-105 BPM, candidate settles at 54-60 BPM, ratio 0.65-0.99 vs. the slow-subject range 0.37-0.68) is the known blind spot of the Phase 9.1 rule and must be characterised, not assumed away.
3. **Build synthetic ground-truth cases.** The existing `signal_validation/synthetic.py` pulse train is a fundamental plus 2nd harmonic, not real PPG morphology; Phase 9.2 needs cases where the *fundamental* is genuinely fast, and cases where a genuine sub-harmonic artefact competes with a fast true rate.
4. **Define an explicit ambiguous / low-confidence outcome.** A resolution policy that must always output a rate cannot represent "the evidence does not separate 60 from 120 BPM". The outcome must be representable in the existing plumbing (`vi["harmonic_resolution"]`, the SQI path, and the session-confidence output) and must not silently fall back to one of the two rates.
5. **Report the cost of every candidate policy** against the same rPPG-10 sweep and against the synthetic ground truth, including the fast-subject regime, so that the choice between "prefer the lower rate" and "prefer the beat stream" is an evidenced decision rather than a default.

### E.1 Gate before any production change

No production file may be edited in Phase 9.2 until all of the following exist:

- a written, reproducible evidence set for the ambiguous regime (the 0.65-0.99 overlap band), using the same rPPG-10 ECG reference and the same offset caveat as Phase 9.0;
- a synthetic ground-truth suite that includes fast fundamentals (about 90-120 BPM) and injected sub-harmonic artefacts;
- an explicit, tested representation of "ambiguous / low confidence" in the production plumbing;
- a before/after comparison on the identical dataset with the same metric definition as the 42.9 -> 16.1 BPM figure, including its exact definition (which this freeze notes is currently ambiguous);
- a decision record stating which policy was chosen and what it costs in the fast-subject regime.

### E.2 Where to resume from

- The **main working tree** (`main`) is the frozen Phase 9.1 baseline described above.
- Exploratory Phase 9.2 scripts already exist in the **`.claude/worktrees/rppg-p92` worktree** (`phase92_harmonic_evidence.py`, `phase92_evaluation_matrix.py`, `phase92_evidence_power.py`, `phase92_fullres_presence.py`, `phase92_ecg_rate_presence.py`). They are diagnostics and were **not** verified, run, or adopted by this freeze; their production files are byte-identical to the frozen baseline. A resuming session may reuse them, but must treat their outputs as unverified until re-run and documented.
- The frozen baseline has **no commit**; committing it is a separate, explicitly-approved action.

---

## F. Verification performed by this freeze

| Check | Result |
| --- | --- |
| `git status --short` re-checked after writing the document | Unchanged except the added `p11_validation/PHASE_9_1_FREEZE.md` (untracked) — see the "after" listing in section F.1 |
| Production files modified by this task | **None.** `rppg_core.py`, `rppg_sqi.py`, `rppg_config.py`, `rppg_main.py` are byte-identical to their pre-task state (the diff stat is unchanged: `rppg_core.py 346 +`, `rppg_config.py 4 +`, `rppg_main.py 87 +`, `rppg_sqi.py 8 +`) |
| Pre-existing modifications removed or reverted | **None.** All 7 modified tracked files are still modified with the same diff |
| Pre-existing untracked deliverables removed | **None.** All 25 untracked entries listed in section A are still present |
| Destructive git commands run | **None.** No `reset`, `checkout`, `restore`, `clean`, `stash`, `rm`, `commit`, `amend`, `push`, or branch creation |
| Tests re-run | Yes, read-only, with `-p no:cacheprovider`; no report or generated artefact was overwritten |
| Dataset sweep re-run | **No** — it would overwrite `validation_output/` (see D.5) |

### F.1 Working-tree status after the freeze

```
 M .serena/project.yml
 M rppg_config.py
 M rppg_core.py
 M rppg_main.py
 M rppg_sessions.db
 M rppg_sqi.py
 M tests/engine/test_motion_detector.py
?? .claude/
?? RESEARCH_PROGRESS_REPORT.md
?? null
?? p11_validation/PHASE_8_5_SQI_RECOVERY.md
?? p11_validation/PHASE_8_6_FIXES_APPLIED.md
?? p11_validation/PHASE_8_6_PEAK_REGULARITY_AUDIT.md
?? p11_validation/PHASE_8_9_REGULARITY_AUDIT.md
?? p11_validation/PHASE_9_0_SIGNAL_VALIDATION.md
?? p11_validation/PHASE_9_1_FREEZE.md
?? phase81_verify_stale_fix.py
?? phase85_sqi_diagnostic.py
?? phase86_diagnostic.py
?? phase86_posterior_trace.py
?? phase87_sqi_zero_lock_diagnostic.py
?? phase88_fused_sqi_trace.py
?? phase89_regularity_audit.py
?? phase90_bpm_harmonic_audit.py
?? phase90_signal_validation.py
?? phase90_sweep_all.py
?? requirements-rppg-env.txt
?? signal_validation/
?? tests/engine/test_bpm_harmonic_resolution.py
?? tests/engine/test_regularity_audit.py
?? tests/engine/test_signal_validation.py
?? tests/engine/test_sqi_recovery.py
?? validation_output/
```

The single difference from the pre-freeze listing is the added `?? p11_validation/PHASE_9_1_FREEZE.md`.

### F.2 Explicit non-claims

- The baseline is **not** claimed to be immutable.
- The baseline is **not** claimed to be fully reproducible (see section A, "Nature of this freeze").
- The baseline is **not** claimed to be committed or recoverable via Git.
- The dataset-level accuracy claims of Phase 9.0/9.1 are **not** re-verified by this task (see B.6).
- Phase 9.2 is **not** started in this working tree.
