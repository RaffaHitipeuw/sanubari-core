"""
Benchmark: OpticalFlowROIStabilizer per-frame overhead.

Run on a synthetic sequence of 300 frames with three ROI sizes to measure:
- goodFeaturesToTrack() call frequency and time
- calcOpticalFlowPyrLK() time per call
- stabilize() total time per call
- Per-ROI breakdown

Usage:
    uv run python benchmark_stabilize.py [--frames N] [--roi-size WxH]
    uv run python benchmark_stabilize.py --integration --frames 300 --video path/to/video.avi
"""
import argparse
import cv2
import numpy as np
import sys
import os
import time as _time_module
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rppg_signal import (
    OpticalFlowROIStabilizer, reset_instrumentation, get_stabilization_stats,
)


# ---------------------------------------------------------------------------
# Model path validation
# ---------------------------------------------------------------------------
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_MODEL_PATH   = os.path.join(_PROJECT_ROOT, "models", "face_landmarker.task")

def _check_model():
    if not os.path.exists(_MODEL_PATH):
        raise FileNotFoundError(
            f"FaceLandmarker model not found at:\n"
            f"  {_MODEL_PATH}\n\n"
            f"Download it with:\n"
            f"  wget https://storage.googleapis.com/mediapipe-models/"
            f"face_landmarker/face_landmarker/float16/1/"
            f"face_landmarker.task -O models/face_landmarker.task\n\n"
            f"(On Windows: use curl or browser download)\n"
            f"MediaPipe version: 0.10.35  —  requires "
            f"mediapipe.tasks.python.vision.FaceLandmarker"
        )
    return _MODEL_PATH


# ---------------------------------------------------------------------------
# Synthetic helpers
# ---------------------------------------------------------------------------

def synthetic_frame(w, h, offset_x=0, offset_y=0):
    """Create a realistic synthetic frame with texture for feature tracking."""
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    x = np.linspace(0, 4 * np.pi, w)
    y = np.linspace(0, 4 * np.pi, h)
    xx, yy = np.meshgrid(x, y)
    gray = (
        120 +
        30 * np.sin(xx + offset_x) * np.sin(yy + offset_y) +
        15 * np.sin(2 * xx - offset_y) +
        10 * np.random.randn(h, w)
    ).astype(np.uint8)
    frame[:, :, 0] = gray
    frame[:, :, 1] = (gray * 0.9).astype(np.uint8)
    frame[:, :, 2] = (gray * 1.1).clip(0, 255).astype(np.uint8)
    return frame


def make_bbox(x, y, roi_w, roi_h, frame_w, frame_h):
    """Ensure bbox is in-bounds."""
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(frame_w, x + roi_w)
    y2 = min(frame_h, y + roi_h)
    return (x1, y1, x2, y2)


# ---------------------------------------------------------------------------
# Pseudo-landmark helpers (for synthetic-landmarks fallback mode)
# ---------------------------------------------------------------------------

def _PseudoLandmark(x, y, z=0.0):
    """Stand-in for a NormalizedLandmark (MediaPipe landmark protocol)."""
    class _L:
        pass
    l = _L()
    l.x = float(x)
    l.y = float(y)
    l.z = float(z)
    return l


class _PseudoLandmarkList:
    """
    Stand-in for NormalizedLandmarkList from FaceLandmarker.

    Generates a set of 468 face landmarks with anatomically realistic positions and
    slow natural head drift. Specifically calibrated so that:
      - pose_gate (yaw, pitch) is within limits
      - forehead / cheek_left / cheek_right landmarks are in correct face regions
      - GFT has sufficient texture diversity to detect ≥4 features per ROI

    V2 engine ROI landmark indices:
      forehead:   109, 67, 108, 151, 337, 297, 338
      cheek_l:    50,101,118,117,116,123,147,187,207,206,205,36,142,126,100,203
      cheek_r:   280,330,347,346,345,352,376,411,427,426,425,266,371,355,329,423

    Pose gate uses landmarks 1, 10, 152, 234, 454 (nose, nasion, chin, eye corners).
    """
    # Normalized anatomical positions (x, y in [0, 1])
    _KEY_LM = {
        # Pose landmarks
        1:   (0.500, 0.520),   # nose tip
        10:  (0.500, 0.440),  # nasion / glabella
        152: (0.500, 0.650),  # under-nose / chin
        234: (0.380, 0.435),  # left eye outer corner
        454: (0.620, 0.435),  # right eye outer corner
        # Forehead landmarks (above nasion, centered)
        109: (0.520, 0.390),  337: (0.480, 0.390),
        108: (0.500, 0.400),  151: (0.510, 0.410),
        297: (0.490, 0.420),  338: (0.515, 0.400),
        # Cheek left landmarks
        50: (0.360, 0.510), 101: (0.370, 0.500), 118: (0.360, 0.490),
       117: (0.355, 0.480), 116: (0.350, 0.470), 123: (0.345, 0.465),
       147: (0.340, 0.460), 187: (0.335, 0.465), 207: (0.340, 0.470),
       206: (0.350, 0.475), 205: (0.360, 0.480),  36: (0.380, 0.435),
       142: (0.370, 0.455), 126: (0.375, 0.460), 100: (0.365, 0.465),
       203: (0.355, 0.470),
        # Cheek right landmarks
       280: (0.640, 0.510), 330: (0.630, 0.500), 347: (0.640, 0.490),
       346: (0.645, 0.480), 345: (0.650, 0.470), 352: (0.655, 0.465),
       376: (0.660, 0.460), 411: (0.665, 0.465), 427: (0.660, 0.470),
       426: (0.650, 0.475), 425: (0.640, 0.480), 266: (0.620, 0.435),
       371: (0.630, 0.455), 355: (0.625, 0.460), 329: (0.635, 0.465),
       423: (0.645, 0.470),
    }

    def __init__(self, frame_idx, W, H, drift_px=1.0):
        self.landmark = []
        t = frame_idx / 30.0
        # Head drift: ±1 px at 640×480
        dx = drift_px * np.sin(2 * np.pi * 0.3 * t) / W
        dy = drift_px * 0.5 * np.sin(2 * np.pi * 0.5 * t) / H

        # Key landmarks at anatomically correct positions
        for idx in range(468):
            if idx in self._KEY_LM:
                bx, by = self._KEY_LM[idx]
            else:
                # Fill: scatter across the face plane with small jitter
                bx = 0.30 + 0.40 * ((idx + 17) / 468) + 0.005 * np.sin(idx * 3.7 + t)
                by = 0.25 + 0.50 * ((idx + 11) / 468) + 0.005 * np.cos(idx * 2.9 - t)
            self.landmark.append(_PseudoLandmark(bx + dx, by + dy))


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _report_latency(label, values_ms):
    if not values_ms:
        return 0.0, 0.0, 0.0
    arr = np.array(values_ms, dtype=float)
    return float(np.median(arr)), float(np.percentile(arr, 95)), float(np.mean(arr))


# ---------------------------------------------------------------------------
# Synthetic / unit benchmark
# ---------------------------------------------------------------------------

def benchmark_stabilize(roi_configs, n_frames=300, motion_amplitude=3.0):
    """
    Run stabilization benchmark on synthetic frames.

    roi_configs: list of (name, roi_w, roi_h, center_x, center_y)
    """
    print(f"\n{'='*70}")
    print(f"BENCHMARK: stabilize() — {n_frames} frames, {len(roi_configs)} ROIs")
    print(f"motion_amplitude={motion_amplitude} px/frame (simulated drift)")
    print(f"{'='*70}")

    frame_w, frame_h = 640, 480

    # Per-stabilizer per-call timers
    stab_timers = {name: {"total": 0.0, "count": 0, "latencies": []}
                   for name, *_ in roi_configs}

    stabilizers = {}
    for name, rw, rh, cx, cy in roi_configs:
        stab = OpticalFlowROIStabilizer()
        stab._roi_name = name
        stabilizers[name] = stab

    reset_instrumentation()

    base_frame = synthetic_frame(frame_w, frame_h)

    for frame_idx in range(n_frames):
        t = frame_idx / 30.0
        dx = int(motion_amplitude * np.sin(2 * np.pi * 0.3 * t))
        dy = int(motion_amplitude * 0.5 * np.sin(2 * np.pi * 0.5 * t))

        for name, rw, rh, cx, cy in roi_configs:
            stab = stabilizers[name]
            bbox = make_bbox(cx + dx, cy + dy, rw, rh, frame_w, frame_h)

            t0 = _time_module.perf_counter()
            result = stab.stabilize(base_frame, bbox)
            t_elapsed = _time_module.perf_counter() - t0
            stab_timers[name]["total"] += t_elapsed
            stab_timers[name]["count"] += 1
            stab_timers[name]["latencies"].append(t_elapsed * 1000)

        offset_x = 2 * np.pi * frame_idx / 90
        base_frame = synthetic_frame(frame_w, frame_h, offset_x=offset_x)

    # Print per-ROI results
    total_stab_time = 0.0
    total_calls = 0
    reset_interval = 90

    print(f"\n{'ROI':<20} {'calls':>8} {'stab_ms':>10} {'stab_avg':>10} "
          f"{'stab_med':>10} {'stab_p95':>10} "
          f"{'gft_ms':>10} {'gft_avg':>10} {'lk_ms':>10} {'lk_avg':>10} "
          f"{'gft_calls':>10} {'feat_min':>9} {'feat_max':>9}")
    print("-" * 140)

    issues = []
    for name, *_ in roi_configs:
        s = stab_timers[name]
        stats = get_stabilization_stats().get(name, {})
        calls = s["count"] or 1
        gft_calls = stats.get("gft_calls", 0)
        gft_total = stats.get("gft_time_sum", 0.0)
        lk_total = stats.get("lk_time_sum", 0.0)
        gft_avg = (gft_total / gft_calls * 1000) if gft_calls else 0
        lk_avg = (lk_total / calls * 1000) if calls else 0
        stab_avg = (s["total"] / calls) * 1000
        stab_med, stab_p95, _ = _report_latency("stab", s["latencies"])

        feat_min = stats.get("features_found_min", 0)
        feat_max = stats.get("features_found_max", 0)
        early_rtn = stats.get("early_reset_return", 0)

        total_stab_time += s["total"]
        total_calls += calls

        # Validations
        if gft_calls == 0:
            issues.append(f"  [{name}] ZERO gft_calls — stabilizer was never reset")
        expected_gft = n_frames // reset_interval + 1
        if gft_calls < expected_gft - 2:
            issues.append(f"  [{name}] fewer gft_calls ({gft_calls}) than expected ({expected_gft})")
        if early_rtn > 0:
            issues.append(f"  [{name}] {early_rtn} early_reset_return calls")
        if feat_min == 0 and feat_max > 0:
            issues.append(f"  [{name}] min features=0 but max={feat_max}")

        print(f"{name:<20} {calls:>8} {s['total']*1000:>10.3f} {stab_avg:>10.3f} "
              f"{stab_med:>10.3f} {stab_p95:>10.3f} "
              f"{gft_total*1000:>10.3f} {gft_avg:>10.3f} {lk_total*1000:>10.3f} {lk_avg:>10.3f} "
              f"{gft_calls:>10} {feat_min:>9} {feat_max:>9}")

    per_frame_overhead_ms = (total_stab_time / max(total_calls, 1)) * 1000
    per_frame_overhead_s  = total_stab_time / max(total_calls, 1)
    fps_stabilizer = 1.0 / per_frame_overhead_s if per_frame_overhead_s > 0 else float("inf")

    print()
    print(f"Total stabilize() time:       {total_stab_time*1000:.3f} ms")
    print(f"Total calls:                  {total_calls}")
    print(f"Avg stabilize() per call:    {per_frame_overhead_ms:.3f} ms")
    print(f"Stabilizer capacity estimate: {fps_stabilizer:.0f} fps  "
          f"(stabilize() calls only, not end-to-end pipeline)")
    print(f"Reset interval:               {reset_interval} frames")
    print(f"Expected gft_calls per ROI:    {n_frames // reset_interval + 1}  "
          f"(initial + resets)")

    if issues:
        print(f"\nISSUES FOUND:")
        for issue in issues:
            print(issue)
    else:
        print(f"\nNo issues detected.")

    return get_stabilization_stats()


# ---------------------------------------------------------------------------
# Integration benchmark — FaceLandmarker (tasks API, 0.10.35)
# ---------------------------------------------------------------------------

def _make_mp_landmarks(face_landmarker_result):
    """
    Extract face landmarks from a FaceLandmarkerResult.

    Returns a NormalizedLandmarkList-like object with a .landmark attribute,
    matching the interface MultiROIFusionEngineV2.update() expects.
    Returns None if no face was detected.
    """
    if not face_landmarker_result.face_landmarks:
        return None
    return face_landmarker_result.face_landmarks[0]


def benchmark_v2_integration(video_path=None, n_frames=300):
    """
    Benchmark MultiROIFusionEngineV2.update() with genuine FaceLandmarker.

    Uses mediapipe.tasks.python.vision.FaceLandmarker (compatible with 0.10.35).

    Landmark source priority:
      1. FaceLandmarker on real video    → "REAL FACE LANDMARKS"
      2. Synthetic landmarks (fallback)  → "SYNTHETIC LANDMARKS"

    Synthetic-landmarks mode activates automatically when FaceLandmarker detects
    no face (e.g. on ROI-cropped datasets like Dataset_rPPG-10 where only
    forehead/cheek patches are stored, not full-face recordings).
    The fallback is always reported explicitly in the output header.
    """
    print(f"\n{'='*70}")
    print(f"INTEGRATION BENCHMARK: MultiROIFusionEngineV2.update() — {n_frames} frames")
    print(f"{'='*70}")

    # --- Validate model before doing anything else ---
    model_path = _check_model()
    print(f"Model: {model_path}")

    # --- Import MediaPipe tasks API ---
    # MediaPipe 0.10.35 layout:
    #   FaceLandmarker, FaceLandmarkerOptions, RunningMode  ← from .vision
    #   Image, ImageFormat                               ← from .vision.core.image
    #   BaseOptions                                      ← from .python
    try:
        from mediapipe.tasks.python.vision import (
            FaceLandmarker, FaceLandmarkerOptions, RunningMode,
        )
        from mediapipe.tasks.python.vision.core.image import ImageFormat, Image
        from mediapipe.tasks.python import BaseOptions
    except ImportError as e:
        print(f"\nERROR: mediapipe.tasks.python.vision imports failed.\n"
              f"  Import error: {e}\n"
              f"  MediaPipe version: 0.10.35  —  correct imports:\n"
              f"    from mediapipe.tasks.python.vision import FaceLandmarker, RunningMode\n"
              f"    from mediapipe.tasks.python.vision.core.image import Image, ImageFormat\n"
              f"    from mediapipe.tasks.python import BaseOptions\n")
        return {}

    # --- Initialise FaceLandmarker in VIDEO mode ---
    try:
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.VIDEO,
            num_faces=1,
        )
        face_landmarker = FaceLandmarker.create_from_options(options)
    except Exception as e:
        print(f"\nERROR: FaceLandmarker failed to initialise.\n"
              f"  Exception: {e}\n"
              f"  Model path: {model_path}\n"
              f"  Verify the .task file is valid and not corrupted.")
        return {}

    try:
        from rppg_core import MultiROIFusionEngineV2
    except ImportError as e:
        print(f"\nERROR: MultiROIFusionEngineV2 import failed.\n  {e}")
        face_landmarker.close()
        return {}

    reset_instrumentation()
    engine = MultiROIFusionEngineV2(enable_logging=False)

    # --- Open video or use synthetic ---
    cap = None
    if video_path and os.path.exists(video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"\nERROR: Could not open video: {video_path}")
            face_landmarker.close()
            return {}
        print(f"Video: {video_path}")
        total_frames_in_file = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Video frame count: {total_frames_in_file}")
    else:
        print("No video — will use synthetic frames + synthetic landmarks")

    W, H = 640, 480
    frame_count = 0
    timestamp_ms = 0
    frame_interval_ms = 33  # ~30 fps

    # Per-frame latencies (ms)
    frame_latencies_ms = []
    mp_latencies_ms    = []   # FaceLandmarker only; 0 in synthetic-landmarks mode

    # Landmark mode: None = detect (FaceLandmarker), "synthetic" = fallback
    landmark_mode = None
    landmark_label = ""

    wall_start = _time_module.perf_counter()
    prev_wall  = wall_start

    try:
        while frame_count < n_frames:
            # Capture or generate frame
            if cap is not None:
                ret, frame = cap.read()
                if not ret:
                    print(f"  Video ended at frame {frame_count} / {n_frames}")
                    break
                frame = cv2.resize(frame, (W, H))
            else:
                offset_x = 2 * np.pi * frame_count / 90
                frame = synthetic_frame(W, H, offset_x=offset_x)

            frame = cv2.GaussianBlur(frame, (3, 3), 0)

            # --- FaceLandmarker path ---
            if landmark_mode is None:
                mp_t0 = _time_module.perf_counter()
                rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
                mp_result = face_landmarker.detect_for_video(mp_image, timestamp_ms)
                mp_latencies_ms.append((_time_module.perf_counter() - mp_t0) * 1000)

                landmarks = _make_mp_landmarks(mp_result)

                if landmarks is None:
                    # First FaceLandmarker call returned no face
                    landmark_mode = "synthetic"
                    if video_path:
                        landmark_label = (
                            f"SYNTHETIC LANDMARKS (FaceLandmarker found no face on "
                            f"frame {frame_count} of '{os.path.basename(video_path)}')"
                        )
                        print(f"\n  NOTE: FaceLandmarker: no face detected on frame {frame_count} "
                              f"of the provided video.\n"
                              f"  Dataset_rPPG-10 videos are ROI crops (forehead/cheek patches)\n"
                              f"  and do not contain full faces — FaceLandmarker requires a full\n"
                              f"  face in frame. Switching to synthetic face landmarks.\n"
                              f"  Pipeline path (stabilizer, signal buffer, fusion) will be\n"
                              f"  exercised fully. FPS and latency numbers below reflect the\n"
                              f"  real pipeline cost without FaceLandmarker overhead.\n")
                    else:
                        landmark_label = "SYNTHETIC LANDMARKS (no video provided)"
                        print(f"\n  NOTE: No video provided. Using synthetic face landmarks.\n"
                              f"  Pipeline path is exercised; FPS excludes FaceLandmarker.\n")
                    # Continue into synthetic path for this frame
                # else: landmarks found → use them below

            # --- Landmarks: real or synthetic ---
            if landmark_mode == "synthetic" or landmark_mode is None:
                landmarks = _PseudoLandmarkList(frame_count, W, H)
                mp_latencies_ms[-1] = 0.0   # FaceLandmarker was not called this frame

            # --- Engine update ---
            t0 = _time_module.perf_counter()
            fr = engine.update(frame, landmarks, H, W)
            frame_latencies_ms.append((_time_module.perf_counter() - t0) * 1000)

            # Wall-clock FPS (end-to-end)
            wall_now = _time_module.perf_counter()
            wall_dt  = wall_now - prev_wall
            prev_wall = wall_now

            timestamp_ms += frame_interval_ms
            frame_count += 1

    finally:
        if cap is not None:
            cap.release()
        face_landmarker.close()

    wall_elapsed = _time_module.perf_counter() - wall_start

    # --- Validation ---
    issues = []

    if frame_count == 0:
        issues.append("  Zero frames processed — benchmark is invalid")

    stats = get_stabilization_stats()
    if not stats:
        issues.append("  Stabilization stats are empty — stabilizer was never called")

    total_stab_calls = sum(s.get("calls", 0) for s in stats.values())
    if total_stab_calls == 0:
        issues.append("  Total stabilizer calls = 0 — stabilizer path was not exercised")

    any_gft = any(s.get("gft_calls", 0) > 0 for s in stats.values())
    if not any_gft:
        issues.append("  No gft_calls recorded — features were never detected / tracked")

    for name, s in stats.items():
        gft = s.get("gft_calls", 0)
        if gft < 1:
            issues.append(f"  [{name}] gft_calls={gft}, expected >=1")

    if issues:
        print(f"\n{'='*70}")
        print("INTEGRATION BENCHMARK FAILED — ERRORS:")
        for iss in issues:
            print(iss)
        print("(FPS/latency numbers below are NOT meaningful.)\n")
    else:
        print(f"\n{'='*70}")
        print("Validation PASSED — all checks succeeded.")

    # --- Performance report ---
    med_f, p95_f, avg_f = _report_latency("frame", frame_latencies_ms)
    mp_avg = float(np.mean(mp_latencies_ms)) if mp_latencies_ms else 0.0
    mp_med = float(np.median(mp_latencies_ms)) if mp_latencies_ms else 0.0
    e2e_fps = frame_count / wall_elapsed if wall_elapsed > 0 else 0.0

    if not landmark_label:
        landmark_label = "REAL FACE LANDMARKS"

    print(f"\n{'='*70}")
    print(f"PERFORMANCE REPORT  [{landmark_label}]")
    print(f"{'='*70}")

    print(f"\n--- Frame processing (pipeline end-to-end) ---")
    print(f"  Frames processed:       {frame_count}")
    print(f"  Wall elapsed:           {wall_elapsed:.2f} s")
    print(f"  FPS end-to-end:         {e2e_fps:.1f} fps  "
          f"(wall-clock, {frame_count} frames / {wall_elapsed:.2f}s)")

    print(f"\n--- Per-frame pipeline latency ---")
    print(f"  Median:                 {med_f:.2f} ms")
    print(f"  P95:                   {p95_f:.2f} ms")
    print(f"  Average:               {avg_f:.2f} ms")

    if landmark_mode == "synthetic":
        print(f"\n--- FaceLandmarker detect_for_video() ---")
        print(f"  [SKIPPED] — synthetic landmarks in use")
        print(f"  To measure FaceLandmarker latency, provide a video containing")
        print(f"  a full, visible face. Use capture_real_face.py to record one.")
    else:
        print(f"\n--- FaceLandmarker detect_for_video() ---")
        print(f"  Median:                 {mp_med:.2f} ms")
        print(f"  Average:               {mp_avg:.2f} ms")

    print(f"\n--- Stabilizer per-ROI breakdown ---")
    print(f"\n{'ROI':<20} {'calls':>8} {'stab_ms':>10} "
          f"{'gft_calls':>10} {'feat_min':>9} {'feat_max':>9} {'none_rtn':>9}")
    print("-" * 80)
    for name, s in stats.items():
        calls = s.get("calls") or 1
        gft   = s.get("gft_calls", 0)
        stab_ms = (s.get("total_time_sum", 0.0) / calls) * 1000
        feat_min = s.get("features_found_min", 0)
        feat_max = s.get("features_found_max", 0)
        none_rtn = s.get("none_returns", 0)
        print(f"{name:<20} {calls:>8} {stab_ms:>10.3f} "
              f"{gft:>10} {feat_min:>9} {feat_max:>9} {none_rtn:>9}")

    if total_stab_calls > 0:
        total_stab_time = sum(s.get("total_time_sum", 0.0) for s in stats.values())
        per_frame_s = total_stab_time / total_stab_calls
        stab_capacity = 1.0 / per_frame_s if per_frame_s > 0 else float("inf")
        print(f"\n  Stabilizer capacity:    {stab_capacity:.0f} fps  "
              f"(stabilize() calls only — NOT end-to-end FPS)")
        print(f"  End-to-end FPS ({e2e_fps:.1f}) reflects the dominant cost:")
        if landmark_mode == "synthetic":
            print(f"  synthetic-landmarks mode — FaceLandmarker overhead is excluded.")
        else:
            print(f"  FaceLandmarker is the dominant cost ({mp_avg:.1f} ms/frame).")

    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark stabilize() overhead and V2 integration")
    parser.add_argument("--frames", type=int, default=300,
                        help="Number of frames")
    parser.add_argument("--video", type=str, default=None,
                        help="Video path for integration benchmark")
    parser.add_argument("--integration", action="store_true",
                        help="Run V2 integration benchmark")
    args = parser.parse_args()

    # ROI configurations: (name, roi_w, roi_h, center_x, center_y)
    roi_configs = [
        ("forehead",    80,  40,  320, 120),
        ("cheek_left",  100, 60,  230, 220),
        ("cheek_right", 100, 60,  410, 220),
    ]

    # 1. Unit benchmark: pure stabilize() overhead on synthetic frames
    benchmark_stabilize(roi_configs, n_frames=args.frames)

    # 2. V2 integration benchmark with FaceLandmarker (or synthetic fallback)
    if args.integration:
        benchmark_v2_integration(video_path=args.video, n_frames=args.frames)
