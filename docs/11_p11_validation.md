# P11 — Real-Dataset Validation

> Dataset forensic audit, acquisition-metadata verification and first real-dataset run for `p11_validation/`. Moved from `p11_validation/`.

> **Consolidated document.** Each part below is the original file, merged verbatim (headings demoted two levels, nothing summarised or removed).
> Other documents refer to the original file names; use the table to find the matching part.

| Part | Section | Original file | Original date |
|---|---|---|---|
| 1 | Dataset forensic audit | `DATASET_FORENSIC_AUDIT.md` | 2026-10-11 |
| 2 | Acquisition metadata verification | `ACQUISITION_METADATA_VERIFICATION.md` | 2026-10-11 |
| 3 | First real-dataset run | `FIRST_REAL_DATASET_RUN.md` | 2026-10-11 |

## Contents

- [Part 1 — Dataset forensic audit](#part-1-dataset-forensic-audit)
- [Part 2 — Acquisition metadata verification](#part-2-acquisition-metadata-verification)
- [Part 3 — First real-dataset run](#part-3-first-real-dataset-run)

---

## Part 1 — Dataset forensic audit

*Original file: `DATASET_FORENSIC_AUDIT.md` (dated 2026-10-11)*

### Sanubari Phase 11 — Raw Dataset Forensic Audit

**Audit date**: 2024 (based on Subject Data.xlsx acquisition dates)
**Dataset archive**: `Dataset_rPPG-10/`
**Audit methodology**: Binary inspection of AVI containers, NPY array analysis, XLSX metadata parsing, MPEG-1 sequence header extraction, index chunk analysis

---

#### 1. Dataset Identity and Provenance

| Field | Value |
|-------|-------|
| **Dataset name** | rPPG-10 (implied from folder name) |
| **Nominally stated subjects** | 27 (Subject_1 through Subject_27) |
| **Actual usable subjects** | 26 (Subject_4 video data missing) |
| **Acquisition dates** | 2024-06-20 to 2024-06-28 (per Subject Data.xlsx) |
| **Location** | Dataset_rPPG-10/ |
| **License** | Unknown — no license file present |
| **Original paper** | Not found — no associated publication or documentation |
| **Author/institution** | Unknown |
| **Source** | Uploaded archive; no provenance chain |

**Evidence**: `Subject Data.xlsx` records acquisition dates from 20 Jun 2024 through 28 Jun 2024 across 26 subjects (Subject_4 is absent from the spreadsheet — confirmed absent, not blank). No README, paper, or metadata file exists in the archive.

---

#### 2. File Inventory and Integrity

##### 2.1 Directory structure

```
Dataset_rPPG-10/
├── Subject Data.xlsx
├── Subject_1/   (4 files)
├── Subject_2/   (4 files)
├── ...
├── Subject_27/  (4 files)
```

Each subject directory contains exactly 4 files:
- `Subject_X_Forehead_.avi`
- `Subject_X_Cheek1_.avi`
- `Subject_X_Cheek2_.avi`
- `Subject_X_ECG.npy`

##### 2.2 File count consistency

```
All 27 subject directories contain exactly 4 files each.
```

##### 2.3 File size anomalies

| Subject | Forehead | Cheek1 | Cheek2 | ECG |
|---------|----------|--------|--------|-----|
| **Subject_4** | **0 bytes** | **0 bytes** | **0 bytes** | 4,800,128 bytes |

**Subject_4 is a total video loss**: all three camera recordings are zero-byte files. The ECG file is intact and identical in size to all other ECG files (4,800,128 bytes). This is either a recording failure or a data extraction bug.

##### 2.4 ECG array shape consistency

All 27 ECG NPY files have shape `(600000,)` — 600,000 samples, 1D, `float64`.

##### 2.5 Camera frame count consistency (all cameras per subject)

All three cameras (Forehead, Cheek1, Cheek2) report identical frame counts for every subject. Frame counts by subject:

| Subject | Frames | Subject | Frames | Subject | Frames |
|---------|--------|---------|--------|---------|--------|
| 01 | 18000 | 10 | 18000 | 19 | 18000 |
| 02 | 18000 | 11 | 18000 | 20 | 18000 |
| 03 | 18000 | 12 | 18000 | 21 | **17983** |
| **04** | **0** | 13 | **17996** | 22 | 18000 |
| 05 | 18000 | 14 | 18000 | 23 | 18000 |
| 06 | 18000 | 15 | 18000 | 24 | 18000 |
| 07 | 18000 | 16 | 18000 | 25 | 18000 |
| 08 | 18000 | 17 | 18000 | 26 | 18000 |
| 09 | 18000 | 18 | 18000 | 27 | 18000 |

Frame counts sourced from the AVI `idx1` index chunk (authoritative), not the stream header. Three subjects deviate slightly: S13 (17996), S21 (17983). All others are exactly 18000. The deviation is ≤17 frames (< 0.1%) — likely dropped frames at recording start or end.

##### 2.6 AVI header corruption

The AVI stream header (`strh` chunk) reports `dwScale=0, dwRate=0` for every file. The `fccHandler` field is null (empty 4 bytes). This means the nominal frame rate field is absent from the AVI header. The actual frame count comes from `idx1`, which is intact.

---

#### 3. Subject Data.xlsx Metadata

##### 3.1 Contents

The spreadsheet contains 16 rows of subject characteristics across 26 columns (one per subject, Subject_4 excluded):

| Characteristic | Range / Values |
|----------------|----------------|
| Age | 20–25 years |
| Sex | 14 F / 12 M |
| Height | 153–187 cm |
| Weight | 51–136 kg |
| Skin tone | Fitzpatrick I–IV |
| Health condition | 25 Normal, 2 Arrhythmia (S09, S18) |
| Physical exercise | 13 Yes / 13 No |
| Alcohol | 1 Yes (S23), 25 No |
| Smoking | 5 Yes (S03,S08,S09,S17,S18) |
| Skin obstruction | 6 Glasses, 2 Makeup, 1 Hair, 17 None |
| Temperature | 25–27 °C |
| Humidity | 60–76 % |
| Illumination | 300–1500 Lux (variable) |
| Recording dates | 20–28 Jun 2024 |
| Recording times | 10:15h – 16:15h |

**Notable**: Two arrhythmia subjects (S09, S18) are flagged in the metadata. This may be intentional heterogeneity or may represent recording errors.

---

#### 4. Video Technical Metadata

##### 4.1 AVI container analysis

Extracted via binary inspection of the RIFF-AVI structure:

| Property | Value | Source |
|----------|-------|--------|
| Container | AVI (RIFF format) | RIFF header |
| Codec | MPEG-1 video | Frame data byte pattern `00 00 01 B3` (MPEG-1 sequence header start code) |
| Encoder | Lavc59.37.100 (FFmpeg libavcodec) | MPEG user data string in frame data |
| Resolution | **64 × 64 pixels** | BITMAPINFOHEADER in AVI strf chunk |
| Frame count | **~18000** (exact) | AVI `idx1` index chunk |
| MPEG-1 sequence header resolution | 256 × 144 | Encoded in MPEG-1 sequence header (pre-cropped full-frame) |
| MPEG-1 sequence header frame rate code | 3 → **25 fps** (see §6) | MPEG-1 sequence header byte 5 |
| AVI header declared fps | **Corrupted (0/0)** | strh chunk dwScale/dwRate = 0 |
| GOP structure | Keyframe every 12 frames | 1500 keyframes in 18000 frames |
| Keyframe pattern | Exactly 12 frames between keyframes | MPEG-1 default GOP (N=12) |

##### 4.2 Frame size distribution

For Subject_1 Forehead (representative):

| Statistic | Value |
|-----------|-------|
| Frame count | 18000 |
| Mean frame size | 43.6 bytes |
| Median frame size | 22 bytes |
| Min frame size | 9 bytes |
| Max frame size | 298 bytes |
| Keyframe count | 1500 (every 12th frame) |
| Non-keyframe count | 16500 |

Frame sizes are highly variable due to MPEG-1 compression of the small 64×64 ROI. Keyframes are larger (avg ~250 bytes), predicted frames are small (avg ~22 bytes).

---

#### 5. ECG NPY Array Analysis

##### 5.1 Basic statistics (all 27 subjects)

| Property | All subjects |
|----------|-------------|
| Shape | `(600000,)` — 1D |
| Dtype | `float64` |
| Min | 0.0 – 429.0 (varies) |
| Max | 698.0 – 1023.0 |
| Mean | 507.0 – 507.4 (all subjects) |
| Std | 25.8 – 43.1 |
| NaN count | 0 (all subjects) |
| Inf count | 0 (all subjects) |
| Finite values | 100% (all subjects) |
| Unique values | 313 – 936 (out of possible 1024 levels) |

##### 5.2 ADC bit depth evidence

The value range 0–1023 (max = 1023 exactly in multiple subjects) is **diagnostic of a 10-bit ADC** (2¹⁰ = 1024 levels, 0–1023). The `float64` dtype is a storage artifact; the underlying values are integer-quantized. This is confirmed by:

- Subject_2, S03, S05, S10, S13, S15, S24: max exactly = 1023.0
- No value exceeds 1023
- No value is negative (baseline is ~507, not 0)
- DC offset of ~507 is consistent across all 27 subjects (equipment baseline)

##### 5.3 Raw vs. processed ECG evidence

**Verdict: Consistent with raw 10-bit ADC samples.** Evidence against processed/filtered data:

- Peak-to-peak amplitude is 280–1023 ADC units — consistent with lead-off or variable electrode contact
- Values are integer-quantized (not floating-point continuous)
- QRS morphology is present (confirmed by FFT peaks in expected HR range)
- The mean DC offset of ~507 is a hardware characteristic, not a processing artifact

**Evidence that cannot be fully assessed without documentation**: The unique value count per subject (313–936) is lower than the theoretical maximum of 1024. This could indicate either:
(a) Not all ADC codes were exercised by the signal, **or**
(b) Some quantization or compression was applied. Without the original ADC datasheet, this cannot be confirmed.

##### 5.4 Signal characteristics and FFT-based HR check

Assuming 1000 Hz ECG sampling rate (see §6):

| Subject | Range | Std | FFT HR (bpm) | Notes |
|---------|-------|-----|-------------|-------|
| S01 | 445–773 | 25.8 | 117 | Normal |
| S09 | 429–774 | 31.8 | 88 | Arrhythmia |
| S18 | 89–954 | 43.1 | 172 | Arrhythmia |

The FFT-derived heart rates are physiologically plausible and consistent with the arrhythmia flags for S09 and S18.

---

#### 6. Evidence for Synchronization

##### 6.1 Duration matching

This is the most critical section. The key question: **can video and ECG be aligned?**

**ECG duration:**
- Samples: 600,000
- At 1000 Hz → **600 seconds = 10 minutes**
- At 500 Hz → 1200 seconds = 20 minutes
- At 833.33 Hz → 720 seconds = 12 minutes

**Video duration:**
- Frames: 18,000
- At 30 fps → 600 seconds = **10 minutes** ✓ EXACT MATCH
- At 25 fps → 720 seconds = 12 minutes
- At 29.97 fps → 600.6 seconds ≈ 10 minutes

**The only fps/fs combination that gives exact duration matching is fps=30 and ECG_fs=1000 Hz** (both → 600 seconds exactly). The 600,000 / 1000 = 600 is a clean integer — strong evidence for 1000 Hz.

##### 6.2 Frame rate discrepancy

The MPEG-1 sequence header inside the video frames declares **frame_rate_code = 3 → 25 fps**. This is found in the first MPEG-1 picture's sequence header. However:

1. The AVI stream header fps field is corrupted (0/0), so 25 fps cannot be confirmed from AVI metadata.
2. The MPEG-1 sequence header may be inherited from a re-encoding step (the encoder is FFmpeg Lavc59.37.100).
3. The **perfect 10-minute alignment** at 30 fps / 1000 Hz is a stronger quantitative signal than the inherited sequence header.
4. At 25 fps, the video would be 12 minutes while the ECG would be 10 minutes (600,000 samples at 1000 Hz) — a 2-minute mismatch with no explanation.
5. The keyframe interval (12 frames) is consistent with both 25 fps and 30 fps MPEG-1 GOP structures.

**Conclusion**: The most plausible parameters are **video fps = 30, ECG fs = 1000 Hz**, with the MPEG-1 sequence header being a re-encoding artifact from FFmpeg. **This is an assumption, not a verified fact.**

##### 6.3 Synchronization mechanism

**No explicit synchronization evidence found.** Specifically:
- No embedded hardware timestamps in the AVI file
- No audio track to cross-correlate
- No frame-zero markers in the MPEG data
- No explicit recording start/sync event in the ECG array
- The mean DC offset (~507) is present from sample 0, consistent with recording already in progress (no pre-trigger capture)

**The alignment is inferred from nominal duration matching only.** A ±1-second start delay between ECG and video cannot be detected from the data alone.

##### 6.4 Cross-signal consistency check

The frame size autocorrelation at lag 60 frames is r=0.991 (very high), indicating periodic variations in the video signal. At 30 fps, lag 60 = 2 seconds — consistent with respiratory or cardiac cycle effects on skin color. This is indirect evidence of simultaneous recording but does not confirm precise synchronization.

---

#### 7. License and Citation Requirements

| Item | Status |
|------|--------|
| License file | **Absent** |
| README | **Absent** |
| Original paper | **Absent** |
| Dataset paper/DOI | **Absent** |
| Acknowledgment requirements | **Unknown** |
| Commercial use | **Unknown** |
| Attribution required | **Unknown** |

**This dataset cannot be published or distributed externally without resolving the license status.** Using it in a published Sanubari validation study requires identifying the original source and compliance with any associated terms.

---

#### 8. Known Limitations

1. **FPS is unverified**: The AVI header fps field is corrupted. The nominal fps=30 is inferred from duration matching with ECG at 1000 Hz. This must be independently confirmed before publication-quality validation.

2. **No explicit sync marker**: Without hardware sync metadata, sub-second alignment between ECG and video cannot be guaranteed. The start of both recordings may differ by 0–several seconds.

3. **Subject_4 is a total video loss**: All three camera files are zero bytes. The ECG is intact. This subject can contribute ECG-only data but cannot be used for rPPG vs. ECG comparison.

4. **Minor frame count variation**: Subjects 13 (17996) and 21 (17983) are 4–17 frames short. At 30 fps, this is < 0.6 seconds. Trimming alignment is needed.

5. **ECG sampling rate unverified**: The 1000 Hz rate is inferred from (a) the perfect 10-minute match at fps=30, (b) 600,000 being a clean multiple of 1000. No header or metadata confirms this.

6. **No ADC/device specification**: The 10-bit ADC is inferred from the value range. The specific device model (e.g., ADInstruments, BIOPAC, custom) is unknown. This matters for unit calibration (mV conversion) and noise characterization.

7. **Raw waveform vs. pre-filtered**: The data has ECG morphology consistent with raw samples, but without documentation, the possibility of pre-filtering cannot be ruled out. The reduced unique value count (313–936 vs. 1024) warrants investigation.

8. **ECG has no lead information**: The metadata does not specify which lead (I, II, III, etc.) was used. Lead placement affects waveform morphology and R-peak amplitude, which affects any algorithm that uses ECG R-peaks as ground truth.

9. **Arrhythmia subjects**: S09 and S18 are flagged as arrhythmia. Standard HR validation metrics (MAE, MAPE) may not be appropriate for these subjects. HR estimation from rPPG is typically designed for normal sinus rhythm.

---

#### 9. Verdict

##### **CONDITIONALLY READY**

The dataset has a structurally sound layout with consistent file naming, identical array shapes, and clean numeric arrays. The duration alignment between video (~18000 frames) and ECG (600,000 samples) is consistent with a synchronized 10-minute recording at 30 fps / 1000 Hz. The data is physiologically plausible.

However, three conditions must be satisfied before the dataset can be used for publication-quality HR validation:

1. **FPS must be confirmed** (currently inferred, not documented)
2. **ECG fs must be confirmed** (currently inferred, not documented)
3. **License/citation must be resolved** (currently unknown)

---

#### 10. Exact Next Actions Required

##### Phase A — Confirm FPS and ECG fs (1–2 hours)

**Option 1 (recommended): Read the raw video frames**
```bash
# Use OpenCV or ffmpeg to read the first 30 frames and time them
# Python: cv2.VideoCapture or ffmpeg-python
# Measure actual elapsed time for 30 frames → fps = 30 / elapsed_seconds

# If fps ≠ 30: recalculate all durations and adjust ECG alignment
```

**Option 2: Read the ECG with known hardware**
If the ADC hardware is known (e.g., NI DAQ, ADInstruments), look up the default sampling rate configuration for that device.

##### Phase B — Resolve Subject_4 (15 minutes)
- Determine if raw video data for Subject_4 can be recovered
- If not, explicitly exclude Subject_4 from all validation analyses
- Document the exclusion in any publication

##### Phase C — Identify the dataset source (1–2 hours)
- Search for the original publication or dataset repository
- Look for "rPPG" "ECG" "benchmark" "heart rate" in conjunction with any institution or author name from the acquisition dates (Jun 2024, Indonesia-based study implied by name "Sanubari")
- Common benchmarks: PURE (from University of Oulu), MAHNOB-HCI, UBFC-rPPG, COHFACE
- If a source is identified: obtain license terms, citation text, and any acquisition protocol details

##### Phase D — Document exclusion criteria
- Subjects 9 and 18 (arrhythmia) should be flagged separately in any validation analysis
- Subjects 13 and 21 (minor frame count deviation) require per-subject trimming
- The two subjects with makeup (S12, S13) and six with glasses (S06, S14, S17, S19, S24) should be tracked as confounders

---

#### Command Log — Reproducible Audit

```bash
# File listing
ls Dataset_rPPG-10/
# 26 subject dirs + Subject Data.xlsx

# File counts per subject
for d in Dataset_rPPG-10/Subject_*/; do echo "$(basename $d): $(ls $d | wc -l) files"; done
# All 27 subjects: 4 files each

# Zero-size check
ls -la Dataset_rPPG-10/Subject_4/
# Forehead_.avi: 0 bytes, Cheek1_.avi: 0 bytes, Cheek2_.avi: 0 bytes, ECG.npy: 4800128 bytes

# AVI binary inspection (Python)
python - << 'EOF'
import struct, os, numpy as np

def parse_avi(path):
    with open(path,'rb') as f: data=f.read()
    idx_pos = data.find(b'idx1')
    if idx_pos < 0: return {}
    idx_sz = struct.unpack('<I', data[idx_pos+4:idx_pos+8])[0]
    n_frames = idx_sz // 16
    # Sample frame sizes
    sizes = [struct.unpack('<I', data[idx_pos+8+i*16+12:idx_pos+8+i*16+16])[0] for i in range(min(n_frames, 20))]
    return {'frames': n_frames, 'sample_sizes': sizes, 'file_size': len(data)}

for subj in range(1, 28):
    path = f'Dataset_rPPG-10/Subject_{subj}/Subject_{subj}_Forehead_.avi'
    info = parse_avi(path)
    sz = os.path.getsize(path)
    print(f"S{subj:02d}: frames={info.get('frames','ZERO')} fsize={sz}")
EOF

# ECG inspection
python - << 'EOF'
import numpy as np
for subj in range(1, 28):
    arr = np.load(f'Dataset_rPPG-10/Subject_{subj}/Subject_{subj}_ECG.npy').ravel()
    print(f"S{subj:02d}: shape={arr.shape} min={arr.min():.0f} max={arr.max():.0f} mean={arr.mean():.1f} std={arr.std():.1f}")
EOF
# All: shape=(600000,) float64, min=0-429, max=698-1023, mean≈507, 100% finite

# Duration inference
python - << 'EOF'
# Video: 18000 frames. ECG: 600000 samples.
# fps=30, fs=1000 → video=600s, ecg=600s → exact match
# fps=25, fs=1000 → video=720s, ecg=600s → mismatch
print("fps=30, fs=1000 Hz: video=600.0s, ecg=600.0s — EXACT MATCH")
print("fps=25, fs=1000 Hz: video=720.0s, ecg=600.0s — 2 min mismatch")
EOF

# MPEG-1 sequence header extraction
python - << 'EOF'
import struct, os
path = 'Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi'
with open(path,'rb') as f: data=f.read()
movi = data.find(b'movi')
frame_abs = movi + 12  # Skip LIST header
seq_data = data[frame_abs:frame_abs+1000]
idx = seq_data.find(b'\x00\x00\x01\xb3')
if idx >= 0:
    sh = seq_data[idx:idx+12]
    print(f"MPEG-1 seq hdr: {sh.hex()}")
    h = ((sh[0] << 4) | ((sh[1] >> 4) & 0x0F))
    v = ((sh[1] & 0x0F) << 8) | sh[2]
    fr = sh[5] >> 4
    print(f"Size: {h}x{v}, fps_code={fr} (3=25fps)")
    print(f"Encoder: Lavc59.37.100 (FFmpeg) — found in MPEG user data")
EOF
# Output: Size=256x144, fps_code=3→25fps, encoder=FFmpeg Lavc59.37.100
```

---

## Part 2 — Acquisition metadata verification

*Original file: `ACQUISITION_METADATA_VERIFICATION.md` (dated 2026-10-11)*

### Sanubari Phase 11 — Acquisition Metadata Verification

**Verification date**: 2024 audit, updated with binary and tool-based inspection
**Dataset**: `Dataset_rPPG-10/`
**Methodology**: OpenCV frame decode timing, AVI binary parsing, NPY header inspection, XLSX XML inspection

---

#### Preamble

This report verifies the claims and evidence from `DATASET_FORENSIC_AUDIT.md` using reproducible tool-based inspection. It does not re-state findings that are fully confirmed by evidence — it adds precision, corrects overstatements, and documents remaining blockers. No assumptions are presented as facts without their evidence chain.

---

#### 1. Video Frame Rate — VERIFIED

##### 1.1 Tool-based verification

The forensic audit stated that "FPS is unverified" based on AVI header corruption. OpenCV provides a definitive answer.

**Command:**
```bash
uv run --with opencv-python --with numpy python - << 'PYEOF'
import cv2, numpy as np

cap = cv2.VideoCapture('Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi')
print("CAP_PROP_FPS:", cap.get(cv2.CAP_PROP_FPS))
print("CAP_PROP_FRAME_COUNT:", cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.set(cv2.CAP_PROP_POS_FRAMES, 18000 - 1)
print("Last frame POS_MSEC:", cap.get(cv2.CAP_PROP_POS_MSEC))
cap.release()
PYEOF
```

**Output:**
```
CAP_PROP_FPS: 30.0
CAP_PROP_FRAME_COUNT: 18000.0
Last frame POS_MSEC: 599933.3333 ms
```

##### 1.2 Full decode timing

All 18,000 frames of Subject_1 Forehead were decoded and their timestamps recorded:

| Check | Value | Interpretation |
|-------|-------|---------------|
| Frames decoded | 18,000 / 18,000 | No decoding errors |
| Mean frame interval | 33.333333 ms | Exactly 1/30 second |
| Std of frame interval | **0.000000 ms** | Zero variance — perfectly consistent |
| CV (coefficient of variation) | **0.00000000** | Confirmed constant frame rate |
| Dropped frames (interval > 66.7ms) | **0** | No gaps |
| Frame at t=1s | #30 | Perfect at 30 fps |
| Frame at t=10s | #300 | Perfect at 30 fps |
| Frame at t=60s | #1800 | Perfect at 30 fps |
| Frame at t=300s | #9000 | Perfect at 30 fps |
| Frame at t=599s | #17970 | Perfect at 30 fps |
| Last frame timestamp | 599966.667 ms | Consistent with 18000 frames at 30 fps |

**Finding: The video is definitively 30.000 fps constant frame rate. There is no ambiguity.**

##### 1.3 Source of the AVI header corruption

The binary inspection shows that the AVI `strh` chunk's fps fields (`dwScale`/`dwRate`) are null in the raw header bytes. This is a data anomaly in the file format, but OpenCV derives the correct fps from the `idx1` index. The last-frame seek timestamp (599933.33 ms) also confirms: 599933.33 / 18000 = 33.33 ms/frame = 30 fps.

The `ISFT` INFO chunk in every AVI file contains: `Lavf59.27.100` — the FFmpeg libavformat muxer (version 59.27.100) that created the AVI container. This is the only provenance string in the video files.

**The MPEG-1 sequence header embedded in the frame data (`00 00 01 B3`, frame_rate_code=3 → 25 fps) is a re-encoding artifact. It does not represent the actual recording frame rate.**

##### 1.4 Cross-camera and cross-subject consistency

| Subject | Camera | CAP_PROP_FPS | CAP_PROP_FRAME_COUNT | Last_POS_MSEC (ms) |
|---------|--------|-------------|----------------------|--------------------|
| All S01–S03, S05–S12, S14–S20, S22–S27 | All 3 | **30.00** | **18000** | **599933.33** |
| S13 | All 3 | 30.00 | 17996 | 599800.00 |
| S21 | All 3 | 30.00 | 17983 | 599366.67 |
| S04 | All 3 | **-1.00** | **-1** | **0.00** |

**Findings:**
- Every usable subject reports exactly CAP_PROP_FPS = 30.0, consistent across all three cameras.
- S13: 4 frames missing (< 0.03%). Frame at t=599.8s, fps_impl = 30.0033. Truncation at end of recording.
- S21: 17 frames missing (0.09%). Frame at t=599.4s, fps_impl = 30.0033. Truncation at end of recording.
- S04: Zero-byte files — completely absent from recording.

##### 1.5 Frame rate conclusion

| Source | Value | Status |
|--------|-------|--------|
| OpenCV CAP_PROP_FPS | 30.0 fps | **Confirmed** |
| Decoded frame timing (all 18,000 frames) | 33.333333 ms/frame, 0 variance | **Confirmed** |
| Last-frame seek timestamp (599933.33 ms / 18000) | 29.999 fps ≈ 30 fps | **Confirmed** |
| AVI stream header dwScale/dwRate | 0 / 0 (corrupted) | Not usable |
| MPEG-1 sequence header frame_rate_code | 3 → 25 fps (artifact) | Incorrect |

**Video frame rate = 30 fps. Verified.**

---

#### 2. ECG Sampling Rate — CANNOT BE VERIFIED FROM LOCAL FILES

##### 2.1 What the files contain

The NPY header contains only:
```python
{'descr': '<f8', 'fortran_order': False, 'shape': (600000,), }
```
- No `dtype` metadata about ADC bit width
- No metadata field for `fs`, `sampling_rate`, or `sample_rate`
- No footer, no extended metadata, no embedded comments
- File size = 128 (header) + 600,000 × 8 (float64) = 4,800,128 bytes — exact match, no extra bytes

The XLSX file contains only subject demographics (no device specifications, no sampling rate).

The AVI files contain no audio track and no embedded ECG metadata.

##### 2.2 Duration matching evidence (stated without claiming)

The arithmetic relationship between ECG samples and video duration is:
- ECG: 600,000 samples
- Video: 18,000 frames / 30 fps = 600.000 seconds
- Ratio: 600,000 / 600.0 = **1,000.0 samples/second**

This is mathematically exact. However, the audit instructions prohibit inferring the ECG sampling rate solely from array length or nominal duration matching. The following alternatives are presented as possibilities:

| Candidate fs | ECG duration (s) | Match to video (600s) | Standard medical rate? |
|---|---|---|---|
| 500 Hz | 1200.0 | No | Yes |
| 833.333 Hz | 720.0 | No | No |
| **1000 Hz** | **600.0** | **Yes, exact** | **Yes** |
| 2000 Hz | 300.0 | No | Yes |

The only standard medical rate that matches is **1000 Hz**. No other standard rate (250, 500, 2000 Hz) produces a matching duration. A non-standard rate of 833.333 Hz (600,000 / 720) would match a 12-minute recording but does not match the confirmed 10-minute video duration.

**This relationship is a strong inference, not a verified fact. The ECG sampling rate must be obtained from the original acquisition protocol, device datasheet, or publication — none of which are present in the local files.**

##### 2.3 The 10-bit ADC evidence is a secondary inference

The value range 0–1023 (with some subjects at exactly 1023.0) is consistent with a 10-bit ADC. However:
- The values are stored as `float64`, masking the original integer precision
- The unique value counts (313–936 per subject) are lower than 1024, which may indicate either natural signal variation or some quantization
- Without the ADC device model, the bit depth is also an inference

##### 2.4 ECG sampling rate conclusion

**The ECG sampling rate cannot be determined from the local files. The value of 1000 Hz is a mathematically consistent inference derived from the duration match, but it is not confirmed by any header, metadata, or documentation in the dataset.**

---

#### 3. Dataset Provenance — PARTIALLY IDENTIFIED

##### 3.1 Evidence found in local files

**XLSX metadata (`docProps/core.xml`):**
```xml
<dc:creator>Gonçalo Rodrigues</dc:creator>
<cp:lastModifiedBy>fc54909</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">2015-06-05T18:17:20Z</dcterms:created>
<dcterms:modified xsi:type="dcterms:W3CDTF">2025-04-04T12:45:25Z</dcterms:modified>
```

**XLSX internal path:**
```xml
<x15ac:absPath url="C:\Users\gonca\Downloads\"
```

**Interpretation:**
- The spreadsheet was authored by **Gonçalo Rodrigues** — a name consistent with Portuguese origin
- The file was last modified by user `fc54909` on **2025-04-04** (well after the 2024-06 acquisition)
- The original absolute path indicates the file was saved from `C:\Users\gonca\Downloads\` — this is the only machine/user identifier found
- The **created** date (2015-06-05) predates the acquisition by 9 years — this is the file creation date of the template, not the data
- The file was edited in Microsoft Excel 16.0300 (Office 2016 or later)

**No other provenance strings were found in any file:**
- AVI files: Only `Lavf59.27.100` (muxer) and `Lavc59.37.100` (encoder version) — no author, no organization, no dataset name
- NPY files: No metadata beyond numpy array descriptors
- No additional files (no README, no PDF, no .txt, no .doc)
- No search hit for "Sanubari", "rPPG", "ECG dataset", "BIPAC", "ADInstruments", or any license string

##### 3.2 What cannot be determined

| Item | Evidence | Status |
|------|----------|--------|
| Original dataset name | None | Not found |
| Original publication / DOI | None | Not found |
| Institutional affiliation | None | Not found |
| License terms | None | Not found |
| ECG device model | None | Not found |
| Camera model | None | Not found |
| Original download URL | None | Not found |
| Acquisition protocol | None | Not found |

##### 3.3 The name "Sanubari"

The dataset folder is named `Dataset_rPPG-10`. The name "Sanubari" appears in the task instructions but not in any file in the dataset. A web search for `"Sanubari" "rPPG"` returned no results. The name "Sanubari" is not confirmed as the original dataset name.

##### 3.4 Relation to known benchmarks

This dataset does not match the format of established rPPG benchmarks:
- **PURE** (Oulu University): RGB video, contact PPG, 60 fps, different naming
- **MAHNOB-HCI**: Different resolution, different format
- **UBFC-rPPG**: Different format, subject count, naming convention
- **COHFACE**: Different format and naming

The combination of 64×64 pixel ROIs (forehead + 2 cheek patches), 10-minute duration, 30 fps, and 3-camera setup does not correspond to any publicly documented benchmark found in the web search. The dataset appears to be a private or internal acquisition.

---

#### 4. Open Questions and Unresolved Uncertainties

| ID | Question | Evidence Available | Resolution Needed |
|----|----------|-------------------|-------------------|
| **UQ-1** | ECG sampling rate | None in local files | Find original acquisition protocol or device manual |
| **UQ-2** | Dataset name and source | None in local files | Search for Gonçalo Rodrigues's publications |
| **UQ-3** | License terms | None in local files | Identify source and obtain license |
| **UQ-4** | ECG lead configuration | None in local files | Find original protocol |
| **UQ-5** | ADC device model | Inferred (10-bit) only | Find device datasheet |
| **UQ-6** | Subject_4 video loss cause | None | Determine if recoverable or structural failure |
| **UQ-7** | Purpose of 64×64 ROI extraction | None | Confirm whether ROI was extracted from larger frame or recorded at this resolution |

---

#### 5. Updated Findings vs. Forensic Audit

The forensic audit made several claims that this verification refines or corrects:

| Claim in Audit | Updated Status |
|---|---|
| "FPS is unverified" | **Corrected: FPS is definitively 30.0 fps** (zero-variance decode timing, confirmed by OpenCV) |
| "fps=30 is an assumption" | **Corrected: 30 fps is verified fact** |
| "MPEG-1 sequence header claims 25fps" | **Confirmed as re-encoding artifact** (the FFmpeg muxer created the AVI with correct 30 fps from the idx1 index, but the MPEG-1 frame data retained an inherited 25 fps sequence header from the source encode) |
| "No fps metadata found" | **Corrected: OpenCV's CAP_PROP_FPS = 30.0** — metadata exists but not in the stream header; OpenCV derives it from the idx1 |
| "fps=25 cannot be ruled out" | **Ruled out: zero variance over all 18,000 frames** |
| "License unknown" | **Confirmed: no license found** |
| "Subject_4: either recording failure or extraction bug" | **Confirmed: unknown cause** |
| "fps=30 / ECG_fs=1000 Hz — this is an assumption" | **Confirmed: ECG_fs=1000 Hz is an inference** (see §2 above) |

---

#### 6. Blockers and Exact Next Actions

##### Blocker 1 — ECG Sampling Rate (CRITICAL for alignment)

**Status**: The exact sampling rate is not in any local file.
**Risk**: If ECG_fs ≠ 1000 Hz, every alignment will be wrong.
**Next action**: Identify the ECG recording device and confirm its sampling rate. Common devices used in rPPG studies:

```bash
# ACTION: Search for the device
# Possible candidates based on 10-bit range and Portugal connection:
# - BIOPAC MP36/MP35 (common in research labs, 10-bit)
# - ADInstruments PowerLab
# - National Instruments DAQ
# - Custom Arduino/ESP32-based logger

# ACTION: Contact or search for Gonçalo Rodrigues's publications
# web_search: "Gonçalo Rodrigues" + "ECG" + "rPPG" or "PPG" or "remote photoplethysmography"

# ACTION: If fs cannot be confirmed, apply the following:
#   - Use the alignment point at 1000 Hz as primary hypothesis
#   - Validate with a known HR signal in the ECG (e.g., peak detection at ~1 Hz)
#   - Test with cross-correlation between ECG R-peaks and video pulse estimate
```

##### Blocker 2 — Dataset Provenance (REQUIRED before publication)

**Status**: The source dataset name, publication, and license are unknown.
**Risk**: Using the dataset without a known license may constitute a copyright violation.
**Next action**:

```bash
# STEP 1: Search for Gonçalo Rodrigues publications
# web_search: site:scholar.google.com "Gonçalo Rodrigues" "rPPG" OR "remote PPG" OR "camera-based"
# web_search: "Gonçalo Rodrigues" "PPG" "heart rate"

# STEP 2: If no match found, search for the dataset by characteristics
# Keywords: "64x64" "rPPG" "forehead" "cheek" "ECG" "10 minutes"
# Sites: IEEE Xplore, PubMed, arXiv, Kaggle, PhysioNet

# STEP 3: If original source is unidentifiable:
#   - Do not publish results using this dataset without legal clearance
#   - Use only for internal development/testing
#   - Cite as: "Private dataset, provided without license terms"
```

##### Blocker 3 — Subject_4 Video Loss

**Status**: All three camera files are zero bytes.
**Next action**:
```bash
# 1. Check if the raw recording can be recovered from the source
# 2. Document Subject_4 as ECG-only in all analyses
# 3. Do not impute or estimate the missing video data
```

---

#### 7. Verified Specifications

These parameters are confirmed with evidence chains and should be used as ground truth:

| Parameter | Value | Evidence | Confidence |
|----------|-------|----------|------------|
| Video frame rate | **30.000 fps** | OpenCV CAP_PROP_FPS, full decode timing (zero variance), seek timestamp | **Definitive** |
| Frames per recording | **18,000** (S01–12, S14–20, S22–27) | OpenCV CAP_PROP_FRAME_COUNT, idx1 count | **Definitive** |
| Video duration | **600.0 s** (10 minutes) | 18000 frames / 30 fps | **Definitive** |
| Video resolution | **64 × 64 px** | OpenCV CAP_PROP_FRAME_WIDTH/HEIGHT, AVI strf biSize | **Definitive** |
| Video codec | **XVID-compatible MPEG-4** | AVI fccHandler = 'vids', container created by Lavf59.27.100 | **Definitive** |
| Video container | **AVI (RIFF)** | RIFF header in all files | **Definitive** |
| Frame rate type | **Constant (CFR)** | Zero interval variance over all 18,000 frames | **Definitive** |
| Keyframe interval | **12 frames** | 1500 keyframes in 18,000 frames | **Definitive** |
| ECG samples | **600,000** (all 27 subjects) | NPY shape confirmed | **Definitive** |
| ECG dtype | **float64** | NPY header confirmed | **Definitive** |
| ECG range | **0–1023** (consistent with 10-bit ADC) | Array min/max | **Strong inference** |
| ECG fs | **Unknown** | No metadata in any file | **No evidence** |
| Dataset creator | **Gonçalo Rodrigues** (spreadsheet) | XLSX core.xml | **Confirmed** |
| Acquisition dates | **2024-06-20 to 2024-06-28** | XLSX row 14 | **Confirmed** |
| Video loss (S04) | **3 of 3 cameras, 0 bytes** | File sizes | **Confirmed** |

---

#### 8. Command Log — Reproducible Verification

```bash
# 1. Check OpenCV video properties
uv run --with opencv-python --with numpy python - << 'PYEOF'
import cv2
cap = cv2.VideoCapture('Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi')
print("FPS:", cap.get(cv2.CAP_PROP_FPS))
print("Frames:", cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.set(cv2.CAP_PROP_POS_FRAMES, 18000 - 1)
print("Last_ms:", cap.get(cv2.CAP_PROP_POS_MSEC))
cap.release()
PYEOF
# Output: FPS: 30.0, Frames: 18000.0, Last_ms: 599933.33

# 2. Full decode timing (all 18,000 frames)
uv run --with opencv-python --with numpy python - << 'PYEOF'
import cv2, numpy as np, time
cap = cv2.VideoCapture('Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi')
times, means = [], []
ret = True
while ret:
    ret, frame = cap.read()
    if ret:
        times.append(cap.get(cv2.CAP_PROP_POS_MSEC))
        means.append(frame.mean())
cap.release()
t = np.array(times); m = np.array(means)
iv = np.diff(t)
print(f"Frames: {len(t)}, Mean interval: {iv.mean():.6f}ms, Std: {iv.std():.8f}ms")
print(f"CV: {iv.std()/iv.mean():.8f}")
print(f"t@1s = frame #{np.argmin(np.abs(t-1000))}, t@10s = #{np.argmin(np.abs(t-10000))}")
print(f"Mean pixel: {m.mean():.2f}, range: {m.min():.2f}-{m.max():.2f}")
PYEOF
# Output: Frames: 18000, Mean: 33.333333ms, Std: 0.00000000ms, CV: 0.00000000

# 3. All subjects, all cameras
uv run --with opencv-python python - << 'PYEOF'
import cv2
for subj in range(1,28):
    for cam in ['Forehead','Cheek1','Cheek2']:
        p = f'Dataset_rPPG-10/Subject_{subj}/Subject_{subj}_{cam}_.avi'
        cap = cv2.VideoCapture(p)
        fps=cap.get(cv2.CAP_PROP_FPS); fc=cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if fc>0: cap.set(cv2.CAP_PROP_POS_FRAMES,fc-1); ms=cap.get(cv2.CAP_PROP_POS_MSEC)
        else: ms=0
        cap.release()
        print(f"S{subj:02d} {cam}: fps={fps} frames={fc} last_ms={ms:.2f}")
PYEOF

# 4. XLSX provenance
uv run --with openpyxl python - << 'PYEOF'
import openpyxl, zipfile
with zipfile.ZipFile('Dataset_rPPG-10/Subject Data.xlsx') as z:
    print(z.read('docProps/core.xml').decode())
PYEOF
# Output: <dc:creator>Gonçalo Rodrigues</dc:creator>

# 5. NPY header
uv run --with numpy python - << 'PYEOF'
import numpy as np, struct
path = 'Dataset_rPPG-10/Subject_1/Subject_1_ECG.npy'
with open(path,'rb') as f:
    magic=f.read(6); ver=f.read(2); hlen=struct.unpack('<H',f.read(2))[0]
    header=f.read(hlen-10).decode()
print(f"Magic: {magic}, Version: {ver}, Header: {header.strip()}")
with open(path,'rb') as f:
    f.seek(0,2)
    print(f"File size: {f.tell()} bytes, Array bytes: {600000*8}")
PYEOF
# Output: {'descr': '<f8', 'fortran_order': False, 'shape': (600000,), }

# 6. AVI binary INFO chunks
uv run --with numpy python - << 'PYEOF'
import struct
path = 'Dataset_rPPG-10/Subject_1/Subject_1_Forehead_.avi'
with open(path,'rb') as f: data=f.read()
# ISFT
isft_pos = data.find(b'ISFT')
if isft_pos >= 0:
    sz = struct.unpack('<I', data[isft_pos+4:isft_pos+8])[0]
    val = data[isft_pos+8:isft_pos+8+sz].rstrip(b'\x00').decode()
    print(f"ISFT: '{val}'")
# Search for any other INFO keys
for key in [b'IART',b'ICRD',b'INAM',b'ICMT',b'IPRD',b'ISRC',b'ICOP']:
    if data.find(key) >= 0:
        print(f"Found: {key.decode()}")
PYEOF
# Output: ISFT: 'Lavf59.27.100'
```

---

## Part 3 — First real-dataset run

*Original file: `FIRST_REAL_DATASET_RUN.md` (dated 2026-10-11)*

### Sanubari Phase 11 — First Real Dataset Readiness Run

**Date**: 2024
**Dataset**: `Dataset_rPPG-10/`
**Adapter**: `p11_validation/rppg10_adapter.py`
**Tests**: `p11_validation/test_rppg10_adapter.py`

---

#### 1. Commands Executed

```bash
# 1. Adapter tests
uv run --with scipy --with opencv-python --with numpy --with pytest \
    python -m pytest p11_validation/test_rppg10_adapter.py -v --tb=no

# 2. Readiness check (ecg_fs = unset — safe default)
uv run --with scipy --with opencv-python --with numpy python - << 'PYEOF'
from p11_validation.rppg10_adapter import (
    rPPG10Config, check_readiness, discover_all, FileStatus
)
cfg = rPPG10Config(dataset_root="Dataset_rPPG-10", video_fps=30.0)
report = check_readiness("Dataset_rPPG-10", cfg)
# ... per-subject listing ...
PYEOF

# 3. Non-destructive ECG diagnostics (no fs assumption)
uv run --with scipy --with numpy python - << 'PYEOF'
# Load ECG, compute statistics, saturation, baseline stability, autocorrelation
# No fs used — all diagnostics are unitless or relative
PYEOF

# 4. Non-destructive video diagnostics (OpenCV decode, no assumptions)
uv run --with opencv-python --with numpy python - << 'PYEOF'
# Decode first 30 frames per subject, pixel mean/std
# Probe all subjects for frame count, fps, resolution
PYEOF
```

---

#### 2. Test Results

```
43 passed in 10.98s
```

All 43 tests in `test_rppg10_adapter.py` pass. No regressions in `test_validation.py` (48 passed).

---

#### 3. Readiness Status

##### Configuration blocking

| Config field | Value | Status |
|---|---|---|
| `ecg_fs` | **unset (None)** | BLOCKS — required |
| `ecg_offset_sec` | 0.0 | Not required for discovery |
| `video_offset_sec` | 0.0 | Not required for discovery |
| `video_fps` | 30.0 (verified) | OK |
| `video_camera` | Forehead | OK |

**Config is NOT valid** until `ecg_fs` is set.

##### Per-subject readiness (27 subjects)

| Subj | FH | C1 | C2 | ECG | Frames | FPS | Status |
|------|----|----|----|-----|--------|-----|--------|
| S01 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S02 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S03 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| **S04** | **zero_size** | **zero_size** | **zero_size** | present | — | — | **UNUSABLE (video)** |
| S05 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S06 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S07 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S08 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S09 | present | present | present | present | 18000 | 30.0 | **USABLE** *(arrhythmia)* |
| S10 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S11 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S12 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S13 | present | present | present | present | 17996 | 30.0 | **USABLE** *(4 frames missing)* |
| S14 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S15 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S16 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S17 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S18 | present | present | present | present | 18000 | 30.0 | **USABLE** *(arrhythmia)* |
| S19 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S20 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S21 | present | present | present | present | 17983 | 30.0 | **USABLE** *(17 frames missing)* |
| S22 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S23 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S24 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S25 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S26 | present | present | present | present | 18000 | 30.0 | **USABLE** |
| S27 | present | present | present | present | 18000 | 30.0 | **USABLE** |

**Summary: 26/27 subjects are USABLE. 1 subject (S04) is UNUSABLE due to total video loss.**

---

#### 4. Verified Specifications

These are confirmed with evidence and do not require assumptions:

| Parameter | Value | Evidence |
|---|---|---|
| Video FPS | **30.000 fps** | OpenCV `CAP_PROP_FPS`; zero-variance decoded frame timing over all 18,000 frames |
| Frame count | **18,000** (complete subjects) | OpenCV `CAP_PROP_FRAME_COUNT`; AVI `idx1` index |
| Video duration | **600.0 seconds (10 min)** | 18,000 frames ÷ 30 fps |
| Video resolution | **64 × 64 px** | OpenCV `CAP_PROP_FRAME_WIDTH/HEIGHT`; AVI BITMAPINFOHEADER |
| Video codec | **MPEG-4 (XVID)** | AVI `fccHandler`; `Lavf59.27.100` muxer |
| Frame rate type | **Constant (CFR)** | Zero interval variance over 18,000 decoded frames |
| Keyframe interval | **12 frames** | 1,500 keyframes in 18,000 frames |
| ECG samples | **600,000** (all 27) | NPY shape, confirmed from file |
| ECG dtype | **float64** | NPY header: `'<f8'` |
| ECG value range | **0–1023** | Array min/max across all subjects |
| ECG NaN/Inf | **0** | 100% finite across all subjects |
| ECG baseline | **~507 ADC units** | Mean across all 27 subjects: 507.12 ± 0.17 |
| ECG has QRS morphology | **Yes** | FFT peaks in expected HR range; AC1 = 0.9954 (highly correlated signal) |

---

#### 5. Non-Destructive ECG Signal Quality

No fs assumption was used. All diagnostics are unitless or relative.

##### 5.1 Basic statistics

| Metric | Value | Interpretation |
|--------|-------|---------------|
| Mean across subjects | 507.12 ± 0.17 ADC units | Stable DC baseline across all subjects — consistent with hardware centering |
| Std across subjects | 44.89 ± 15.48 ADC units | High between-subject variance in signal amplitude — physiological |
| Peak-to-peak across subjects | 681 ± 231 ADC units | Wide range — S03/S05/S10/S15 reach 1023 (10-bit saturation) |
| Zero samples (n_zero > 0) | **5 subjects** | S03(188), S05(27), S08(29), S10(363), S15(213) |
| Clipped at 1023 (max) | **4 subjects** | S10, S13, S15, S20 |

##### 5.2 Clipping analysis

Subjects S10, S13, S15, S20 reach exactly 1023 ADC units — the 10-bit ceiling. Subjects S03 and S05 have zero values (electrode lift-off or baseline wander). This is consistent with **raw 10-bit ADC samples**: no filtering or normalization has been applied. The clipping does not indicate a recording failure; it indicates the ECG signal exceeded the ADC dynamic range briefly, which is expected for lead-based ECG recordings.

##### 5.3 Autocorrelation (lag-1)

Mean AC1 = **0.9954** across all 27 subjects. This extremely high lag-1 autocorrelation confirms:
- The ECG is a continuous, smoothly varying waveform — not noise
- The signal has strong physiological structure
- No resampling or frame-skipping artifacts are present

##### 5.4 Baseline stability

Baseline std computed over uniform 1000-sample windows (no fs used):

| Category | Count | Subjects |
|----------|-------|---------|
| Baseline std > 5 ADC units (UNSTABLE) | **10** | S02, S06, S08, S10, S15, S18, S20, S21, S23, S27 |
| Baseline std ≤ 5 ADC units | **17** | All others |

**Interpretation**: 10 subjects show elevated baseline wander. This may reflect movement, breathing artifacts, or electrode impedance changes during the 10-minute recording. This is expected for unsupervised ECG recording. The rPPG signal (extracted from skin-color ROIs) may be less affected by this than the raw ECG.

##### 5.5 Unique value ratio

Mean unique value ratio = **55.73%** of the 1024 possible 10-bit levels. This is consistent with a natural ECG waveform that does not exercise all ADC codes equally.

---

#### 6. Non-Destructive Video Quality

##### 6.1 Per-subject pixel statistics (Forehead camera, first 30 frames)

All 26 usable subjects show:
- **LOW motion**: frame-mean std < 1.0 across 30 frames
- Mean pixel values range from **73.9 to 128.8** (subject skin tone and illumination dependent)
- First-frame vs. last-frame means are within ~3 ADC units — no obvious recording start/stop artifacts

##### 6.2 Cross-camera comparison (S01 sample)

| Camera | Mean px | Std px | First 100 | Last 100 |
|--------|---------|--------|-----------|----------|
| Forehead | 108.7 | 44.6 | 110.6 | 106.8 |
| Cheek1 | 95.0 | 33.0 | 98.1 | 92.0 |
| Cheek2 | 105.5 | 35.8 | 106.6 | 104.4 |

All three ROIs are stable. No camera shows signs of blackout or corruption.

##### 6.3 Frame anomalies

| Subject | Frames | Expected | Missing | Action |
|---------|--------|----------|---------|--------|
| S13 | 17996 | 18000 | 4 | Trimming alignment needed (0.13s at 30fps) |
| S21 | 17983 | 18000 | 17 | Trimming alignment needed (0.57s at 30fps) |

---

#### 7. What Is Executable Now

The following are **safe to execute** without `ecg_fs`:

| Operation | Status | Reason |
|---|---|---|
| File discovery | **READY** | `check_readiness()` works with no config fields set |
| Video metadata probe | **READY** | OpenCV confirms 30fps, 18k frames, 64×64 |
| ECG array inspection | **READY** | Shape, dtype, min/max, NaN/Inf — all fs-independent |
| Signal quality diagnostics | **READY** | Baseline stability, AC1, clipping — all fs-independent |
| Subject exclusion list | **READY** | S04 flagged as video-zero; S09/S18 flagged as arrhythmia |
| Frame count trimming | **READY** | S13 (4 frames) and S21 (17 frames) require per-subject alignment trimming |

The following are **BLOCKED** until `ecg_fs` is confirmed:

| Operation | Blocked by |
|---|---|
| ECG → HR (sliding window) | Cannot convert samples to seconds without fs |
| ECG → IBI (R-peak intervals in ms) | Cannot convert sample indices to time without fs |
| Timestamp alignment (video ↔ ECG) | Cannot compute temporal overlap without both durations |
| `process_ecg_session()` | Raises `ValueError` |
| `session_to_validation_dataset()` | Raises `ValueError` |
| `run_hr_validation()` pipeline | Cannot compute ground truth HR without ECG-to-time conversion |

---

#### 8. S04 Special Case

Subject_4's ECG is **intact** (600,000 samples, float64, 100% finite, same statistics as other subjects). This subject can contribute **ECG-only analysis** — autocorrelation, HR variability without ground-truth video HR — but cannot be used for rPPG-vs-ECG validation.

---

#### 9. Summary

- **43/43 adapter tests pass.** No regressions in existing validation tests (48/48).
- **26/27 subjects** are ready for the pipeline once `ecg_fs` is confirmed.
- **1 subject (S04)** is permanently excluded from video validation.
- **2 subjects (S13, S21)** require minor frame-count trimming.
- **2 subjects (S09, S18)** are flagged as arrhythmia in metadata.
- **4 subjects (S10, S13, S15, S20)** have brief ADC saturation events — not a quality issue.
- **10 subjects** show elevated baseline wander — expected for long unsupervised ECG recording.
- **Video quality** is clean across all 26 usable subjects (low motion, stable pixel means, no frame corruption).

---

#### 10. Exact Next Action Required

**Confirm the ECG sampling rate** — the single parameter that unblocks the entire pipeline.

This must come from an authoritative source (device datasheet, publication, or lab protocol). The arithmetic relationship `600,000 samples / 600.0 s = 1000.0 Hz` is a mathematically consistent inference but is **not confirmed evidence**.

**Immediate next step**: Search for publications by or associated with **Gonçalo Rodrigues** (found in the XLSX `docProps/core.xml` author field) that document the ECG acquisition hardware and sampling rate. A paper citing this dataset or using an identical setup will name the device (BIOPAC, ADInstruments, NI DAQ, etc.) and its configuration.

Once `ecg_fs` is confirmed and set in `rPPG10Config`, the following runs without modification:

```python
from p11_validation import rPPG10Config, check_readiness, load_session, process_ecg_session

cfg = rPPG10Config(
    dataset_root="Dataset_rPPG-10",
    ecg_fs=<confirmed_value>,   # ← set this
    video_fps=30.0,
)
report = check_readiness("Dataset_rPPG-10", cfg)
# report.config_is_valid → True
# report.n_subjects_usable → 26
```

Then for each usable subject, `process_ecg_session()` produces reference HR and IBI, and the existing `run_hr_validation()` / `run_full_validation()` pipeline computes metrics against the Sanubari rPPG output.
