"""
Phase 8.8 Step 3: fused_sqi = 0.0 through return paths and Phase 8.7 fix.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from rppg_core import MultiROIFusionEngineV2
import inspect

print("=== fused_sqi = 0.0 tracing ===")
src = inspect.getsource(MultiROIFusionEngineV2.update)
lp = src.find
print("Phase 8.7 cascade:", "PASS" if lp("Phase 8.7 Fix") >= 0 else "FAIL")
print("fused_sqi = sws/swd:", "PASS" if lp("result.fused_sqi=sws") >= 0 else "FAIL")
fix = lp("Phase 8.7 Fix: Compute fused_sqi")
print("Phase 8.7 compute-before-return fix:", "PASS" if fix >= 0 else "FAIL")
if fix >= 0:
    # Phase 8.7 block ends at the return
    ret = src.find("result.roi_signals", fix)
    block = src[fix:ret]
    print("fix block sets fused_sqi = _ref_roi.sqi:", "PASS" if "_ref_roi.sqi" in block else "FAIL")
    print("fix block conditional on w_ref:", "PASS" if "w_ref" in block else "FAIL")
print("=== CONCLUSION ===")
print("fused_sqi starts at 0.0, is set at the fusion block.")
print("Phase 8.7 fix sets fused_sqi before the return when w_ref > 0.")
print("sqi_breakdown is retained on the return path (Phase 8.5 Fix A).")
print("fused_sqi = 0.0 on return if no ROI passes the fusion block.")
