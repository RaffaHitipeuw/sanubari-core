# Phase 9.0 — Signal validation: Subject 4

## Notes

- Subject 4 of Dataset_rPPG-10. Each ROI video is a 64x64 crop of one face region, so the whole frame is treated as the ROI.
- SKIPPED ROI - forehead: Subject_4_Forehead_.avi (Cannot open video: Dataset_rPPG-10\Subject_4\Subject_4_Forehead_.avi)
- SKIPPED ROI - cheek_left: Subject_4_Cheek1_.avi (Cannot open video: Dataset_rPPG-10\Subject_4\Subject_4_Cheek1_.avi)
- SKIPPED ROI - cheek_right: Subject_4_Cheek2_.avi (Cannot open video: Dataset_rPPG-10\Subject_4\Subject_4_Cheek2_.avi)
- ECG reference: Subject_4_ECG.npy - 945 R-peaks, mean HR 94.7 BPM, SDNN 40.2 ms, ECG inter-beat CV 0.063.
- The ECG-video start offset for rPPG-10 is not published; beat-level comparisons are therefore hypothesis-level only.
- All interval statistics describe the detector's output on this recording. They are not a measurement of the subject's heart rhythm.

## Category legend

- **OK** - OK. Signal usable, detection consistent with the reference
- **A** - A. Genuinely poor signal quality
- **B** - B. Peak-detection failure
- **C** - C. Preprocessing or ROI artifact
- **D** - D. Inconclusive - reference sensor required
