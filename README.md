# Health

## Active Engine
The active rPPG processing engine is **MultiROIFusionEngineV2** (`rppg_core.py`).
Legacy baseline **MultiROIFusionEngine (V1)** is preserved but not used by default.

## Research System
This is a **research prototype** for camera-based physiological measurement.
- Core HR estimation from facial video is the primary validated component.
- Respiration rate, HRV metrics, stress index, arrhythmia detection, and AI interpretation are **EXPERIMENTAL**.
- This system is NOT a medical device and makes NO diagnostic claims.

## CLI Usage
```bash
python rppg_main.py --log  # Enable reproducibility logging
python rppg_main.py --help  # Show options
```

## Research Logging
Press `[L]` during a session to save reproducibility logs (CSV files) of raw signals, SQI breakdowns, and events.


## Repository Layout

```
rppg_main.py                     Entry point (CLI session runner)
rppg_core.py  rppg_signal.py     Engine (MultiROIFusionEngineV2) and its modules:
rppg_config / sqi / roi /        config, SQI, ROI, temporal fusion, uncertainty,
  temporal / uncertainty /       physiological state, vitals, algorithms, AI layer
  physio_state / vitals /
  algorithms / ai
rppg_sessions.db                 Session database (default path used by rppg_ai.py)
.req.txt                         Dependencies
models/                          MediaPipe / face model files
Dataset_rPPG-10/                 Real dataset (P11)

rppg_benchmark*.py               Benchmark framework (Phase 1/2). Imported by name by the engine
                                 (rppg_core -> rppg_benchmark), so these stay at the repo root.
benchmark_video.py               Benchmark CLIs:  benchmark_synthetic_example.py,
  benchmark_stabilize.py           phase2_data_acquisition.py, rppg_phase2_realbenchmark.py,
  ...                              capture_real_face.py
benchmarks/experimental/         Experimental Phase-2 benchmark code (not imported by anything)

p3_spatial/ ... p11_validation/  One package per phase (P3 spatial, P4 reliability, P5 neural,
                                 P6 temporal, P7 self-supervised, P8 multitask, P9 domain
                                 generalization, P10 stress lab, P11 validation). Tests are
                                 kept next to the code.
tests/engine/                    Engine tests (SQI, signal routing, uncertainty, vitals, ...)
tests/benchmark/                 Benchmark / Phase-2 acquisition tests
tests/manual/                    Manual scripts (need camera / models / Windows paths); never collected
scripts/                         Utilities and audit tools (validation gate, test inventory, ...)
docs/                            Documentation, one file per phase (00 ... 12), plus assets/
archive/                         Legacy and one-off debugging material, kept for reference
```

Details of what moved and why: `docs/REORGANIZATION_REPORT.md`.

## Running Tests

```bash
pytest                                  # tests/ plus every phase package (see pytest.ini)
pytest p9_domain_generalization/ -v     # one phase
python tests/engine/test_uncertainty.py # script-style tests also run directly
python scripts/run_test_inventory.py    # Phase-1/2 inventory
```

P5-P10 need PyTorch. Always run commands from the repository root.

## Documentation

| File | Phase |
|---|---|
| `docs/00_engine_upgrade.md` | Engine upgrade summary (May 2026) |
| `docs/01_phase1_benchmark_infrastructure.md` | Phase 1 |
| `docs/02_phase2_real_data_benchmark.md` | Phase 2 |
| `docs/03_p3_spatial.md` ... `docs/11_p11_validation.md` | P3 ... P11 |
| `docs/12_engine_runtime_audits.md` | Post-P11 engine audits |
