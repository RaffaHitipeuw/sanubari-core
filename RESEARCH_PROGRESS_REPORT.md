# Research Progress Report: Remote Photoplethysmography (rPPG) — Camera-Based Physiological Measurement

**Project:** Sanubari rPPG Research System  
**Report Date:** Generated from codebase audit  
**Repository State:** Single initial commit (`1bf1c3b`), working tree modified  

---

## 1. Executive Summary

This is a research prototype for **camera-based (remote) photoplethysmography (rPPG)** — extracting heart rate and other physiological signals from facial video without contact sensors. The system implements a multi-ROI fusion engine (MultiROIFusionEngineV2) using MediaPipe face landmark detection, signal quality indexing, Bayesian ROI weighting, and temporal smoothing.

**Current status:** Infrastructure and algorithms are **implemented and partially tested**. Real physiological accuracy **cannot be claimed** due to lack of validated ground truth. The codebase contains nine research phases (P3–P11), with Phase 2 providing the most complete infrastructure for classical method comparison. A real dataset (rPPG-10) exists but has unresolved provenance and synchronization questions.

---

## 2. Research Problem and Motivation

### Problem
Contact-based physiological monitoring (ECG, pulse oximeter) is intrusive, expensive, and impractical for continuous monitoring. Remote photoplethysmography offers contactless measurement of heart rate, respiration, and stress indicators using a standard camera.

### Motivation
- **Applications:** Healthcare monitoring, telehealth, sports science, affective computing
- **Challenges:** Motion artifacts, illumination variations, skin tone bias, harmonic confusion (doubling/halving of pulse frequency), and low signal-to-noise ratio
- **State of the field:** Classical methods (CHROM, POS, GREEN, ICA) are established baselines; deep learning approaches are emerging but require large labeled datasets

---

## 3. Research Objectives and Research Questions

### Stated Research Objectives (from docs)
| Phase | Objective | Status |
|-------|-----------|--------|
| P1 | Benchmark infrastructure | **Complete** |
| P2 | Real-data benchmark with classical baselines | **Infrastructure complete; blocked on GT** |
| P3 | Spatial/motion evolution | **Implemented, not experimentally validated** |
| P4 | Reliability and uncertainty | **Implemented, not experimentally validated** |
| P5 | Neural network approaches | **Scaffolded (models exist), not trained** |
| P6 | Temporal model exploration | **Scaffolded (models exist), not trained** |
| P7 | Self-supervised learning | **Scaffolded, not trained** |
| P8 | Multi-task learning | **Scaffolded, not trained** |
| P9 | Domain generalization | **Scaffolded, not trained** |
| P10 | Stress lab protocol | **Implemented** |
| P11 | Real-dataset validation | **Dataset acquired; adapter implemented; metrics blocked** |

### Key Research Questions
1. Can classical rPPG (CHROM/POS/GREEN) achieve clinically acceptable accuracy on real facial video?
2. Does multi-ROI fusion improve over single-ROI approaches?
3. Do neural/temporal models outperform classical methods?
4. How robust is the system under motion, illumination, and skin tone variation?
5. Can stress detection be reliably performed from physiological signals?

*Evidence status: Questions 1–5 are **not yet answered** — no real-data validation with ground truth has been completed.*

---

## 4. Proposed Contributions

| Contribution | Classification | Evidence |
|-------------|----------------|----------|
| Multi-ROI fusion with harmonic zombie detection | **Preliminary** | Code exists; harmonic rejection implemented; not validated on real data |
| Posterior SQI with Bayesian ROI weighting | **Preliminary** | Implemented; tested on synthetic data only |
| Stress lab protocol (P10) | **Proposed** | Framework exists; no experimental execution |
| rPPG-10 dataset adapter | **Preliminary** | Adapter implemented; dataset provenance unresolved |
| Temporal neural architectures (PhysNet, CNN+LSTM, Transformer) | **Proposed** | Scaffolded; no training performed |

---

## 5. System Architecture and Pipeline

### Active Engine
**MultiROIFusionEngineV2** (`rppg_core.py`, lines 1293–)

### Pipeline Stages
```
Camera Frame
    ↓
MediaPipe FaceLandmarker (models/face_landmarker.task)
    ↓
ROI Extraction (forehead, left cheek, right cheek)
    ↓
Signal Processing (CHROM/POS/GREEN/ICA via rppg_algorithms.py)
    ↓
SQI Computation (PosteriorSQI in rppg_sqi.py)
    ↓
BPM Estimation (FFT with harmonic rejection)
    ↓
Bayesian ROI Weighting (LearnedWeighting)
    ↓
Hierarchical Fusion + Kalman Smoothing
    ↓
Session Confidence Scoring
    ↓
Output: fused_bpm, fused_sqi, per-ROI metrics
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| Face detection | MediaPipe Tasks FaceLandmarker 0.10.35 | 478-landmark face mesh |
| ROI extraction | `rppg_core.py` (lines 47–56) | 3 anatomical ROIs via landmark indices |
| Signal extraction | `rppg_signal.py` | Optical flow stabilization, pulse-rich pixel selection |
| rPPG algorithms | `rppg_algorithms.py` | CHROM, POS, GREEN, ICA implementations |
| SQI | `rppg_sqi.py` | PosteriorSQI, BayesianROIWeighting, StatisticallyCalibratedSQI |
| Temporal smoothing | `rppg_temporal.py` | KalmanBPMFilter, ProbabilisticFusion |
| Uncertainty | `rppg_uncertainty.py` | UncertaintyAwareConfidence |
| Physiological state | `rppg_physio_state.py` | PhysiologicalStateClassifier, PantingAdaptiveHR |

### Models Directory
```
models/
├── face_detector.tflite         224 KB
├── face_landmarker.task         1.3 MB  (MediaPipe FaceLandmarker)
└── face_landmarks_detector.tflite  1.1 MB
```

---

## 6. Algorithms and Technical Methods

### 6.1 rPPG Signal Extraction
| Method | Implementation | Evidence |
|--------|---------------|----------|
| CHROM | `rppg_algorithms.py` | Implemented |
| POS (Plane Orthogonal to Skin) | `rppg_algorithms.py` | Implemented |
| GREEN (mean green channel) | `rppg_algorithms.py` | Implemented |
| ICA | `rppg_algorithms.py` | Implemented |

### 6.2 Signal Quality Index (SQI)
**PosteriorSQI** (`rppg_sqi.py:36–265`):
- SNR-based logit score (reference 6 dB, temperature 4 dB)
- Spectral concentration weighting (weight 0.8)
- Regularity scoring via autocorrelation and CV (weight 0.5)
- Motion prior, illumination prior
- **Physiological BPM priors:** Hard rejection at >130 BPM, forehead high-BPM penalty
- **Harmonic/subharmonic filtering:** Rejects peaks with 2:1 or 1:2 ratio to stable BPM
- **Temporal inertia:** Penalizes jumps >30 BPM (weight -6.0)
- **Peak dominance ratio:** Rejects if second peak >77% of first peak

### 6.3 ROI Weighting
**BayesianROIWeighting** (`rppg_sqi.py:289–369`):
- Beta-distributed success probability per ROI
- BPM agreement weighting: `exp(-|bpm - fused| / 12.0)`
- Harmonic/subharmonic penalty (0.4x for subharmonic, 0.3x for harmonic)
- BPM gate: >145 → 0.15x, >135 → 0.30x, >130 → 0.50x
- Forehead high-BPM penalty: additional 0.15x multiplier

### 6.4 Harmonic Rejection
- **Zombie streak detection** (`rppg_core.py:1141–1221`): Confirmed when ROI BPM ≈ 2× another ROI's BPM for ≥5 consecutive frames
- **FFT-based rejection** (`rppg_signal.py:54–93`): Checks sub-harmonic energy ratio >40–60%
- **Peak picking** (`rppg_core.py:549–639`): Penalizes peaks in harmonic relationship, applies doubling/halving trap detection

### 6.5 Temporal Smoothing
- **KalmanBPMFilter** (`rppg_temporal.py`): Q_BPM=0.5, Q_VEL=0.3, R_BPM=2.0
- **EMA smoothing** with configurable alpha
- **BPM jump protection** (max 10 BPM jump, 2.5× for immature windows)
- **Stable lock detection** (std ≤3.5 BPM over 8 seconds)

---

## 7. Implementation Status

### 7.1 Core Engine (V2)

| Component | File | Status | Evidence |
|-----------|------|--------|----------|
| MultiROIFusionEngineV2 | `rppg_core.py` | **Implemented** | 1397+ lines, active |
| SQI (PosteriorSQI) | `rppg_sqi.py` | **Implemented** | 405 lines |
| Bayesian ROI weighting | `rppg_sqi.py` | **Implemented** | 81 lines |
| Harmonic rejection | `rppg_core.py` | **Implemented** | 80+ lines |
| Kalman smoothing | `rppg_temporal.py` | **Implemented** | Evidence in code |
| Face landmark adapter | `rppg_benchmark_face_landmarker.py` | **Implemented** | Verified MediaPipe integration |

### 7.2 Phase Packages

| Phase | Package | Status | Evidence |
|-------|---------|--------|----------|
| P3 Spatial | `p3_spatial/` | **Implemented** | 9 files, spatial quality maps, motion field |
| P4 Reliability | `p4_reliability/` | **Implemented** | 9 files, uncertainty decomposition |
| P5 Neural | `p5_neural/` | **Scaffolded** | 12 files, models defined, no training |
| P6 Temporal | `p6_temporal/` | **Scaffolded** | 12 files, LSTM/GRU/Transformer, no training |
| P7 Self-supervised | `p7_self_supervised/` | **Scaffolded** | 10 files, no training |
| P8 Multi-task | `p8_multitask/` | **Scaffolded** | 10 files, no training |
| P9 Domain generalization | `p9_domain_generalization/` | **Scaffolded** | 9 files, no training |
| P10 Stress lab | `p10_stress_lab/` | **Implemented** | 11 files, protocol exists |
| P11 Validation | `p11_validation/` | **Partial** | 13 files, adapter exists, metrics blocked |

### 7.3 Benchmark Infrastructure

| Component | File | Status | Evidence |
|-----------|------|--------|----------|
| Video iterator | `rppg_benchmark_video.py` | **Implemented** | Test: 28 methods pass |
| GT parsing | `rppg_benchmark_gt.py` | **Implemented** | Test: 6 methods pass |
| Timestamp alignment | `rppg_benchmark_alignment.py` | **Implemented** | Test: 20 methods pass |
| Metrics (MAE/RMSE/Pearson/B-A) | `rppg_benchmark.py` | **Implemented** | Synthetic validated |
| Ablation framework | `rppg_benchmark.py:308–437` | **Implemented** | 8 ablation configs |
| Synthetic fixture | `synthetic_fixture_gt.csv` | **Available** | 70.5 BPM reference |
| Real dataset adapter | `p11_validation/rppg10_adapter.py` | **Implemented** | rPPG-10 dataset mapped |

### 7.4 Test Suite Status

| Test File | Test Count | Status | Evidence |
|-----------|------------|--------|----------|
| `test_benchmark_infrastructure.py` | 28 | **PASS** | Docs 01, 02 |
| `test_ground_truth.py` | 6 | **PASS** | Docs 01, 02 |
| `test_benchmark_alignment.py` | 20 | **PASS** | Docs 01, 02 |
| `test_e2e_synthetic.py` | 4 | **PASS** | Docs 01 |
| `test_phase2_acquisition.py` | 18 | **PASS** | Docs 02 |
| `benchmark_synthetic_example.py` | 5 | **PASS** | Docs 01 |

**Total verified tests: 63+ methods, 0 failures**

---

## 8. Experimental Setup

### 8.1 Hardware / Software Environment

| Element | Specification | Evidence |
|---------|--------------|----------|
| Python | miniconda3 / rppg_env | `docs/02_phase2_real_data_benchmark.md:823` |
| NumPy | 2.2.6 | `docs/02_phase2_real_data_benchmark.md:1032` |
| SciPy | 1.15.3 | `docs/02_phase2_real_data_benchmark.md:1033` |
| OpenCV | 4.13.0.92 | `docs/02_phase2_real_data_benchmark.md:1034` |
| MediaPipe | 0.10.9 | `docs/02_phase2_real_data_benchmark.md:1035` |
| Face model | MediaPipe Tasks FaceLandmarker 0.10.35 | `docs/02_phase2_real_data_benchmark.md:99–119` |
| Random seed | 42 (fixed) | `rppg_benchmark.py:191` |

### 8.2 Available Datasets

| Dataset | Status | Details | Evidence |
|---------|--------|---------|----------|
| Synthetic fixture | **Available** | `synthetic_fixture.mp4`, gray square, 90 frames | `synthetic_fixture_gt.csv` |
| rPPG-10 (26 subjects) | **Acquired** | 64×64 AVI, 30 fps, 10 min, ECG ground truth | `docs/11_p11_validation.md` |

### 8.3 rPPG-10 Dataset Characteristics

| Property | Value | Confidence |
|----------|-------|------------|
| Video FPS | **30.000 fps (CFR)** | Verified — zero variance, OpenCV confirmed |
| Frame count | 18,000 per recording | Verified |
| Duration | 600.0 s (10 min) | Verified |
| Resolution | 64 × 64 px | Verified |
| Codec | MPEG-1 | Binary inspection |
| ECG samples | 600,000 per subject | Verified |
| ECG fs | **1000 Hz (inferred)** | Not documented — strong inference from duration match |
| Subjects | 27 (26 usable, Subject_4 lost) | Verified |
| Arrhythmia subjects | S09, S18 | Metadata confirmed |
| Skin tones | Fitzpatrick I–IV | Metadata confirmed |
| Illumination | 300–1500 Lux | Metadata confirmed |

**Dataset provenance: Unknown — no license, no original paper, author "Gonçalo Rodrigues" in XLSX metadata. Cannot be published without resolving license.**

### 8.4 Evaluation Protocol

| Metric | Method | Min N | Evidence |
|--------|--------|-------|----------|
| MAE | `mean(|pred - gt|)` | 10 | `rppg_benchmark.py:278–279` |
| RMSE | `sqrt(mean((pred-gt)²))` | 10 | `rppg_benchmark.py:280–281` |
| Pearson r | `scipy.stats.pearsonr` | 3 | `rppg_benchmark.py:283–291` |
| Bland-Altman | Bias, LoA, proportional bias | 10 | `rppg_benchmark.py:208–260` |
| Bootstrap CIs | 1000 resamples, 95% | — | `rppg_benchmark.py:178–205` |

---

## 9. Results and Metrics

### 9.1 Synthetic Validation (Infrastructure Only)

| Test | Result | Interpretation |
|------|--------|----------------|
| Perfect alignment MAE | **0.000 BPM** | Metrics mathematically correct |
| Known bias (5.0 BPM) | **MAE = 5.00 BPM** | Bias correctly detected |
| Random noise (σ=2) | **MAE = 1.63 BPM** | Consistent with theory |
| Combined bias+noise | **Bias = 2.86 BPM** | Correctly measured |

**Evidence:** `docs/01_phase1_benchmark_infrastructure.md:460–491`

### 9.2 Real-Data Validation

**Status: NOT EXECUTED — blocked by:**
1. ECG sampling rate unverified (inferred as 1000 Hz, not confirmed)
2. Video-ECG synchronization offset unverified (±500 ms uncertainty cited in adapter)
3. Dataset license/provenance unresolved

### 9.3 Smoke Test (Static Frame)

| Metric | Value | Condition |
|--------|-------|-----------|
| Valid BPM outputs | 7/200 frames | Static test image (not real video) |
| BPM range | 88.1–88.2 | Same frame repeated — artificial |
| SQI range | 55.9–67.4 | Same frame repeated — artificial |

**Evidence:** `docs/02_phase2_real_data_benchmark.md:219–238`

### 9.4 Algorithm-Specific Results

**Status: No real-data comparisons executed.** Classical methods (CHROM/POS/GREEN/ICA) are implemented but have not been benchmarked on real physiological data.

---

## 10. Failed, Invalidated, or Inconclusive Experiments

| Experiment | Outcome | Evidence |
|-----------|---------|----------|
| DNN face detection adapter | **REJECTED** | Template projection, not genuine ML landmarks — `docs/02_phase2_real_data_benchmark.md:365–368` |
| Synthetic fixture as face proxy | **REJECTED** | Gray square has no face — `docs/02_phase2_real_data_benchmark.md:256–267` |
| ECG fs = 1000 Hz claim | **UNVERIFIED** | Inferred from duration match, not confirmed in metadata — `docs/11_p11_validation.md:546–591` |
| Real-data benchmark (G5–G8) | **BLOCKED** | No independent ground truth with verified sync — `docs/02_phase2_real_data_benchmark.md:242–276` |

---

## 11. Limitations and Threats to Validity

### 11.1 Ground Truth Limitations
1. **No independent physiological ground truth** — External sensor (Polar H10, CMS50D+) not acquired
2. **ECG sampling rate unverified** — Inferred as 1000 Hz from duration matching; cannot be confirmed from file metadata
3. **Synchronization offset unknown** — ±500 ms uncertainty cited; per-subject offsets not verified
4. **Dataset provenance unresolved** — rPPG-10 has no license, no original publication, cannot be published

### 11.2 Technical Limitations
1. **64×64 pixel resolution** — Very low; real-world cameras typically provide higher resolution
2. **Forehead ROI vulnerability** — High-BPM harmonic false locks common; explicit suppression needed
3. **Skin tone bias** — LUM-A/B/C labels are luminance-based, NOT Fitzpatrick classification
4. **Motion robustness** — Tested on synthetic data; real motion stress testing not executed
5. **Arrhythmia subjects** — S09 and S18 flagged; standard MAE/RMSE metrics may not be appropriate

### 11.3 Methodological Limitations
1. **Phase 5–9 neural models not trained** — No evidence for deep learning performance
2. **No ablation studies executed** — AblationConfig implemented but not run on real data
3. **No cross-dataset validation** — rPPG-10 only; no held-out dataset for generalization testing
4. **No clinical validation** — System explicitly disclaiming medical claims

### 11.4 Reproducibility Gaps
1. Single git commit — no version history for algorithmic evolution
2. Configuration parameters scattered — many tuned values (BPM priors, SQI weights) lack ablation justification
3. Working tree modified — `rppg_sqi.py` shows local changes

---

## 12. Reproducibility and Artifact Availability

### 12.1 Repository Structure
```
./
├── rppg_main.py              # CLI entry point
├── rppg_core.py              # V2 fusion engine
├── rppg_sqi.py               # SQI computation
├── rppg_signal.py            # Optical flow, POS extraction
├── rppg_algorithms.py         # Classical methods
├── rppg_config.py            # ~100 hyperparameters
├── models/                   # MediaPipe model files
├── Dataset_rPPG-10/          # Real dataset (26 subjects)
├── synthetic_fixture_gt.csv   # Synthetic reference
├── p3_spatial/ ... p11_validation/  # Phase packages
├── tests/                    # Test suite (63+ methods)
├── benchmarks/               # Experimental benchmarks
├── scripts/                  # Utilities
└── docs/                    # Phase documentation (12 files)
```

### 12.2 Dependencies
```
opencv-python>=4.8.0
mediapipe>=0.10.0
numpy>=1.24.0
scipy>=1.11.0
requests>=2.28.0
```

### 12.3 Reproducibility Checklist
| Element | Status | Evidence |
|---------|--------|----------|
| Git commit captured | Yes | `1bf1c3b` |
| Random seed fixed | Yes | 42 in benchmark code |
| Configuration logged | Partial | Many params in rppg_config.py |
| Environment documented | Yes | docs/02_phase2_real_data_benchmark.md:822–1035 |
| Test suite passing | Yes | 63+ tests, 0 failures |

---

## 13. Comparison With Existing Research

**Status: PENDING — no literature comparison evidence exists in codebase.**

### Required Actions
1. Literature review of rPPG state-of-the-art (PURE, COHFACE, UBFC-rPPG benchmarks)
2. Collect published MAE/RMSE values for CHROM, POS, GREEN baselines
3. Execute own benchmarks on rPPG-10
4. Compare with published results under matched conditions

### Expected Baselines (from literature, not yet verified)
- CHROM on PURE: MAE ≈ 2–5 BPM
- POS on PURE: MAE ≈ 2–4 BPM
- GREEN on PURE: MAE ≈ 3–6 BPM
- Deep learning: MAE ≈ 1–3 BPM (on matched datasets)

---

## 14. Claims Supported by Current Evidence

| Claim | Classification | Evidence |
|-------|---------------|----------|
| Infrastructure metrics are mathematically correct | **Verified** | Synthetic validation (MAE=0 for perfect, 5.0 for biased, 1.63 for noisy) |
| Timestamp alignment algorithm is correct | **Verified** | 20 alignment tests pass |
| Classical methods are implemented | **Verified** | CHROM/POS/GREEN/ICA all executable |
| V2 engine is frozen | **Verified** | No modifications to core files per Phase 1 audit |
| Video is 30 fps CFR | **Verified** | Zero variance, OpenCV-confirmed |
| FaceLandmarker is genuine ML | **Verified** | MediaPipe Tasks API, not template projection |
| rPPG-10 has 26 usable subjects | **Verified** | Subject_4 lost, S13/S21 minor frame deviation |

---

## 15. Claims Not Yet Supported

| Claim | Required Evidence |
|-------|-------------------|
| Real heart rate accuracy (any MAE value) | Real video + verified ground truth |
| Method superiority (V2 vs CHROM/POS) | Side-by-side real-data benchmark |
| Multi-ROI fusion advantage | Ablation on real data |
| Neural model performance | Training and evaluation |
| Stress detection accuracy | Experimental protocol execution |
| Clinical applicability | Field study |
| Robustness under motion | Stress test execution |
| Skin tone generalizability | Multi-dataset evaluation |
| Arrhythmia detection | Specialized validation |

---

## 16. Remaining Work and Priorities

### Priority 1: Verify Ground Truth (BLOCKING)
1. **Confirm ECG sampling rate** — Contact dataset author or identify device
2. **Establish video-ECG synchronization** — Verify ±500 ms claim or find true offset
3. **Resolve dataset provenance** — Identify license terms before publication

### Priority 2: Execute Real-Data Benchmark
1. Run P11 validation on rPPG-10 (26 subjects)
2. Compute MAE, RMSE, Pearson r, Bland-Altman
3. Execute ablation study (full system vs individual components)
4. Report per-subject breakdown with failure accounting

### Priority 3: Classical Method Comparison
1. Compare V2 vs CHROM vs POS vs GREEN vs ICA on real data
2. Statistical significance testing
3. Failure mode analysis

### Priority 4: Neural Model Development
1. Train PhysNet/CNN+Temporal on rPPG-10
2. Compare with classical baselines
3. Evaluate on held-out subjects

### Priority 5: Generalization Testing
1. Acquire external dataset (PURE/COHFACE/UBFC-rPPG)
2. Test cross-dataset generalization
3. Identify dataset-specific failure modes

---

## 17. Evidence Index

### Core Source Files
| File | Lines | Relevance |
|------|-------|-----------|
| `rppg_core.py` | 1397 | Active V2 engine, fusion logic |
| `rppg_sqi.py` | 405 | PosteriorSQI, BayesianROIWeighting |
| `rppg_signal.py` | 462 | Optical flow, POS, respiratory analysis |
| `rppg_algorithms.py` | — | CHROM, POS, GREEN, ICA |
| `rppg_config.py` | — | ~100 hyperparameters |
| `rppg_temporal.py` | — | Kalman, probabilistic fusion |
| `rppg_benchmark.py` | 773 | Metrics, ablation, reproducibility |

### Documentation
| File | Content |
|------|---------|
| `docs/00_engine_upgrade.md` | May 2026 engine changes |
| `docs/01_phase1_benchmark_infrastructure.md` | P1 audit and closure |
| `docs/02_phase2_real_data_benchmark.md` | P2 audit and closure (5 parts) |
| `docs/03_p3_spatial.md` | P3 spatial evolution |
| `docs/11_p11_validation.md` | rPPG-10 dataset forensic audit |
| `docs/12_engine_runtime_audits.md` | Optical flow and session diagnostics |

### Phase Packages
| Package | Files | Evidence |
|---------|-------|----------|
| `p3_spatial/` | 9 | Motion-aware quality, spatial maps |
| `p4_reliability/` | 9 | Uncertainty decomposition, plausibility |
| `p5_neural/` | 12 | PhysNet, attention, CNN models |
| `p6_temporal/` | 12 | LSTM, GRU, Transformer |
| `p7_self_supervised/` | 10 | Augmentations, encoder |
| `p8_multitask/` | 10 | Multi-task heads and losses |
| `p9_domain_generalization/` | 9 | Sampling and splits |
| `p10_stress_lab/` | 11 | Protocol conditions and metrics |
| `p11_validation/` | 13 | rPPG-10 adapter, sync, alignment |

### Tests
| File | Tests | Status |
|------|-------|--------|
| `tests/benchmark/test_benchmark_infrastructure.py` | 28 | PASS |
| `tests/benchmark/test_ground_truth.py` | 6 | PASS |
| `tests/benchmark/test_benchmark_alignment.py` | 20 | PASS |
| `tests/benchmark/test_e2e_synthetic.py` | 4 | PASS |
| `tests/engine/` | — | Engine unit tests |
| `tests/manual/` | — | Manual integration scripts |

---

## 18. Suggested Paper Outline

### 18.1 Title Candidates
1. "Multi-ROI Bayesian Fusion for Robust Remote Photoplethysmography"
2. "Harmonic Rejection and Signal Quality Indexing for Camera-Based Heart Rate Estimation"
3. "Camera-Based Physiological Monitoring: Benchmarking Classical and Neural Approaches"

### 18.2 Abstract Facts (to be filled with real results)
- rPPG extracts heart rate from facial video using remote photoplethysmography
- System uses MediaPipe face landmark detection with 3 anatomical ROIs
- Posterior SQI combines SNR, spectral concentration, regularity, and physiological priors
- Bayesian ROI weighting adapts to signal quality per region
- [MAE: pending real-data execution]
- [Comparison with CHROM/POS/GREEN: pending]

### 18.3 Methodology Outline
1. **Signal acquisition:** Facial video at 30 fps, MediaPipe 478-landmark detection
2. **ROI extraction:** Forehead (7 landmarks), left cheek (16), right cheek (16)
3. **rPPG algorithms:** CHROM, POS, GREEN, ICA; active method configurable
4. **SQI computation:** PosteriorSQI with Bayesian fusion of 5 evidence sources
5. **BPM estimation:** FFT with harmonic/subharmonic rejection, temporal smoothing
6. **Multi-ROI fusion:** Hierarchical clustering with Bayesian ROI weighting
7. **Evaluation:** MAE, RMSE, Pearson correlation, Bland-Altman on rPPG-10

### 18.4 Results Outline
1. **Synthetic validation:** Metrics mathematically correct
2. **Real-data benchmark:** [Pending execution]
   - Per-method MAE/RMSE with 95% CIs
   - Bland-Altman plots
   - Failure rate breakdown
3. **Ablation study:** [Pending execution]
   - Full system vs without SQI
   - Full system vs without temporal smoothing
   - Full system vs single-ROI
4. **Failure analysis:** Motion, illumination, skin tone

### 18.5 Discussion Topics
1. **Strengths:** Robust harmonic rejection, principled SQI, multi-ROI fusion
2. **Limitations:** 64×64 resolution, single dataset, unverified ground truth sync
3. **Comparison with literature:** [Pending literature review]
4. **Clinical applicability:** Distance from clinical deployment
5. **Future work:** Deep learning, multi-dataset validation, stress detection

---

## Summary

This research project implements a comprehensive rPPG system with classical signal processing, quality indexing, and multi-ROI fusion. The infrastructure is well-tested (63+ unit tests passing) and documented. However, **no real physiological accuracy claims are supported** because ground truth synchronization and dataset provenance remain unverified. The neural and advanced phases (P5–P9) are scaffolded but not trained. The most immediate priorities are verifying the rPPG-10 ground truth and executing the real-data benchmark to establish the classical method baseline.

---

*Report generated: READ-ONLY audit of codebase*  
*Files examined: 50+ source files, 12 documentation files, 6 test modules*  
*No source files modified*
