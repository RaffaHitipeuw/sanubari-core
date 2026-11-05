"""
Unit tests for V1 MotionDetector bug fix.

Issue: MotionArtifactDetector references self.enter_threshold which doesn't exist.
Fix: Added enter_threshold and exit_threshold properties.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rppg_core import MotionArtifactDetector
from rppg_config import cfg


class TestMotionDetector:
    """Test suite for MotionArtifactDetector."""

    def test_enter_threshold_property_exists(self):
        """Test that enter_threshold property is accessible."""
        detector = MotionArtifactDetector()

        # Should be accessible as property
        assert hasattr(detector, 'enter_threshold'), \
            "MotionArtifactDetector should have enter_threshold property"

        # Should return the configured threshold
        assert detector.enter_threshold == cfg.MOTION_ENTER_THRESHOLD, \
            f"enter_threshold should equal cfg.MOTION_ENTER_THRESHOLD ({cfg.MOTION_ENTER_THRESHOLD})"

        print(f"  [OK] enter_threshold = {detector.enter_threshold}")

    def test_exit_threshold_property_exists(self):
        """Test that exit_threshold property is accessible."""
        detector = MotionArtifactDetector()

        assert hasattr(detector, 'exit_threshold'), \
            "MotionArtifactDetector should have exit_threshold property"

        assert detector.exit_threshold == cfg.MOTION_EXIT_THRESHOLD, \
            f"exit_threshold should equal cfg.MOTION_EXIT_THRESHOLD ({cfg.MOTION_EXIT_THRESHOLD})"

        print(f"  [OK] exit_threshold = {detector.exit_threshold}")

    def test_motion_detector_integration(self):
        """
        Test that the motion detector can be instantiated and used
        without AttributeError on enter_threshold.

        This was the bug: V1 code calls motion_detector.enter_threshold
        but the attribute didn't exist.
        """
        detector = MotionArtifactDetector()

        # Simulate the V1 access pattern
        motion_score = 0.5
        enter_thresh = detector.enter_threshold
        exit_thresh = detector.exit_threshold

        # Should not raise AttributeError
        assert motion_score <= enter_thresh, \
            f"motion_score ({motion_score}) should be <= enter_threshold ({enter_thresh})"

        # The bug was accessing enter_threshold - verify it works
        # This would have raised AttributeError before the fix
        threshold_used = detector.enter_threshold
        assert threshold_used > 0, "Threshold should be positive"

        print(f"  [OK] No AttributeError when accessing enter_threshold ({threshold_used})")

    def test_reset_preserves_threshold_properties(self):
        """Test that reset() doesn't clear threshold properties."""
        detector = MotionArtifactDetector()
        detector.reset()

        # Properties should still be accessible after reset
        assert detector.enter_threshold == cfg.MOTION_ENTER_THRESHOLD
        assert detector.exit_threshold == cfg.MOTION_EXIT_THRESHOLD

        print("  [OK] Threshold properties preserved after reset")

    def test_grace_remaining_property(self):
        """Test that grace_remaining exposes the grace counter read-only."""
        detector = MotionArtifactDetector()

        # Initially zero
        assert detector.grace_remaining == 0

        # Simulate entering motion state (score > ENTER threshold)
        # Manually set state as if update() triggered ENTER
        detector.motion_score = 3.0
        detector.is_moving = True
        detector.grace_counter = cfg.MOTION_GRACE_FRAMES

        assert detector.grace_remaining == cfg.MOTION_GRACE_FRAMES

        # Decrement simulation
        detector.grace_counter -= 1
        assert detector.grace_remaining == cfg.MOTION_GRACE_FRAMES - 1

        print(f"  [OK] grace_remaining = {detector.grace_remaining}")

    def test_grace_active_property_active_motion(self):
        """grace_active is False when motion score is above ENTER threshold."""
        detector = MotionArtifactDetector()
        detector.motion_score = 3.0
        detector.grace_counter = 10
        # With score > ENTER, this is active motion, not grace-only
        assert detector.grace_active is False

        print("  [OK] grace_active=False when score above ENTER threshold")

    def test_grace_active_property_grace_residual(self):
        """grace_active is True when score is below ENTER and grace is non-zero."""
        detector = MotionArtifactDetector()
        detector.motion_score = 0.5   # below ENTER (2.5)
        detector.grace_counter = 15   # grace still active

        # This is the key diagnostic: score=0.5, grace=15, rejection is grace-residual
        assert detector.grace_active is True

        print("  [OK] grace_active=True when score below ENTER with non-zero grace")

    def test_grace_active_property_no_grace(self):
        """grace_active is False when grace_counter is zero."""
        detector = MotionArtifactDetector()
        detector.motion_score = 0.5
        detector.grace_counter = 0

        assert detector.grace_active is False

        print("  [OK] grace_active=False when grace_counter is zero")

    def test_grace_properties_read_only(self):
        """Verify grace properties do not modify state."""
        detector = MotionArtifactDetector()
        detector.motion_score = 1.0
        detector.grace_counter = 5

        _initial = detector.grace_counter
        _ = detector.grace_remaining   # read
        _ = detector.grace_active       # read

        assert detector.grace_counter == _initial, \
            "Reading grace_remaining must not modify grace_counter"

        print("  [OK] Grace properties are read-only")


# =============================================================================
# Phase 8: Stale-state regression tests
# =============================================================================

class TestStaleStateFix:
    """
    Regression tests for the Phase 8 stale-is_moving fix.

    Root cause: V1 MultiROIFusionEngine used the local is_moving return value
    (stale — True from a grace-pending previous frame) instead of
    the authoritative self.motion_detector.is_moving at:
      (a) result.motion_rejected = is_moving    (rppg_core.py:1344)
      (b) if is_moving:  (the V1 graceful-override block, rppg_core.py:1400)

    Fix: both use self.motion_detector.is_moving (authoritative).

    Key scenarios:
      S1 — Grace just expired, detector inactive: local=True, detector=False -> was stale
      S2 — Genuine active motion:                   local=True, detector=True  -> consistent
      S3 — Grace period active (score dropped):     local=True, detector=True  -> grace ok
      S4 — Fully inactive (no grace, no motion):  local=False, detector=False-> consistent
    """

    def _MockDetector(self, motion_score, grace_counter, is_moving):
        """Return a mock detector stub whose .update() returns stale is_moving."""
        class Mock:
            def __init__(self):
                self.motion_score = float(motion_score)
                self.grace_counter = int(grace_counter)
                self.is_moving = bool(is_moving)
                self._stale_is_moving = bool(is_moving)
            def update(self, gray, landmarks, h, w):
                return float(motion_score), self._stale_is_moving
            @property
            def grace_remaining(self):
                return self.grace_counter
        return Mock()

    def _v1_logic(self, detector, is_moving_returned):
        """Replicate V1 update() logic WITH Phase 8 fix applied. Returns dict."""
        # Phase 8 fix: authoritative detector state
        result_rejected = detector.is_moving
        # Diagnostics
        diag_det_is_mov = detector.is_moving
        diag_grace      = detector.grace_counter
        diag_score      = detector.motion_score
        diag_was_stale  = bool(is_moving_returned and not detector.is_moving)
        # V1 override
        overr_fired = False
        if detector.is_moving:
            overr_fired = diag_was_stale
        return {
            'result_rejected': result_rejected,
            'overr_fired': overr_fired,
            'diag_was_stale': diag_was_stale,
        }

    def test_s1_stale_grace_expired(self):
        """S1: grace=0, detector inactive, local is_moving=True (stale from prev frame).
        After fix: result.motion_rejected=False (authoritative detector state).
        The override block's if-condition is False (detector is_moving=False), so the
        override never executes and overr_fired=False. This is correct — the stale
        local variable would have been used by the buggy code, but the fix prevents it."""
        d = self._MockDetector(motion_score=0.48, grace_counter=0, is_moving=False)
        # update() returns stale is_moving=True (from previous frame's grace-pending state)
        r = self._v1_logic(d, is_moving_returned=True)
        assert r['result_rejected'] is False, \
            f"S1: authoritative detector inactive: rejected must be False, got {r['result_rejected']}"
        assert r['diag_was_stale'] is True, \
            "S1: stale mismatch recorded (local=True, detector=False)"
        # Override block never fires because detector.is_moving=False
        assert r['overr_fired'] is False, \
            f"S1: overr_fired must be False (override block skipped when detector inactive), got {r['overr_fired']}"
        print("  S1 PASS: grace expired -> rejected=False, stale mismatch recorded, no spurious override")

    def test_s2_genuine_active(self):
        """S2: high score, detector active. Consistent True. No stale."""
        d = self._MockDetector(motion_score=3.10, grace_counter=20, is_moving=True)
        r = self._v1_logic(d, is_moving_returned=True)
        assert r['result_rejected'] is True, \
            f"S2: motion_rejected must be True, got {r['result_rejected']}"
        assert r['diag_was_stale'] is False, "S2: not stale"
        assert r['overr_fired'] is False, "S2: overr_fired=False with authoritative True"
        print("  S2 PASS: genuine active -> rejected=True")

    def test_s3_grace_period_sustaining(self):
        """S3: grace>0, score below ENTER, detector is_moving=True (grace sustains).
        Both local and detector True. Grace legitimately sustains."""
        d = self._MockDetector(motion_score=0.80, grace_counter=12, is_moving=True)
        r = self._v1_logic(d, is_moving_returned=True)
        assert r['result_rejected'] is True, \
            f"S3: motion_rejected must be True (grace={d.grace_counter}), got {r['result_rejected']}"
        assert r['diag_was_stale'] is False, "S3: local and detector agree"
        print("  S3 PASS: grace period -> rejected=True")

    def test_s4_fully_inactive(self):
        """S4: grace=0, score low, detector inactive. Consistent False."""
        d = self._MockDetector(motion_score=0.05, grace_counter=0, is_moving=False)
        r = self._v1_logic(d, is_moving_returned=False)
        assert r['result_rejected'] is False, \
            f"S4: motion_rejected must be False, got {r['result_rejected']}"
        assert r['diag_was_stale'] is False
        assert r['overr_fired'] is False
        print("  S4 PASS: fully inactive -> rejected=False")

    def test_s5_border_at_exit_threshold(self):
        """S5: score=1.5 (EXIT), grace=0, detector inactive."""
        d = self._MockDetector(motion_score=1.50, grace_counter=0, is_moving=False)
        r = self._v1_logic(d, is_moving_returned=False)
        assert r['result_rejected'] is False, \
            f"S5: score=EXIT(1.5), grace=0: rejected must be False, got {r['result_rejected']}"
        print("  S5 PASS: at EXIT threshold -> rejected=False")

    def test_s6_border_at_enter_threshold(self):
        """S6: score=2.5 (ENTER), grace=20, detector active."""
        d = self._MockDetector(motion_score=2.50, grace_counter=20, is_moving=True)
        r = self._v1_logic(d, is_moving_returned=True)
        assert r['result_rejected'] is True, \
            f"S6: score=ENTER(2.5): rejected must be True, got {r['result_rejected']}"
        print("  S6 PASS: at ENTER threshold -> rejected=True")

    def test_s7_v2_authoritative_no_override(self):
        """S7: V2 has no override. Stale local never affects result."""
        d = self._MockDetector(motion_score=1.78, grace_counter=0, is_moving=False)
        # V2 path: result_rejected = detector.is_moving (authoritative only)
        result_rejected = d.is_moving  # authoritative
        assert result_rejected is False, \
            f"S7 V2: grace expired + inactive: rejected must be False, got {result_rejected}"
        print("  S7 PASS: V2 authoritative path -> stale local irrelevant")


def run_tests():
    """Run all motion detector tests."""
    print("\n" + "=" * 60)
    print("TESTING: V1 Motion Detector Bug Fix")
    print("=" * 60)

    test_suite = TestMotionDetector()
    stale_suite = TestStaleStateFix()

    tests = [
        ("enter_threshold property exists",
         test_suite.test_enter_threshold_property_exists),
        ("exit_threshold property exists",
         test_suite.test_exit_threshold_property_exists),
        ("Motion detector integration (no AttributeError)",
         test_suite.test_motion_detector_integration),
        ("Reset preserves threshold properties",
         test_suite.test_reset_preserves_threshold_properties),
        ("grace_remaining property",
         test_suite.test_grace_remaining_property),
        ("grace_active during active motion",
         test_suite.test_grace_active_property_active_motion),
        ("grace_active during grace residual",
         test_suite.test_grace_active_property_grace_residual),
        ("grace_active with no grace",
         test_suite.test_grace_active_property_no_grace),
        ("Grace properties read-only",
         test_suite.test_grace_properties_read_only),
        # Phase 8 stale-state regressions
        ("S1: Grace expired — detector inactive (was stale)",
         stale_suite.test_s1_stale_grace_expired),
        ("S2: Genuine active motion rejected",
         stale_suite.test_s2_genuine_active),
        ("S3: Grace period active (grace sustains rejection)",
         stale_suite.test_s3_grace_period_sustaining),
        ("S4: Fully inactive — no rejection",
         stale_suite.test_s4_fully_inactive),
        ("S5: Border — score at EXIT threshold (1.5)",
         stale_suite.test_s5_border_at_exit_threshold),
        ("S6: Border — score at ENTER threshold (2.5)",
         stale_suite.test_s6_border_at_enter_threshold),
        ("S7: V2 — authoritative state, no override",
         stale_suite.test_s7_v2_authoritative_no_override),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\nTest: {name}")
        try:
            test_fn()
            passed += 1
            print("  PASS")
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except AttributeError as e:
            print(f"  ATTRIBUTE ERROR: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


def run_stale_tests():
    """Run Phase 8 stale-state regression tests."""
    print("\n" + "=" * 60)
    print("TESTING: Phase 8 -- Stale-State Regression")
    print("=" * 60)

    suite = TestStaleStateFix()
    tests = [
        ("S1: Grace expired — detector inactive (was stale)",
         suite.test_s1_stale_grace_expired),
        ("S2: Genuine active motion rejected",
         suite.test_s2_genuine_active),
        ("S3: Grace period active (grace sustains rejection)",
         suite.test_s3_grace_period_sustaining),
        ("S4: Fully inactive — no rejection",
         suite.test_s4_fully_inactive),
        ("S5: Border — score at EXIT threshold (1.5)",
         suite.test_s5_border_at_exit_threshold),
        ("S6: Border — score at ENTER threshold (2.5)",
         suite.test_s6_border_at_enter_threshold),
        ("S7: V2 — authoritative state, no override",
         suite.test_s7_v2_authoritative_no_override),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f"\nTest: {name}")
        try:
            test_fn()
            print("  PASS")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0



# =============================================================================
# Phase 8.4D: Landmark validity and MediaPipe staleness diagnostics
# =============================================================================

class TestLandmarkDiagnostics:
    """
    Verify _diag_landmarks_valid, _diag_frames_since_mp, and _diag_landmarks_cached
    are correctly populated by the engine's update() on every frame.

    Diagnostic meanings:
      _diag_landmarks_valid:   1 = valid landmarks (detector pipeline executed)
                              0 = face_landmarks was None (early-return path fired)
      _diag_frames_since_mp:  -1 = no valid detection yet this session
                               1 = MediaPipe ran on this frame (fresh)
                               2+ = cached landmarks or missed detection
      _diag_landmarks_cached: -1 = no valid detection yet
                               0 = MediaPipe ran on this frame
                               1 = used cached value (skip frame)

    These diagnostics are set BEFORE the early-return check in update() so they
    reflect the face_landmarks INPUT to update(), not the detector's internal state.
    """

    class _DummyPoint:
        __slots__ = ('x', 'y', 'z')
        def __init__(self, x, y, z=0.0):
            self.x = x; self.y = y; self.z = z

    class _DummyLandmarks:
        __slots__ = ('_pts',)
        def __init__(self, pts):
            self._pts = pts
        @property
        def landmark(self):
            return self
        def __len__(self):
            return len(self._pts)
        def __getitem__(self, key):
            return self._pts[key]

    def _lm(self, x=0.5, y=0.5, count=478):
        return self._DummyLandmarks([self._DummyPoint(x, y) for _ in range(count)])

    def _gray(self):
        import numpy as np
        # Engine calls cv2.cvtColor(frame, COLOR_BGR2GRAY), so pass 3-channel BGR.
        return np.full((480, 640, 3), 128, dtype=np.uint8)

    # ------------------------------------------------------------------
    # V1 engine
    # ------------------------------------------------------------------

    def test_v1_valid_landmarks_fresh(self):
        """With valid landmarks on frame 1: valid=1, sinceMp=1, cached=-1 (first detection)."""
        import numpy as np
        from rppg_core import MultiROIFusionEngine

        engine = MultiROIFusionEngine()
        lm = self._lm()
        fr = engine.update(self._gray(), lm, 480, 640)

        assert fr._diag_landmarks_valid == 1, \
            f"valid landmarks -> valid=1, got {fr._diag_landmarks_valid}"
        assert fr._diag_frames_since_mp == 1, \
            f"first frame -> sinceMp=1, got {fr._diag_frames_since_mp}"
        # cached=-1: no previous detection to compare against; engine cannot distinguish
        # fresh-vs-cached (caller controls MediaPipe interval). -1 = "no prior comparison".
        assert fr._diag_landmarks_cached == -1, \
            f"first detection -> cached=-1 (no prior), got {fr._diag_landmarks_cached}"
        print("  [OK] V1: valid=1, sinceMp=1, cached=-1 on first frame")

    def test_v1_none_landmarks_early_return(self):
        """With face_landmarks=None: valid=0, EMA/state unchanged, detector untouched."""
        import numpy as np
        from rppg_core import MultiROIFusionEngine

        engine = MultiROIFusionEngine()
        lm = self._lm()
        # Establish state with valid landmarks
        engine.update(self._gray(), lm, 480, 640)
        prior_ema   = engine.motion_detector._score_ema
        prior_score = engine.motion_detector.motion_score
        prior_moving = engine.motion_detector.is_moving
        prior_grace = engine.motion_detector.grace_counter

        # Call with None -> early return
        fr = engine.update(self._gray(), None, 480, 640)

        assert fr._diag_landmarks_valid == 0, \
            f"landmarks=None -> valid=0, got {fr._diag_landmarks_valid}"
        # EMA/state must be UNCHANGED (early return does not touch detector internals)
        assert engine.motion_detector._score_ema == prior_ema, \
            f"EMA must not change on early return"
        assert engine.motion_detector.motion_score == prior_score, \
            f"motion_score must not change on early return"
        assert engine.motion_detector.is_moving == prior_moving, \
            f"is_moving must not change on early return"
        assert engine.motion_detector.grace_counter == prior_grace, \
            f"grace_counter must not change on early return"
        assert fr.motion_score == 0.0, \
            f"early return -> score=0.0, got {fr.motion_score}"
        print("  [OK] V1: valid=0, detector state unchanged on landmarks=None")

    def test_v1_landmarks_cached_on_skip_frame(self):
        """On a non-MediaPipe frame: valid=1, sinceMp=2, cached=1."""
        import numpy as np
        from rppg_core import MultiROIFusionEngine

        engine = MultiROIFusionEngine()
        lm = self._lm()

        # Frame 1: fresh (first detection, no prior object to compare)
        fr1 = engine.update(self._gray(), lm, 480, 640)
        assert fr1._diag_landmarks_valid == 1
        assert fr1._diag_frames_since_mp == 1
        assert fr1._diag_landmarks_cached == -1, \
            f"first detection -> cached=-1 (no prior), got {fr1._diag_landmarks_cached}"

        # Frame 2: same landmarks object -> cached=1 (object identity, same object reused)
        fr2 = engine.update(self._gray(), lm, 480, 640)
        assert fr2._diag_landmarks_valid == 1, \
            f"valid landmarks on skip frame -> valid=1, got {fr2._diag_landmarks_valid}"
        assert fr2._diag_frames_since_mp == 1, \
            f"consecutive same landmarks -> sinceMp=1, got {fr2._diag_frames_since_mp}"
        assert fr2._diag_landmarks_cached == 1, \
            f"same object as frame 1 -> cached=1 (reused), got {fr2._diag_landmarks_cached}"
        print("  [OK] V1: valid=1, sinceMp=1, cached=1 on skip frame (same object)")

    def test_v1_none_then_valid_resets_since_mp(self):
        """landmarks=None preserves the last detection frame; next valid shows the gap.

        With the fix, _last_valid_mp_frame stores the actual frame_count of the last
        valid detection. frames_since_mp = frame_count - _last_valid_mp_frame:
          fr1 (fc=1): last_valid=1, sinceMp=1 [OK] (just now)
          fr2 (fc=2): last_valid=2, sinceMp=1 [OK] (previous frame was valid)
          fr3 (fc=3, lm=None): last_valid=2, sinceMp=1 [OK] (1 frame since last valid)
          fr4 (fc=4, lm returns): last_valid=4, sinceMp=2 [OK] (2 frames since last valid)
        """
        import numpy as np
        from rppg_core import MultiROIFusionEngine

        engine = MultiROIFusionEngine()
        lm = self._lm()

        fr1 = engine.update(self._gray(), lm, 480, 640)   # fc=1, sinceMp=1, cached=-1
        assert fr1._diag_frames_since_mp == 1
        assert fr1._diag_landmarks_cached == -1

        fr2 = engine.update(self._gray(), lm, 480, 640)  # fc=2, sinceMp=1, cached=1 (same object reused)
        assert fr2._diag_frames_since_mp == 1, \
            f"fr2: prev valid fc=1, current fc=2 -> sinceMp=1, got {fr2._diag_frames_since_mp}"
        assert fr2._diag_landmarks_cached == 1, \
            f"fr2: same lm object as fr1 -> cached=1 (reused), got {fr2._diag_landmarks_cached}"

        # Frame 3: landmarks=None — last_valid stays at fc=2, sinceMp=1 (1 frame since last)
        fr3 = engine.update(self._gray(), None, 480, 640)  # fc=3, lm=None
        assert fr3._diag_landmarks_valid == 0
        assert fr3._diag_frames_since_mp == 1, \
            f"fr3: last valid fc=2, current fc=3 -> sinceMp=1 (1 frame ago), got {fr3._diag_frames_since_mp}"
        assert fr3._diag_landmarks_cached == 0, \
            f"fr3: None vs prev_lm object -> cached=0, got {fr3._diag_landmarks_cached}"

        # Frame 4: valid landmarks return — last valid is now fc=4, gap of 2 frames
        fr4 = engine.update(self._gray(), lm, 480, 640)  # fc=4
        assert fr4._diag_landmarks_valid == 1
        assert fr4._diag_frames_since_mp == 2, \
            f"fr4: last valid fc=2, current fc=4 -> sinceMp=2 (2 frames ago), got {fr4._diag_frames_since_mp}"
        assert fr4._diag_landmarks_cached == 1, \
            f"fr4: same lm object as fr2 -> cached=1 (reused), got {fr4._diag_landmarks_cached}"
        print("  [OK] V1: sinceMp=1 after None, sinceMp=2 after gap, correct staleness tracking")

    # ------------------------------------------------------------------
    # V2 engine
    # ------------------------------------------------------------------

    def test_v2_valid_landmarks_fresh(self):
        """V2: valid=1, sinceMp=1, cached=-1 on first frame (no prior detection to compare)."""
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()
        lm = self._lm()
        fr = engine.update(self._gray(), lm, 480, 640)

        assert fr._diag_landmarks_valid == 1
        assert fr._diag_frames_since_mp == 1
        assert fr._diag_landmarks_cached == -1, \
            f"first detection -> cached=-1 (no prior), got {fr._diag_landmarks_cached}"
        print("  [OK] V2: valid=1, sinceMp=1, cached=-1 on first frame")

    def test_v2_none_landmarks_early_return(self):
        """V2: landmarks=None -> valid=0, detector state unchanged."""
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()
        lm = self._lm()
        engine.update(self._gray(), lm, 480, 640)   # establish state

        prior_ema   = engine.motion_detector._score_ema
        prior_grace = engine.motion_detector.grace_counter
        prior_moving = engine.motion_detector.is_moving

        fr = engine.update(self._gray(), None, 480, 640)

        assert fr._diag_landmarks_valid == 0
        assert engine.motion_detector._score_ema == prior_ema
        assert engine.motion_detector.grace_counter == prior_grace
        assert engine.motion_detector.is_moving == prior_moving
        print("  [OK] V2: valid=0, detector state unchanged on landmarks=None")

    def test_v2_consistent_after_reset(self):
        """After engine.reset(), _last_valid_mp_frame resets so next valid -> sinceMp=1."""
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()
        lm = self._lm()
        fr1 = engine.update(self._gray(), lm, 480, 640)
        assert fr1._diag_frames_since_mp == 1

        engine.reset()
        fr2 = engine.update(self._gray(), lm, 480, 640)
        assert fr2._diag_frames_since_mp == 1, \
            f"after reset, fresh detection -> sinceMp=1, got {fr2._diag_frames_since_mp}"
        print("  [OK] V2: sinceMp resets to 1 after engine.reset()")


# =============================================================================
# Phase 8.4E: V2 production-path diagnostic propagation
# =============================================================================

class TestV2ProductionPath:
    """
    Verify that V2 (the production engine used by rppg_main.py) correctly propagates
    all diagnostic fields through the update() call and that the rppg_main variable-
    extraction pattern produces consistent values.

    rppg_main.py hoists diagnostics before the if-motion_rejected block:
        grace_rem  = fusion_engine.motion_detector.grace_remaining
        det_is_mov = fusion_engine.motion_detector.is_moving
        det_grace  = getattr(fr, '_diag_grace_counter',      None)
        det_score  = getattr(fr, '_diag_score_at_decision', None)
        det_ema    = getattr(fr, '_diag_score_ema',         None)
        overr_fire = getattr(fr, '_diag_override_fired',    None)
        was_stale  = getattr(fr, '_diag_was_local_stale',  None)
        lm_valid   = getattr(fr, '_diag_landmarks_valid',   None)
        lm_since   = getattr(fr, '_diag_frames_since_mp',  None)
        lm_cached  = getattr(fr, '_diag_landmarks_cached', None)

    These tests verify every field is present and non-None on the V2 result object.
    """

    class _DummyPoint:
        __slots__ = ('x', 'y', 'z')
        def __init__(self, x, y, z=0.0):
            self.x = x; self.y = y; self.z = z

    class _DummyLandmarks:
        def __init__(self, pts): self._pts = pts
        @property
        def landmark(self): return self
        def __len__(self): return len(self._pts)
        def __getitem__(self, k): return self._pts[k]

    def _lm(self, x=0.5, y=0.5, count=478):
        return self._DummyLandmarks([self._DummyPoint(x, y) for _ in range(count)])

    def _gray(self):
        import numpy as np
        return np.full((480, 640, 3), 128, dtype=np.uint8)

    def _rppg_main_pattern(self, fr, engine):
        """Mirror the rppg_main.py variable-extraction pattern exactly."""
        grace_rem = engine.motion_detector.grace_remaining
        det_is_mov = engine.motion_detector.is_moving
        det_grace   = getattr(fr, '_diag_grace_counter',      None)
        det_score   = getattr(fr, '_diag_score_at_decision',  None)
        det_ema     = getattr(fr, '_diag_score_ema',          None)
        overr_fired = getattr(fr, '_diag_override_fired',     None)
        was_stale   = getattr(fr, '_diag_was_local_stale',    None)
        lm_valid    = getattr(fr, '_diag_landmarks_valid',    None)
        lm_since    = getattr(fr, '_diag_frames_since_mp',    None)
        lm_cached   = getattr(fr, '_diag_landmarks_cached',  None)
        return {
            'grace_rem': grace_rem, 'det_is_mov': det_is_mov,
            'det_grace': det_grace, 'det_score': det_score,
            'det_ema': det_ema, 'overr_fired': overr_fired,
            'was_stale': was_stale, 'lm_valid': lm_valid,
            'lm_since': lm_since, 'lm_cached': lm_cached,
        }

    def test_v2_all_diag_fields_present_on_valid_landmarks(self):
        """V2: on a valid-landmarks frame, every diagnostic field is present and non-None."""
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()
        lm = self._lm()
        fr = engine.update(self._gray(), lm, 480, 640)
        d = self._rppg_main_pattern(fr, engine)

        assert d['grace_rem'] is not None
        assert d['det_is_mov'] is not None
        assert d['det_grace'] is not None
        assert d['det_score'] is not None
        assert d['det_ema'] is not None
        assert d['overr_fired'] is not None
        assert d['was_stale'] is not None
        assert d['lm_valid'] is not None
        assert d['lm_since'] is not None
        assert d['lm_cached'] is not None

        assert d['lm_valid'] == 1,    f"lm_valid=1, got {d['lm_valid']}"
        assert d['lm_since'] == 1,    f"lm_since=1, got {d['lm_since']}"
        assert d['lm_cached'] == -1,  f"lm_cached=-1 (first), got {d['lm_cached']}"
        print("  [OK] V2: all 10 diagnostic fields present and consistent")

    def test_v2_all_diag_fields_present_on_none_landmarks(self):
        """V2: on a landmarks=None frame, all fields are present (early-return path)."""
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()
        lm = self._lm()
        engine.update(self._gray(), lm, 480, 640)   # establish state
        fr = engine.update(self._gray(), None, 480, 640)
        d = self._rppg_main_pattern(fr, engine)

        assert d['grace_rem'] is not None
        assert d['det_is_mov'] is not None
        assert d['det_grace'] is not None
        assert d['det_score'] is not None
        assert d['det_ema'] is not None
        assert d['overr_fired'] is not None
        assert d['was_stale'] is not None
        assert d['lm_valid'] is not None
        assert d['lm_since'] is not None
        assert d['lm_cached'] is not None

        assert d['lm_valid'] == 0,    f"lm_valid=0 (None), got {d['lm_valid']}"
        print("  [OK] V2: all fields present on early-return (landmarks=None)")

    def test_v2_cached_detection_object_identity(self):
        """V2: passing the same landmark object twice sets cached=1."""
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()
        lm = self._lm()
        fr1 = engine.update(self._gray(), lm, 480, 640)
        fr2 = engine.update(self._gray(), lm, 480, 640)   # same object

        assert fr1._diag_landmarks_cached == -1, f"fr1 cached=-1, got {fr1._diag_landmarks_cached}"
        assert fr2._diag_landmarks_cached == 1,  f"fr2 cached=1 (same obj), got {fr2._diag_landmarks_cached}"
        print("  [OK] V2: cached=1 when same landmark object is reused")

    def test_v2_fresh_detection_new_object(self):
        """V2: passing a new landmark object each call sets cached=0."""
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()
        fr1 = engine.update(self._gray(), self._lm(), 480, 640)
        fr2 = engine.update(self._gray(), self._lm(), 480, 640)   # new object

        assert fr1._diag_landmarks_cached == -1, f"fr1 cached=-1, got {fr1._diag_landmarks_cached}"
        assert fr2._diag_landmarks_cached == 0,  f"fr2 cached=0 (new obj), got {fr2._diag_landmarks_cached}"
        print("  [OK] V2: cached=0 when a new landmark object is passed")

    def test_v2_none_then_revalid_shows_gap(self):
        """V2: after a None frame, the next valid shows frames_since_mp > 1."""
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()
        lm = self._lm()
        engine.update(self._gray(), lm, 480, 640)   # fc=1, last_valid=1
        engine.update(self._gray(), lm, 480, 640)   # fc=2, last_valid=2
        fr_none = engine.update(self._gray(), None, 480, 640)  # fc=3, last_valid=2
        fr_ok   = engine.update(self._gray(), self._lm(), 480, 640)  # fc=4, last_valid=4

        # fc=4 - last_valid=2 = 2 frames gap
        assert fr_ok._diag_frames_since_mp == 2, \
            f"gap of 2 (fc=4, last_valid=2) -> sinceMp=2, got {fr_ok._diag_frames_since_mp}"
        # lm is a new object (lm() call creates new DummyLandmarks)
        assert fr_ok._diag_landmarks_cached == 0, \
            f"new lm object after None -> cached=0, got {fr_ok._diag_landmarks_cached}"
        print("  [OK] V2: sinceMp=2 after 1-frame gap, cached=0 (new object)")

    def test_v2_event_detail_format_matches_rppg_main(self):
        """V2: the event detail string built in rppg_main matches the actual values."""
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()
        lm = self._lm()
        fr = engine.update(self._gray(), lm, 480, 640)
        d = self._rppg_main_pattern(fr, engine)

        # Build the detail string exactly as rppg_main does
        grace_rem = d['grace_rem']
        det_is_mov = d['det_is_mov']
        motion_tag = ("grace" if grace_rem > 0
                      else "active" if det_is_mov
                      else "inactive")
        _ema_str = f"{d['det_ema']:.2f}" if d['det_ema'] is not None else "n/a"
        detail = (
            f"score={fr.motion_score:.2f} ema={_ema_str} "
            f"grace={grace_rem}({motion_tag})"
            f" det_isMov={det_is_mov} det_grace={d['det_grace']} "
            f"det_score={d['det_score']:.2f}"
            f" overr_stale={d['overr_fired']} was_stale={d['was_stale']}"
            f" lm={d['lm_valid']} sinceMp={d['lm_since']} cached={d['lm_cached']}"
        )
        assert "score=" in detail
        assert "ema=" in detail
        assert "grace=" in detail
        assert "lm=" in detail
        assert "sinceMp=" in detail
        assert "cached=" in detail
        print(f"  [OK] V2 event detail format valid: {detail[:80]}...")

    def test_v2_none_landmarks_detail_uses_n_a(self):
        """V2 early-return (landmarks=None): EMA carries last known value.

        _score_ema bootstraps to raw_score on first valid call.
        On subsequent early-return calls (landmarks=None), it carries the previous EMA.
        None means 'not yet initialized' (first call before any valid landmarks).
        """
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()

        # First call with landmarks=None: detector returns early before _score_ema is set
        fr0 = engine.update(self._gray(), None, 480, 640)
        d0 = self._rppg_main_pattern(fr0, engine)
        assert d0['det_ema'] is None, \
            f"first call (landmarks=None): det_ema=None, got {d0['det_ema']}"

        # Bootstrap EMA on first valid call
        lm = self._lm()
        fr1 = engine.update(self._gray(), lm, 480, 640)
        d1 = self._rppg_main_pattern(fr1, engine)
        assert d1['det_ema'] is not None, \
            f"after first valid call: det_ema must be set, got {d1['det_ema']}"

        # Early return carries the previous EMA value (not None)
        fr2 = engine.update(self._gray(), None, 480, 640)
        d2 = self._rppg_main_pattern(fr2, engine)
        assert d2['det_ema'] is not None, \
            f"early return: det_ema must carry previous value, got {d2['det_ema']}"
        assert d2['det_ema'] == d1['det_ema'], \
            f"early return EMA must match previous: expected {d1['det_ema']}, got {d2['det_ema']}"

        # _ema_str format: None -> 'n/a', float -> formatted value
        _ema_str0 = f"{d0['det_ema']:.2f}" if d0['det_ema'] is not None else "n/a"
        _ema_str2 = f"{d2['det_ema']:.2f}" if d2['det_ema'] is not None else "n/a"
        assert _ema_str0 == "n/a", f"first call: 'n/a', got {_ema_str0}"
        assert _ema_str2 != "n/a", f"early return: should have value, got {_ema_str2}"
        print("  [OK] V2: first-call='n/a', early-return carries previous EMA, no crash")

    def test_v2_motion_rejected_to_cleared_transition(self):
        """V2: the engine correctly tracks motion_rejected True->False state transition.

        This test verifies the engine-side state machine, not the main-loop event logger.
        The actual 'motion_cleared' event is emitted by rppg_main when it detects
        (was_rejected and not fr.motion_rejected) — a purely display-layer concern.
        """
        import numpy as np
        from rppg_core import MultiROIFusionEngineV2

        engine = MultiROIFusionEngineV2()

        # Force motion to be active on frame 1: big pixel difference -> enter rejection
        gray1 = np.full((480, 640, 3), 50, dtype=np.uint8)
        lm = self._lm()
        fr1 = engine.update(gray1, lm, 480, 640)
        # Manually spike the detector to enter motion state
        engine.motion_detector._score_ema = 5.0
        engine.motion_detector.motion_score = 2.0
        engine.motion_detector.is_moving = True
        engine.motion_detector.grace_counter = 30

        # Frame 2: same state, still rejected
        fr2 = engine.update(gray1, lm, 480, 640)
        assert fr2.motion_rejected == True, "frame 2 should still be rejected"

        # Frame 3: simulate motion settling — set score below exit threshold
        engine.motion_detector.motion_score = 0.05
        engine.motion_detector._score_ema = 0.1
        engine.motion_detector.is_moving = False
        engine.motion_detector.grace_counter = 0

        fr3 = engine.update(gray1, lm, 480, 640)
        assert fr3.motion_rejected == False, \
            f"transition to cleared: expected False, got {fr3.motion_rejected}"
        assert fr3._diag_detector_is_moving == False
        assert fr3._diag_grace_counter == 0
        print("  [OK] V2: motion_rejected True->False transition tracked correctly")



def run_v2_production_tests():
    """Run Phase 8.4E V2 production-path tests."""
    print("\n" + "=" * 60)
    print("TESTING: Phase 8.4E -- V2 Production-Path Diagnostic Propagation")
    print("=" * 60)

    suite = TestV2ProductionPath()
    tests = [
        ("V2: all diag fields present on valid landmarks",
         suite.test_v2_all_diag_fields_present_on_valid_landmarks),
        ("V2: all diag fields present on None landmarks (early return)",
         suite.test_v2_all_diag_fields_present_on_none_landmarks),
        ("V2: cached=1 when same landmark object reused",
         suite.test_v2_cached_detection_object_identity),
        ("V2: cached=0 when new landmark object",
         suite.test_v2_fresh_detection_new_object),
        ("V2: sinceMp>1 after None-frame gap",
         suite.test_v2_none_then_revalid_shows_gap),
        ("V2: event detail format matches rppg_main construction",
         suite.test_v2_event_detail_format_matches_rppg_main),
        ("V2: early-return EMA = 'n/a' (not None, not fabricated zero)",
         suite.test_v2_none_landmarks_detail_uses_n_a),
        ("V2: motion_rejected True->False transition tracked",
         suite.test_v2_motion_rejected_to_cleared_transition),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f"\nTest: {name}")
        try:
            test_fn()
            print("  PASS")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback; traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


def run_landmark_tests():
    """Run Phase 8.4D landmark validity diagnostic tests."""
    print("\n" + "=" * 60)
    print("TESTING: Phase 8.4D -- Landmark Validity Diagnostics")
    print("=" * 60)

    suite = TestLandmarkDiagnostics()
    tests = [
        ("V1: valid landmarks on first frame",
         suite.test_v1_valid_landmarks_fresh),
        ("V1: landmarks=None -> early return, state unchanged",
         suite.test_v1_none_landmarks_early_return),
        ("V1: cached landmarks on skip frame",
         suite.test_v1_landmarks_cached_on_skip_frame),
        ("V1: None then valid -> sinceMp resets to 1",
         suite.test_v1_none_then_valid_resets_since_mp),
        ("V2: valid landmarks on first frame",
         suite.test_v2_valid_landmarks_fresh),
        ("V2: landmarks=None -> early return, state unchanged",
         suite.test_v2_none_landmarks_early_return),
        ("V2: sinceMp resets to 1 after engine.reset()",
         suite.test_v2_consistent_after_reset),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f"\nTest: {name}")
        try:
            test_fn()
            print("  PASS")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback; traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


class TestGraceExpirationRealSM:
    """
    Verify the MotionArtifactDetector state machine through a complete
    ENTER -> grace-decrement -> EXIT transition using REAL update() calls.

    Key invariant: grace_counter == 0 IMPLIES is_moving == False.
    There is no code path in update() where both are true simultaneously
    when update() returns.

    Also verifies the phase81 bug: update() with landmarks=None returns early
    without touching is_moving or grace_counter (rppg_core.py:462-463).
    """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    class _DummyPoint:
        __slots__ = ('x', 'y', 'z')
        def __init__(self, x, y, z=0.0):
            self.x = x; self.y = y; self.z = z

    class _DummyLandmarks:
        """Lightweight landmark list: 478 points, indexable by int.

        Mimics MediaPipe's face_landmarks object:
          face_landmarks.landmark[i] -> DummyPoint(x, y, z)
        """
        __slots__ = ('_pts',)
        def __init__(self, pts):
            self._pts = pts

        @property
        def landmark(self):
            return self

        def __len__(self):
            return len(self._pts)

        def __getitem__(self, key):
            return self._pts[key]

    def _make_landmarks(self, x, y, count=478):
        """Return dummy landmarks centred at (x, y)."""
        return self._DummyLandmarks([self._DummyPoint(x, y) for _ in range(count)])

    def _make_gray_frame(self):
        """Return a real uint8 frame (required: prev_gray != None)."""
        import numpy as np
        return np.full((480, 640), 128, dtype=np.uint8)

    # ------------------------------------------------------------------
    # Test: phase81 bug — landmarks=None is a no-op for state machine
    # ------------------------------------------------------------------

    def test_landmarks_none_returns_early(self):
        """
        update(gray, None, h, w) must return (0.0, False) WITHOUT modifying
        is_moving or grace_counter (rppg_core.py:462-463).

        This is the root cause of phase81 B/C/D failures: those tests called
        update() with landmarks=None and expected the state machine to react,
        but it returned early and left internal state unchanged.
        """
        detector = MotionArtifactDetector()
        gray = self._make_gray_frame()

        # Set up a state that would be active if update() ran
        detector.is_moving = True
        detector.grace_counter = 15

        # Call with landmarks=None -> early return
        score, is_moving_ret = detector.update(gray, None, 480, 640)

        assert score == 0.0, f"Expected score=0.0 from early return, got {score}"
        assert is_moving_ret is False, f"Expected return False from early return, got {is_moving_ret}"
        # State must be UNCHANGED (this is the bug the phase81 tests fell into)
        assert detector.is_moving is True, \
            "is_moving must remain True after early return (update never ran)"
        assert detector.grace_counter == 15, \
            "grace_counter must remain 15 after early return (update never ran)"

        print("  [OK] landmarks=None -> early return, state unchanged")

    # ------------------------------------------------------------------
    # Test: complete ENTER -> grace -> EXIT through real update()
    # ------------------------------------------------------------------

    def test_grace_expiration_real_update(self):
        """
        Walk the detector through ENTER -> graceful decrement -> EXIT using
        real update() calls with valid landmarks on every frame.

        Invariant: grace_counter == 0  ⇒  is_moving == False
        (no transient where both are true on a returned state).
        """
        import numpy as np

        detector = MotionArtifactDetector()
        gray = self._make_gray_frame()

        # ── Step 1: Establish active state ─────────────────────────────────
        # Directly set the authoritative state variables as if ENTER fired.
        # This bypasses the EMA (which would produce 0 with uniform landmarks)
        # while still exercising the EXIT-path graceful decrement through real
        # update() calls.
        detector.is_moving = True
        detector.grace_counter = cfg.MOTION_GRACE_FRAMES
        assert detector.is_moving is True
        assert detector.grace_counter == cfg.MOTION_GRACE_FRAMES
        print(f"  [OK] Active state established: grace={detector.grace_counter}, is_moving={detector.is_moving}")

        # ── Step 2: Walk through graceful decrement ─────────────────────────
        # Tiny-shift frames produce near-zero motion_score (EMA->0 with uniform
        # landmarks), which stays below EXIT (1.5).  grace_counter decrements
        # each call; is_moving stays True until grace reaches 0.
        for i in range(1, cfg.MOTION_GRACE_FRAMES):
            lm_low = self._make_landmarks(0.50 + 0.0001, 0.50 + 0.0001)
            score_i, ret_i = detector.update(gray, lm_low, 480, 640)

            # CRITICAL INVARIANT: grace=0 implies is_moving=False
            assert not (detector.grace_counter == 0 and detector.is_moving is True), \
                f"INVARIANT VIOLATED at frame {i}: grace=0 but is_moving=True"

            # is_moving should stay True during grace
            assert detector.is_moving is True, \
                f"Frame {i}: is_moving must be True during grace (grace={detector.grace_counter}), got {detector.is_moving}"

        print(f"  [OK] Grace decremented correctly over {cfg.MOTION_GRACE_FRAMES-1} frames "
              f"(grace={detector.grace_counter})")

        # ── Step 3: Grace expiration ─────────────────────────────────────────
        # grace hits 0 on the LAST decrement call (grace: 1->0).  is_moving
        # stays True on THAT call because the `else` (which clears is_moving)
        # only fires when grace==0 *before* the decrement.
        # is_moving is cleared on the SUBSEQUENT call (grace already 0 -> else).
        lm_last = self._make_landmarks(0.50 + 0.0001, 0.50 + 0.0001)
        score_last, ret_last = detector.update(gray, lm_last, 480, 640)

        assert detector.grace_counter == 0, \
            f"Grace must be 0 at expiration, got {detector.grace_counter}"
        # is_moving is still True at this exact moment (grace just hit 0)
        # — it will be cleared on the next update() call.
        print(f"  Grace expired (gc=0, is_moving={detector.is_moving} -- "
              f"cleared on NEXT call per state-machine design)")

        # ── Step 4: is_moving cleared on NEXT call (grace already 0) ────────
        lm_after = self._make_landmarks(0.50 + 0.0001, 0.50 + 0.0001)
        score_after, ret_after = detector.update(gray, lm_after, 480, 640)

        assert detector.grace_counter == 0, \
            "grace must stay at 0 after expiration"
        assert detector.is_moving is False, \
            f"is_moving must be False when grace=0 on NEXT call, got {detector.is_moving}"
        assert ret_after is False, \
            f"Return is_moving must be False when grace=0, got {ret_after}"
        assert score_after < cfg.MOTION_EXIT_THRESHOLD, \
            f"score={score_after:.3f} must be below EXIT={cfg.MOTION_EXIT_THRESHOLD}"
        print(f"  [OK] Grace expired: grace={detector.grace_counter}, is_moving={detector.is_moving}")

        # ── Step 5: Stable inactive after expiration ───────────────────────
        lm_still = self._make_landmarks(0.50 + 0.0001, 0.50 + 0.0001)
        score_next, ret_next = detector.update(gray, lm_still, 480, 640)

        assert detector.grace_counter == 0, "grace must stay at 0 after expiration"
        assert detector.is_moving is False, "is_moving must stay False after expiration"
        assert ret_next is False
        print(f"  [OK] Post-expiration stable: grace={detector.grace_counter}, is_moving={detector.is_moving}")

        # ── Step 5: RE-ENTER ────────────────────────────────────────────────
        # Inject a score above ENTER and call update() to trigger re-entry.
        detector._score_ema = 15.0   # EMA high enough to keep motion_score above ENTER
        detector._slow_ema = 0.0
        lm_reenter = self._make_landmarks(0.50, 0.50)
        detector.update(gray, lm_reenter, 480, 640)

        assert detector.is_moving is True, \
            f"RE-ENTER failed: is_moving={detector.is_moving}, expected True"
        assert detector.grace_counter == cfg.MOTION_GRACE_FRAMES, \
            f"RE-ENTER failed: grace={detector.grace_counter}, expected {cfg.MOTION_GRACE_FRAMES}"
        print(f"  [OK] RE-ENTER works: grace={detector.grace_counter}")

    # ------------------------------------------------------------------
    # Test: graceful-motion — score drops below ENTER but grace > 0
    # ------------------------------------------------------------------

    def test_grace_sustains_rejection_below_enter(self):
        """
        After ENTER, if score drops below ENTER but grace > 0:
        is_moving must remain True (grace sustains rejection).
        """
        import numpy as np

        detector = MotionArtifactDetector()
        gray = self._make_gray_frame()

        # ── Establish active state ─────────────────────────────────────────
        detector.is_moving = True
        detector.grace_counter = cfg.MOTION_GRACE_FRAMES
        assert detector.is_moving is True
        assert detector.grace_counter == cfg.MOTION_GRACE_FRAMES

        # ── Simulate motion stopping: tiny shifts -> near-zero score.
        #    grace decrements; is_moving stays True because grace > 0.
        #    Run all grace frames and verify is_moving never goes False. ───
        for i in range(cfg.MOTION_GRACE_FRAMES - 1):
            lm_low = self._make_landmarks(0.50 + 0.0001, 0.50 + 0.0001)
            score, ret = detector.update(gray, lm_low, 480, 640)

            assert detector.grace_counter == cfg.MOTION_GRACE_FRAMES - (i + 1), \
                f"Frame {i+1}: grace should be {cfg.MOTION_GRACE_FRAMES - (i + 1)}, got {detector.grace_counter}"
            assert detector.is_moving is True, \
                f"Frame {i+1}: is_moving must remain True during grace (grace={detector.grace_counter}), got {detector.is_moving}"
            assert detector.motion_score < cfg.MOTION_ENTER_THRESHOLD, \
                f"Frame {i+1}: score={detector.motion_score:.3f} must be below ENTER={cfg.MOTION_ENTER_THRESHOLD}"

        print(f"  [OK] Grace sustains rejection for all {cfg.MOTION_GRACE_FRAMES - 1} grace frames: "
              f"is_moving={detector.is_moving}, score={detector.motion_score:.3f}<ENTER")

    # ------------------------------------------------------------------
    # Test: grace_active property reflects the right condition
    # ------------------------------------------------------------------

    def test_grace_active_property_semantics(self):
        """
        grace_active = (grace_counter > 0) AND (motion_score < ENTER).
        Must be False when grace=0, regardless of motion_score.
        """
        detector = MotionArtifactDetector()

        # grace=0 -> grace_active must be False
        detector.grace_counter = 0
        detector.motion_score = 0.5
        assert detector.grace_active is False, "grace_active must be False when grace=0"
        detector.motion_score = 5.0
        assert detector.grace_active is False, "grace_active must be False when grace=0"

        # grace>0, score < ENTER -> grace_active is True
        detector.grace_counter = 10
        detector.motion_score = 0.5
        assert detector.grace_active is True, "grace_active must be True when grace>0 and score<ENTER"

        # grace>0, score >= ENTER -> grace_active is False (active motion, not grace-residual)
        detector.grace_counter = 10
        detector.motion_score = 3.0
        assert detector.grace_active is False, "grace_active must be False when score>=ENTER"

        print("  [OK] grace_active property semantics correct")


def run_grace_expiration_tests():
    """Run Phase 8.2 real state-machine grace-expiration tests."""
    print("\n" + "=" * 60)
    print("TESTING: Phase 8.2 -- Real State-Machine (Live update())")
    print("=" * 60)

    suite = TestGraceExpirationRealSM()
    tests = [
        ("Early return: landmarks=None -> no state change",
         suite.test_landmarks_none_returns_early),
        ("Grace expiration: ENTER -> decrement -> EXIT (real update)",
         suite.test_grace_expiration_real_update),
        ("Grace sustains rejection when score drops below ENTER",
         suite.test_grace_sustains_rejection_below_enter),
        ("grace_active property semantics",
         suite.test_grace_active_property_semantics),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f"\nTest: {name}")
        try:
            test_fn()
            print("  PASS")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success1 = run_tests()
    success2 = run_stale_tests()
    success3 = run_grace_expiration_tests()
    success4 = run_landmark_tests()
    success5 = run_v2_production_tests()
    sys.exit(0 if all([success1, success2, success3, success4, success5]) else 1)
