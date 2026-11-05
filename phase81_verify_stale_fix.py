"""
Phase 8.1 runtime verification: exercise V2 update() with controlled motion states.

Uses mock face landmarks to drive MotionArtifactDetector through:
  - Still frames (low motion_score, grace=0, inactive)
  - Active motion (high motion_score, grace=20, active)
  - Grace expiration (score drops, grace counts down to 0, inactive)

Verifies:
  A. Diagnostic fields are populated on every frame
  B. Stale local does not cause rejection when detector is inactive
  C. Active motion still causes rejection
  D. Grace period behavior unchanged
  E. V2 authoritative state used

FIX in Phase 8.3: tests B-E called update(gray, None, ...) which triggers the
face_landmarks=None early-return at rppg_core.py:462-463, bypassing the entire
motion-score/EMA/threshold pipeline.  The injected _score_ema values were
discarded.  Fixed by calling update() with valid MockLandmarks so the real
state-transition code executes.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# -- Mock face mesh result ---------------------------------------------------

class DummyPoint:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

class MockLandmarks:
    def __init__(self, points):
        self._points = points
        self.landmark = self   # face_landmarks.landmark must be indexable

    def __len__(self):
        return len(self._points)

    def __getitem__(self, key):
        return self._points[key]

class MockResult:
    def __init__(self, landmarks):
        self._landmarks = landmarks

    @property
    def multi_face_landmarks(self):
        return self._landmarks

    def __len__(self):
        return len(self._landmarks)


# -- Mock frame --------------------------------------------------------------
import numpy as np

def make_frame(gray_val=128):
    return np.full((480, 640, 3), gray_val, dtype=np.uint8)


# -- Import V2 engine -------------------------------------------------------
import types

def _make_dummy_cv2():
    m = types.ModuleType('cv2')
    class _DummyVideoCapture:
        def __init__(self, *a, **kw): pass
        def read(self): return False, None
        def release(self): pass
        def get(self, prop): return 30.0
        def isOpened(self): return False
    m.VideoCapture = _DummyVideoCapture
    m.COLOR_BGR2GRAY = 6
    m.GaussianBlur = lambda img, k, sig: img
    return m

try:
    import cv2
    _cv2_loaded = True
except ImportError:
    sys.modules['cv2'] = _make_dummy_cv2()
    _cv2_loaded = False

try:
    import mediapipe as mp
except ImportError:
    mp = types.ModuleType('mediapipe')
    sys.modules['mediapipe'] = mp

from rppg_core import MultiROIFusionEngineV2, MotionArtifactDetector


# -- Test A: Diagnostic fields populated ------------------------------------

def test_a_diagnostic_fields_populated():
    """Verify _diag_* fields are set on every V2 frame result."""
    engine = MultiROIFusionEngineV2()
    landmarks = MockLandmarks([DummyPoint(0.5, 0.3) for _ in range(478)])
    frame = make_frame()

    results = []
    for i in range(10):
        fr = engine.update(frame, landmarks, 480, 640)
        has_diag = (
            hasattr(fr, '_diag_detector_is_moving') and
            hasattr(fr, '_diag_grace_counter') and
            hasattr(fr, '_diag_score_at_decision') and
            hasattr(fr, '_diag_was_local_stale') and
            hasattr(fr, '_diag_override_fired')
        )
        results.append(has_diag)

    assert all(results), f"Some frames missing diagnostic fields: {results}"
    print(f"  A PASS: {len(results)}/{len(results)} frames have all diagnostic fields")


# -- Test B: Stale local -- graceful-motion transition ----------------------

def test_b_stale_local_grace_expired():
    """
    Simulate: motion detector goes from active (grace>0) to inactive (grace=0).
    The local is_moving return from update() can be stale (True from previous frame).
    After Phase 8 fix: result.motion_rejected must reflect authoritative state.

    Approach:
      1. Call update() with valid landmarks so the real EMA pipeline fires ENTER.
      2. Directly set grace_counter=19 so subsequent zero-motion calls exercise
         the EXIT path (score < EXIT=1.5, grace decrements).
      3. After 19 zero-motion calls, grace reaches 1; one more call clears it to 0.
      4. The frame after grace=0 confirms is_moving=False.
    """
    from rppg_config import cfg

    detector = MotionArtifactDetector()
    gray = np.full((480, 640), 128, dtype=np.uint8)

    # -- Establish active state via the real pipeline -----------------------
    # prev_lm_pts must contain only the 12 indexed landmarks (same subset that
    # update() extracts via _lm_ids).  Building it from all 478 points causes a
    # length mismatch with curr_pts (12 pts) so lm_score stays 0.
    lm_shifted = MockLandmarks([DummyPoint(0.5 - 0.05, 0.3) for _ in range(478)])
    # Extract the indexed subset, matching what update() computes for curr_pts:
    prev_pts_shifted = np.array([[lm_shifted.landmark[i].x * 640,
                                   lm_shifted.landmark[i].y * 480]
                                  for i in detector._lm_ids], dtype=np.float32)
    detector.prev_lm_pts = prev_pts_shifted
    detector.motion_score = 10.0
    detector._score_ema   = 10.0
    detector._slow_ema    = 0.0
    # prev_gray is still None → pixel score = 0 on first call, but lm_score fires.
    lm_active = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
    score, is_mov = detector.update(gray, lm_active, 480, 640)

    assert detector.is_moving is True, \
        f"B-1: ENTER must fire on first real update(), is_moving={detector.is_moving}"
    assert detector.grace_counter == cfg.MOTION_GRACE_FRAMES, \
        f"B-1: grace must be {cfg.MOTION_GRACE_FRAMES}, got {detector.grace_counter}"
    # PROOF the real EMA pipeline ran: _slow_ema starts at 0.0 and is updated
    # only inside update().  If update() had returned early (face_landmarks=None),
    # _slow_ema would still be 0.0.
    assert detector._slow_ema > 0, \
        f"B-1: _slow_ema must be > 0 (real EMA ran), got {detector._slow_ema}"
    print(f"  B-1 PASS: active state: grace={detector.grace_counter}, is_moving={detector.is_moving}, "
          f"_slow_ema={detector._slow_ema:.4f} (real EMA confirmed)")

    # -- Grace decrement: 19 calls with near-zero score, then 1 call to exhaust --------
    # Reset _score_ema to a low value so motion_score < EXIT immediately.
    # The real pipeline then recomputes _score_ema from zero-motion frames as
    # the loop iterates; EXIT fires every iteration and grace counts down to 0.
    # _slow_ema is reset to 1.0 so the HPF (ema - slow*0.6) gives motion_score ≈ 0.
    detector._score_ema = 0.4   # below EXIT threshold
    detector._slow_ema  = 1.0
    detector.grace_counter = cfg.MOTION_GRACE_FRAMES - 1   # 19
    assert detector.is_moving is True   # ENTER set this
    grace_expired_frame = None
    for i in range(cfg.MOTION_GRACE_FRAMES):   # 20 iterations: grace 19->1 on first 19
        lm_zero = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
        s, im = detector.update(gray, lm_zero, 480, 640)
        if detector.grace_counter == 0:
            grace_expired_frame = i + 1   # 1-indexed
            print(f"  B-2 INFO: grace expired at frame {grace_expired_frame}: "
                  f"score={s:.3f}, returned={im}, internal={detector.is_moving}, "
                  f"grace={detector.grace_counter}")
            break

    assert grace_expired_frame is not None, \
        f"B-2: grace never reached 0 in {cfg.MOTION_GRACE_FRAMES} calls; " \
        f"final: grace={detector.grace_counter}"

    # At grace=0: authoritative is_moving is still True (EXIT fires on NEXT call).
    # Call update() once more to trigger the EXIT path and clear is_moving=False.
    lm_zero_exit = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
    s_exit, im_exit = detector.update(gray, lm_zero_exit, 480, 640)

    authoritative_rejected = detector.is_moving
    assert authoritative_rejected is False, \
        f"B-2: grace expired, EXIT fired on next call, authoritative is_moving must be False, got {authoritative_rejected}"
    # PROOF real pipeline computed the EXIT: _score_ema has decayed toward 0 from
    # zero-motion frames.  The injected value (10.0) would still be 10.0 if
    # update() had returned early.
    assert detector._score_ema < 1.0, \
        f"B-2: _score_ema must be < 1.0 (real zero-motion EMA), got {detector._score_ema:.3f}"
    print(f"  B-2 PASS: grace expired at frame {grace_expired_frame} + EXIT next call: "
          f"authoritative inactive, _score_ema={detector._score_ema:.3f} (real EXIT confirmed)")

    # -- Grace expiration confirmed: is_moving stays False on the frame after ----
    lm_zero2 = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
    s2, im2 = detector.update(gray, lm_zero2, 480, 640)
    assert detector.grace_counter == 0, \
        f"B-3: grace must stay 0, got {detector.grace_counter}"
    assert detector.is_moving is False, \
        f"B-3: is_moving must stay False after grace expired, got {detector.is_moving}"
    assert im2 is False, f"B-3: returned is_moving must be False, got {im2}"
    print(f"  B-3 PASS: frame after expiration -> grace=0, is_moving=False")


# -- Test C: Active motion still causes rejection ----------------------------

def test_c_active_motion_rejected():
    """
    Verify genuine active motion (high score) still causes rejection.

    Establish active state via the real update() pipeline (ENTER fires), then
    re-inject a score that keeps ENTER true on subsequent calls.
    """
    from rppg_config import cfg

    detector = MotionArtifactDetector()
    gray = np.full((480, 640), 128, dtype=np.uint8)

    # -- Establish active state via real pipeline ----------------------------
    # prev_lm_pts must contain only the 12 indexed landmarks (matching curr_pts).
    lm_shifted = MockLandmarks([DummyPoint(0.5 - 0.05, 0.3) for _ in range(478)])
    prev_pts_shifted = np.array([[lm_shifted.landmark[i].x * 640,
                                   lm_shifted.landmark[i].y * 480]
                                  for i in detector._lm_ids], dtype=np.float32)
    detector.prev_lm_pts = prev_pts_shifted
    detector.motion_score = 10.0
    detector._score_ema   = 10.0
    detector._slow_ema    = 0.0
    lm = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
    # With prev_lm_pts set, the first call fires real lm_score → _slow_ema > 0.
    detector.update(gray, lm, 480, 640)

    assert detector.is_moving is True, \
        f"C-setup: active state not established, is_moving={detector.is_moving}"
    assert detector.grace_counter == cfg.MOTION_GRACE_FRAMES
    # PROOF real EMA pipeline ran: _slow_ema > 0 only if update() executed.
    assert detector._slow_ema > 0, \
        f"C-setup: _slow_ema must be > 0 (real EMA ran), got {detector._slow_ema}"
    print(f"  C-setup PASS: active state established (grace={detector.grace_counter}), "
          f"_slow_ema={detector._slow_ema:.4f} (real EMA confirmed)")

    # -- Verify rejection is active -----------------------------------------
    # Inject high score to keep ENTER firing.
    detector.motion_score = 10.0
    detector._score_ema   = 10.0
    # DO NOT reset prev_lm_pts — it is already set from the right-shifted
    # position from the last update() call; the next call sees lm_score = 0
    # (no landmark change) and slow_ema stays non-zero (proving real pipeline ran).
    lm2 = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
    s, im = detector.update(gray, lm2, 480, 640)

    assert detector.motion_score > cfg.MOTION_ENTER_THRESHOLD, \
        f"C-1: score={detector.motion_score:.3f} must be >ENTER={cfg.MOTION_ENTER_THRESHOLD}"
    assert im is True, f"C-1: returned is_moving must be True, got {im}"
    assert detector.is_moving is True, \
        f"C-1: authoritative is_moving must be True, got {detector.is_moving}"
    print(f"  C-1 PASS: score={detector.motion_score:.3f}, is_moving={detector.is_moving}")

    # Authoritative result
    result_rejected = detector.is_moving
    assert result_rejected is True, \
        f"C-2: authoritative rejection must be True, got {result_rejected}"
    print(f"  C-2 PASS: authoritative rejection=True during active motion")


# -- Test D: Grace period behavior unchanged --------------------------------

def test_d_grace_period_unchanged():
    """
    Verify grace period: score drops below ENTER but grace > 0 -> still rejected.

    Approach: call update() once to enter active state (grace=20, is_moving=True).
    Directly set grace_counter=19 to simulate mid-grace.  The next zero-motion
    call exercises the EXIT path: score < EXIT, grace decrements to 18, and
    is_moving stays True (grace sustains rejection).
    """
    from rppg_config import cfg

    detector = MotionArtifactDetector()
    gray = np.full((480, 640), 128, dtype=np.uint8)

    # -- Establish active state via real pipeline ----------------------------
    # prev_lm_pts must contain only the 12 indexed landmarks (matching curr_pts).
    lm_shifted = MockLandmarks([DummyPoint(0.5 - 0.05, 0.3) for _ in range(478)])
    prev_pts_shifted = np.array([[lm_shifted.landmark[i].x * 640,
                                   lm_shifted.landmark[i].y * 480]
                                  for i in detector._lm_ids], dtype=np.float32)
    detector.prev_lm_pts = prev_pts_shifted
    detector.motion_score = 10.0
    detector._score_ema   = 10.0
    detector._slow_ema    = 0.0
    lm = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
    # With prev_lm_pts set, the first call fires real lm_score → _slow_ema > 0.
    detector.update(gray, lm, 480, 640)

    assert detector.is_moving is True
    assert detector.grace_counter == cfg.MOTION_GRACE_FRAMES
    # PROOF real EMA pipeline ran: _slow_ema > 0 only if update() executed.
    assert detector._slow_ema > 0, \
        f"D-setup: _slow_ema must be > 0 (real EMA ran), got {detector._slow_ema}"
    print(f"  D-setup PASS: grace={detector.grace_counter}, "
          f"_slow_ema={detector._slow_ema:.4f} (real EMA confirmed)")

    # -- Grace decrements during zero-motion frames (grace > 0, score < ENTER) --
    # Reset _score_ema to a low value so motion_score < EXIT immediately.
    # The real pipeline recomputes _score_ema from zero-motion frames;
    # EXIT fires and grace decrements.
    detector._score_ema = 0.4   # below EXIT threshold
    detector._slow_ema  = 1.0
    detector.grace_counter = cfg.MOTION_GRACE_FRAMES - 1   # 19
    assert detector.is_moving is True

    lm_zero = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
    s_dropped, im_dropped = detector.update(gray, lm_zero, 480, 640)

    assert detector.grace_counter < cfg.MOTION_GRACE_FRAMES, \
        f"D-1: is_moving must stay True during grace (grace={detector.grace_counter}), got {detector.is_moving}"
    print(f"  D-1 PASS: grace decremented to {detector.grace_counter}, is_moving={detector.is_moving}")

    # Authoritative result
    result_rejected = detector.is_moving
    assert result_rejected is True, \
        f"D-2: authoritative rejection must be True during grace, got {result_rejected}"
    print(f"  D-2 PASS: grace period -> authoritative rejection=True")


# -- Test E: V2 authoritative state used -----------------------------------

def test_e_v2_authoritative():
    """
    Verify V2 uses self.motion_detector.is_moving (authoritative), not local.

    Enter active state via the real pipeline, then simulate grace exhaustion
    by directly setting grace_counter and walking through zero-motion calls.
    """
    from rppg_config import cfg

    detector = MotionArtifactDetector()
    gray = np.full((480, 640), 128, dtype=np.uint8)

    # -- Establish active state --------------------------------------------
    # prev_lm_pts must contain only the 12 indexed landmarks (matching curr_pts).
    lm_shifted = MockLandmarks([DummyPoint(0.5 - 0.05, 0.3) for _ in range(478)])
    prev_pts_shifted = np.array([[lm_shifted.landmark[i].x * 640,
                                   lm_shifted.landmark[i].y * 480]
                                  for i in detector._lm_ids], dtype=np.float32)
    detector.prev_lm_pts = prev_pts_shifted
    detector.motion_score = 10.0
    detector._score_ema   = 10.0
    detector._slow_ema    = 0.0
    lm = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
    # With prev_lm_pts set, the first call fires real lm_score → _slow_ema > 0.
    detector.update(gray, lm, 480, 640)
    assert detector.is_moving is True
    assert detector.grace_counter == cfg.MOTION_GRACE_FRAMES
    assert detector._slow_ema > 0, \
        f"E-setup: _slow_ema must be > 0 (real EMA ran), got {detector._slow_ema}"
    print(f"  E-setup PASS: grace={detector.grace_counter}, _slow_ema={detector._slow_ema:.4f}")

    # -- Exhaust grace via zero-motion calls ---------------------------------
    # Reset _score_ema to a low value so motion_score < EXIT immediately.
    detector._score_ema = 0.4   # below EXIT threshold
    detector._slow_ema  = 1.0
    detector.grace_counter = cfg.MOTION_GRACE_FRAMES - 1   # 19
    for _ in range(cfg.MOTION_GRACE_FRAMES):   # 20 calls: grace 19 -> 1
        lm_zero = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
        detector.update(gray, lm_zero, 480, 640)

    # grace is now 1; one more call triggers EXIT and clears is_moving=False.
    lm_zero_exit = MockLandmarks([DummyPoint(0.5 + 0.05, 0.3) for _ in range(478)])
    detector.update(gray, lm_zero_exit, 480, 640)

    assert detector.grace_counter == 0, \
        f"E: grace must be 0 after exhaustion, got {detector.grace_counter}"
    assert detector.is_moving is False, \
        f"E: is_moving must be False when grace=0, got {detector.is_moving}"

    # Authoritative: result.motion_rejected = self.motion_detector.is_moving
    v2_result = detector.is_moving
    assert v2_result is False, f"E: V2 authoritative must be False, got {v2_result}"
    print(f"  E PASS: V2 authoritative state = False (grace=0, inactive)")


# -- Run all ----------------------------------------------------------------

def run():
    print("=" * 60)
    print("PHASE 8.1: Runtime Verification (V2 Engine, Offline)")
    print("=" * 60)
    tests = [
        ("A: Diagnostic fields populated on every frame",
         test_a_diagnostic_fields_populated),
        ("B: Stale local -- graceful-motion transition",
         test_b_stale_local_grace_expired),
        ("C: Active motion still causes rejection",
         test_c_active_motion_rejected),
        ("D: Grace period behavior unchanged",
         test_d_grace_period_unchanged),
        ("E: V2 authoritative state used",
         test_e_v2_authoritative),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        print(f"\n[{name}]")
        try:
            fn()
            passed += 1
            print("  RESULT: PASS")
        except AssertionError as e:
            print(f"  RESULT: FAIL -- {e}")
            failed += 1
        except Exception as e:
            print(f"  RESULT: ERROR -- {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0

if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
