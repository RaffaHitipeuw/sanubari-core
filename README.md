# sanubari-core

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Architecture](https://img.shields.io/badge/Architecture-MultiROI%20Fusion-5B5BD6)](#system-architecture)
[![Build](https://img.shields.io/badge/Build-Research%20Prototype-orange)](#validation-and-tests)

**sanubari-core** is a local, real-time remote photoplethysmography (rPPG) engine for estimating physiological signals from facial video. It combines MediaPipe landmark tracking, multi-region-of-interest (ROI) color analysis, chrominance/POS signal processing, signal-quality assessment, temporal fusion, and uncertainty-aware gating.

The repository is designed for research, engineering experimentation, and reproducible validation. It is not a medical device and must not be used to diagnose, treat, or monitor a medical condition.

## Status and Scope

The active runtime engine is `MultiROIFusionEngineV2` in [`rppg_core.py`](rppg_core.py). The original `MultiROIFusionEngine` implementation is retained as a legacy baseline and is not selected by the default CLI.

Heart-rate estimation from facial video is the primary validated capability. Respiration rate, HRV metrics, stress index, arrhythmia flags, and AI-assisted interpretation are experimental research outputs and are not clinically validated.

## Overview

Remote photoplethysmography estimates subtle, pulse-related changes in facial skin reflectance without physical contact. For each frame, sanubari-core tracks facial landmarks and evaluates several skin-containing regions, currently including:

- forehead;

- left cheek; and

- right cheek.

For a region of interest, spatially averaged color observations are accumulated over time. The engine can use the green channel and chrominance/POS-derived signals to emphasize pulsatile variation relative to slowly varying illumination. A simplified POS-style projection can be expressed as:

$$
\mathbf{C}(t) = \begin{bmatrix} R(t) \\ G(t) \\ B(t) \end{bmatrix}, \qquad
\mathbf{C}_{n}(t) = \frac{\mathbf{C}(t)}{\operatorname{mean}(\mathbf{C}(t))}
$$

$$
S_1(t) = G_n(t) - B_n(t), \qquad
S_2(t) = G_n(t) + B_n(t) - 2R_n(t), \qquad
S_{POS}(t) = S_1(t) + \alpha S_2(t)
$$

where the projection and normalization reduce common-mode illumination effects. The implementation then applies detrending, band-limited filtering, spectral analysis, and temporal consistency checks. The cardiac search band is configured in [`rppg_config.py`](rppg_config.py), with a default operating range of 50–180 BPM.

The current engine also accounts for practical sources of error:

- motion and micro-motion rejection;

- head-pose and landmark validity gating;

- skin coverage and ROI brightness checks;

- exposure-drift compensation;

- signal-to-noise and regularity metrics;

- ROI agreement and adaptive ROI weighting;

- harmonic and subharmonic rejection;

- temporal inertia, median/EMA smoothing, and Kalman filtering; and

- confidence and uncertainty propagation.

The term “non-Gaussian noise reduction” should be understood as a quality-aware artifact-rejection strategy rather than an assumption that all camera noise is Gaussian. The pipeline uses robust physiological plausibility checks, peak dominance, temporal persistence, ROI consensus, motion gates, and SQI penalties to suppress artifacts that do not behave like a stable pulsatile signal.

## Key Features

- **Remote vital-sign extraction** — estimates heart rate from a webcam or video stream without contact sensors.

- **Multi-ROI fusion** — combines forehead and cheek regions while retaining per-ROI diagnostics and trust weights.

- **Quality-aware signal filtering** — uses SQI, SNR, regularity, motion, exposure, pose, ROI agreement, and physiological plausibility gates.

- **Chrominance and POS processing** — supports color-space signal extraction and method arbitration through the signal-processing modules.

- **Low-latency processing pipeline** — processes frames incrementally and exposes a frame-level `FrameResult` instead of requiring a complete video in memory.

- **Temporal stabilization** — applies outlier handling, historical inertia, median/EMA smoothing, Kalman filtering, and stable-lock logic.

- **Reproducibility logging** — optional CSV logging for raw signals, SQI breakdowns, and runtime events.

- **Local and edge-friendly execution** — no cloud service is required at runtime; the system runs with Python, OpenCV, MediaPipe, NumPy, and SciPy installed locally.

- **Research and validation tooling** — includes unit tests, synthetic fixtures, benchmarks, phase-based experiments, and validation reports.

## System Architecture

```
Video source
  │
  ├── OpenCV VideoCapture
  │
  ▼
Frame acquisition and normalization
  │  brightness/exposure tracking, optional blur, frame-rate estimation
  ▼
Face detection and landmark tracking
  │  MediaPipe Face Mesh; landmark validity and staleness checks
  ▼
Adaptive facial ROIs
  │  forehead, left cheek, right cheek
  │  skin coverage, pose, jaw/blink, motion and micro-motion gates
  ▼
Color-signal extraction
  │  RGB observations → normalized channels → green/POS/chrominance paths
  ▼
Signal conditioning
  │  detrending → bandpass filtering → spectral/FFT analysis
  │  artifact suppression → harmonic/subharmonic rejection
  ▼
Quality and uncertainty estimation
  │  SNR, regularity, peak dominance, temporal consistency, ROI agreement
  ▼
Multi-ROI temporal fusion
  │  adaptive ROI trust → plausibility gates → smoothing/Kalman filtering
  ▼
FrameResult
  │
  ├── fused_bpm
  ├── fused_sqi and session_confidence
  ├── motion/exposure/ROI diagnostics
  ├── cardiac and respiratory signal buffers
  └── optional experimental physiological metrics
```

At a high level, the runtime path is:

1. Capture a BGR frame with OpenCV.

1. Detect or reuse MediaPipe facial landmarks.

1. Construct the configured facial ROIs.

1. Reject or down-weight frames affected by motion, poor pose, invalid landmarks, poor skin coverage, or exposure drift.

1. Accumulate RGB observations and derive pulse-sensitive signals.

1. Detrend and filter the signal, then estimate the dominant cardiac frequency.

1. Compare candidate estimates across ROIs and time.

1. Return an uncertainty- and quality-aware `FrameResult`.

## Repository Layout

```
rppg_main.py                 Interactive webcam CLI and visualization session
rppg_core.py                 V1 baseline and active MultiROIFusionEngineV2
rppg_signal.py               POS/chrominance, filtering, peak and respiratory helpers
rppg_roi.py                  Adaptive ROI management
rppg_sqi.py                  Signal-quality and learned ROI weighting components
rppg_temporal.py             Temporal fusion and stabilization
rppg_uncertainty.py          Confidence and uncertainty propagation
rppg_vitals.py               Experimental respiration, HRV and physiological outputs
rppg_config.py               Runtime configuration and thresholds
rppg_algorithms.py           Signal-processing algorithm registry
models/                      MediaPipe and face-model assets
scripts/                     Validation, inventory and signal-debugging utilities
p3_spatial/ ... p11_validation/
                             Phase-based research and validation packages
tests/                       Engine and benchmark tests
docs/                        Phase documentation and runtime audit notes
.req.txt                     Minimal runtime dependency specification
requirements-rppg-env.txt   Full captured research environment
```

## Installation

### Prerequisites

- Python 3.10 or newer;

- a webcam or prerecorded video source;

- a local display if using the interactive CLI; and

- sufficient, stable frontal lighting for meaningful measurements.

The project currently uses a script/module layout and does not yet publish a packaged `sanubari_core` import. Run commands from the repository root.

### Setup

```bash
git clone https://github.com/RaffaHitipeuw/sanubari-core.git
cd sanubari-core

python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r .req.txt
```

The minimal dependency file installs the runtime stack. `requirements-rppg-env.txt` is a much larger, pinned environment snapshot containing optional research, benchmark, and machine-learning dependencies; use it only when you need those additional experiments:

```bash
python -m pip install -r requirements-rppg-env.txt
```

If MediaPipe model assets are missing in a fresh checkout, verify that the files under [`models/`](models/) are present before starting a session.

## Quick Start

### Interactive webcam session

The supported entry point is the CLI:

```bash
python rppg_main.py
```

Enable reproducibility logging when running a research session:

```bash
python rppg_main.py --log
```

During a session, press `L` to save reproducibility logs. The CLI also supports the interactive controls implemented in [`rppg_main.py`](rppg_main.py); press `H` in the running window to view the available controls.

### Minimal programmatic frame loop

The engine accepts an OpenCV BGR frame and MediaPipe face-landmark result. The following example shows the core integration path without duplicating the CLI visualization layer:

```python
import cv2
import mediapipe as mp

from rppg_core import MultiROIFusionEngineV2

cap = cv2.VideoCapture(0)
engine = MultiROIFusionEngineV2(enable_logging=True)
face_mesh = mp.solutions.face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
)

try:
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        height, width = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detection = face_mesh.process(rgb)
        landmarks = (
            detection.multi_face_landmarks[0]
            if detection.multi_face_landmarks
            else None
        )

        result = engine.update(frame, landmarks, height, width)

        if result.fused_bpm > 0:
            print(
                f"HR: {result.fused_bpm:.1f} BPM | "
                f"SQI: {result.fused_sqi:.1f}% | "
                f"Confidence: {result.session_confidence:.1f}%"
            )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    face_mesh.close()
    cv2.destroyAllWindows()
```

A valid face is not guaranteed on every frame. Treat `fused_bpm == 0`, low SQI, `motion_rejected`, `output_frozen`, and low session confidence as quality states—not as zero physiological measurements.

## Configuration

Runtime thresholds are centralized in [`rppg_config.py`](rppg_config.py). Important defaults include:

- `FPS_TARGET = 30.0`;

- `MIN_FRAMES = 120` before a stable estimate is expected;

- `CALIBRATION_FRAMES = 180` for the initial calibration phase;

- `RPPG_ALGO = "POS"`;

- `BPM_LOW = 50.0` and `BPM_HIGH = 180.0`;

- `SQI_HARD_GATE = 20.0`; and

- motion entry/exit thresholds of `2.5` and `1.5`.

These values are research defaults, not universal physiological or clinical limits. Change them only together with a documented validation experiment.

## Validation and Tests

Run the full test suite from the repository root:

```bash
pytest
```

Run selected areas:

```bash
pytest p9_domain_generalization/ -v
python tests/engine/test_uncertainty.py
python scripts/run_test_inventory.py
```

The repository contains synthetic fixtures, benchmark scripts, phase-specific packages, and validation documentation. P5–P10 experiments may require PyTorch and other dependencies from the full environment snapshot. Review the relevant document under [`docs/`](docs/) before comparing results across phases.

## Reproducibility

For a reproducible session, record at minimum:

- commit hash and Python version;

- camera model, resolution, and effective frame rate;

- lighting and subject-motion conditions;

- configuration changes from [`rppg_config.py`](rppg_config.py); and

- logged raw signals, SQI breakdowns, events, and benchmark ground truth where available.

The `--log` option enables the engine's reproducibility logger. Log output is intended for analysis and auditability; it does not convert the system into a clinically validated instrument.

## Limitations and Responsible Use

rPPG is sensitive to lighting, camera exposure, frame rate, compression, skin coverage, head pose, facial motion, facial hair, occlusion, and subject-specific physiology. Estimates can be unstable or unavailable when signal quality is poor.

Heart rate is the primary validated output in this repository. Respiration, HRV, stress, arrhythmia, and AI interpretation features are experimental. Never use these outputs as a substitute for a pulse oximeter, ECG, clinician, or emergency service. Do not make health or diagnostic decisions from this software.

## Roadmap

Planned or potential future work includes:

- robust multi-face tracking and subject identity management;

- stronger cross-device and cross-lighting validation;

- standardized public benchmark reports with confidence intervals;

- mobile integration for Android and iOS;

- WebAssembly or browser-compatible signal-processing exports;

- a stable installable Python package and typed public API;

- broader reference-sensor alignment and external validation; and

- clearer separation between validated core measurements and experimental research modules.

Roadmap items are not promises of clinical performance or release dates.

## Contributing

Contributions should include a focused description of the change, reproducible steps, tests or benchmark evidence, and any effect on signal quality, latency, or failure behavior. Changes to physiological thresholds should include the rationale, dataset or fixture used, and before/after measurements.

Please avoid submitting claims that imply diagnosis, medical certification, or clinical accuracy without appropriate evidence and regulatory review.

## License

This project is intended to be released under the [MIT License](LICENSE). If the repository does not yet contain a `LICENSE` file, add the standard MIT license text before distributing a release or presenting the repository as formally licensed.

## Citation

If you use sanubari-core in academic work, research reports, benchmarks, or competition submissions, cite the repository and the exact commit used. A minimal BibTeX entry is:

```
@software{sanubari_core,
  author  = {Hitipeuw, Raffa},
  title   = {sanubari-core: A Multi-ROI Remote Photoplethysmography Engine},
  year    = {2026},
  url     = {https://github.com/RaffaHitipeuw/sanubari-core},
  note    = {Accessed: YYYY-MM-DD}
}
```

When publishing results, also report the camera, frame rate, lighting conditions, subject protocol, reference sensor, preprocessing configuration, quality-gating policy, and evaluation split. This information is necessary for meaningful comparison and reproducibility.

## References

- De Haan, G. and Jeanne, V. “Robust Pulse Rate From Chrominance-Based rPPG.” *IEEE Transactions on Biomedical Engineering*, 2013. [DOI](https://doi.org/10.1109/TBME.2013.2266196)

- Verkruysse, W., Svaasand, L. O., and Nelson, J. S. “Remote Plethysmographic Imaging Using Ambient Light.” *Optics Express*, 2008. [DOI](https://doi.org/10.1364/OE.16.002865).

- MediaPipe Face Mesh documentation: [Google AI Edge](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker)

- OpenCV documentation: [opencv.org](https://docs.opencv.org/)
