# Laporan Reorganisasi Repository

Pendekatan: **audit dulu, lalu pindahkan hanya yang terbukti aman.** Tidak ada algoritma, threshold, pipeline, API, atau perilaku runtime yang diubah. Tidak ada file yang dihapus kecuali cache `__pycache__`/`*.pyc` (hasil generate).

Catatan: arsip tidak berisi `.git`, jadi "riwayat penggunaan" tidak bisa diperiksa. Status "tidak terpakai" dinilai dari import, string path, perintah yang dicetak script, dan referensi di dokumentasi.

## 1. Struktur final

```
Health/
├── README.md  .req.txt  .gitattributes  .gitignore*  pytest.ini*
├── rppg_main.py                    entry point
├── rppg_core / signal / sqi / roi / temporal / uncertainty / physio_state /
│   vitals / algorithms / config / ai .py   + rppg_sessions.db     (engine, tidak disentuh)
├── rppg_benchmark*.py              framework benchmark Phase 1/2 (diimpor engine -> tetap di root)
├── benchmark_video / benchmark_synthetic_example / benchmark_stabilize .py,
│   phase2_data_acquisition.py, rppg_phase2_realbenchmark.py, capture_real_face.py   (CLI terdokumentasi)
├── rppg_phase2_signal_lab.py  rppg_phase2_evolution.py  rppg_phase2_real_benchmark.py
├── synthetic_fixture.mp4/_gt.csv   validation_test_face.png   (dibaca kode via path tetap)
├── models/   Dataset_rPPG-10/   benchmark_results/
├── p3_spatial/ … p11_validation/   satu paket per fase, test tetap di samping kode
├── tests/{engine,benchmark,manual}/
├── benchmarks/experimental/
├── scripts/
├── docs/                           00 … 12 per fase + assets/phase2/ + laporan ini
└── archive/{legacy,mediapipe_env_debug}/
```
\* file baru. Entri di root turun dari 124 menjadi 59.

## 2. Dipindahkan

| Dari | Ke | Jumlah | Alasan / bukti | Edit isi |
|---|---|---|---|---|
| Test engine (`test_ablation, ground_truth, motion_detector, signal_routing, uncertainty, session_diagnostic`) | `tests/engine/` | 6 | Tidak diimpor siapa pun | 1 baris `sys.path` |
| Test benchmark (`test_benchmark_infrastructure, benchmark_alignment, e2e_synthetic, face_dnn_adapter, phase2_acquisition`) | `tests/benchmark/` | 5 | idem | 1 baris `sys.path` (4 file); `phase2_acquisition` tidak perlu |
| 6 script bernama `test_*` yang **bukan test** (`face_landmarker, gate_validation, integration, integration_final, mp_image_mode, topology`) | `tests/manual/` | 6 | Tanpa fungsi/class test, berjalan saat import, memakai path `D:/…` dan kamera/model. `pytest` akan menjalankannya saat collection. Dikecualikan di `pytest.ini` | tidak ada |
| `phase2_validation_gate, run_test_inventory, verify_commands, generate_synthetic_video, signal_debugger` | `scripts/` | 5 | Tidak diimpor, tidak dirujuk dokumen/kode | `sys.path`/`chdir` di 3 file; 1 entri daftar path di `verify_commands` |
| `rppg_phase2_experiments, rppg_phase2_source_audit, rppg_benchmark_face_adapter` | `benchmarks/experimental/` | 3 | Nol importer, nol referensi dokumen | `sys.path` di `experiments` |
| 9 script debug DLL/binding MediaPipe + `temp_extract/` + `temp_mp/` (wheel 11 MB) | `archive/mediapipe_env_debug/` | 11 | Sesi debugging lingkungan (3 Okt), nol referensi | tidak ada |
| `p3_quality_map.py`, `p3_spatial_quality.py` | `archive/legacy/p3_spatial/` | 2 | Dilabeli *legacy* oleh `P3_CLOSURE_REPORT`; SyntaxError; tidak diimpor `__init__` | tidak ada |
| `rppg_benchmark_face.py` | `archive/legacy/benchmark/` | 1 | SyntaxError baris 149, nol referensi | tidak ada |
| 8 PNG bukti validasi | `docs/assets/phase2/` | 8 | Hanya disebut sebagai nama di tabel dokumen | tidak ada |

Peta path lama → baru: `test_X.py` → `tests/<engine\|benchmark\|manual>/test_X.py`; `run_test_inventory.py` dsb. → `scripts/`; perintah lama di dokumen historis (mis. `python test_ground_truth.py`) kini `python tests/engine/test_ground_truth.py`, dijalankan dari root repo.

## 3. Digabung (dokumentasi)

29 file MD → 13 dokumen, digabung **verbatim** (heading diturunkan 2 level; tanpa ringkasan atau dedup, agar tidak ada informasi hilang). Tiap dokumen memuat tabel "file asli → bagian".

| Dokumen | Sumber |
|---|---|
| `00_engine_upgrade` | `upgrade.md` |
| `01_phase1_…` | PHASE1_SCIENTIFIC_AUDIT, PHASE1_CLOSURE_REPORT |
| `02_phase2_…` | PHASE2_REALDATA_UNBLOCK/FINAL, PREEXECUTION_AUDIT, SCIENTIFIC_AUDIT, CLOSURE (urut tanggal, closure terakhir) |
| `03_p3_spatial` | 6 file P3 |
| `04`–`08` | P4 closure; P5, P6, P7, P8 implementation (1 file tiap fase) |
| `09_p9_…` / `10_p10_…` | 3 file P9 / 2 file P10 |
| `11_p11_validation` | 3 MD dari `p11_validation/` |
| `12_engine_runtime_audits` | OPTICAL_FLOW_STABILIZATION_AUDIT, SESSION_DIAGNOSTIC_AUDIT |

`README.md` tetap; teks aslinya dipertahankan dan ditambah peta struktur.

## 4. Dipertahankan di tempat (dan kenapa)

Modul yang diimpor dengan nama datar (`import rppg_core`) **tidak dipindah**: engine sendiri mengimpor `rppg_benchmark`, dan memindahkannya berarti menulis ulang import di engine, yaitu mengubah API modul. Ini sengaja dijadikan tindak lanjut terpisah (bagian 8). Paket `p3…p11` juga tetap karena dokumentasi memakai `pytest p9_domain_generalization/ …`, `from p8_multitask import *`. `rppg_sessions.db` tetap (dibuka relatif oleh `rppg_ai.py`), begitu juga fixture yang path-nya tertulis di kode.

## 5. Benchmark: relevan vs eksperimental

| Kategori | File |
|---|---|
| **Relevan** (dipakai engine/CLI/test) | `rppg_benchmark`, `_gt`, `_video`, `_manifest`, `_failures`, `_alignment`, `_run`, `_face_dnn`, `_face_landmarker`; `benchmark_video`, `benchmark_stabilize` (terbaru, 13 Okt), `benchmark_synthetic_example`, `phase2_data_acquisition`, `rppg_phase2_realbenchmark` |
| **Eksperimental, tetap di root** karena diimpor | `rppg_phase2_signal_lab`, `rppg_phase2_evolution` (diimpor gate dan e2e test); `rppg_benchmark_ablation_audit`, `_reference_audit` (diimpor `test_benchmark_infrastructure`) |
| **Eksperimental, dipisah** | `benchmarks/experimental/*` |
| **Superseded (NEEDS_REVIEW)** | `rppg_phase2_real_benchmark.py` → digantikan `…realbenchmark.py` (berbeda 1.237 baris, bukan duplikat) |

## 6. Kandidat tidak terpakai (tidak ada yang dihapus)

| Keyakinan | Item | Bukti |
|---|---|---|
| Tinggi | `archive/mediapipe_env_debug/temp_mp/*.whl`, `temp_extract/` | Artefak pihak ketiga, bisa diunduh ulang; `temp_extract` memuat file test MediaPipe yang akan ikut ter-collect pytest |
| Tinggi | 9 script `archive/mediapipe_env_debug/*.py` | Debug satu kali, path `C:\miniconda3` (salah ketik `minconda3` di salah satu), 4 rusak sintaks |
| Tinggi | `archive/legacy/**` (3 file) | Rusak sintaks + tak dirujuk; 2 di antaranya diberi label *legacy* oleh dokumen P3 |
| **NEEDS_REVIEW** | `rppg_phase2_real_benchmark.py` | Superseded, **tetapi** `capture_real_face.py` mencetak instruksi yang menyebutnya |
| **NEEDS_REVIEW** | `benchmarks/experimental/rppg_benchmark_face_adapter.py` | Nol referensi; docstring menyebut `benchmark_runner` yang tidak ada di repo |
| **NEEDS_REVIEW** | `benchmarks/experimental/rppg_phase2_experiments.py`, `…_source_audit.py` | Hanya dicek keberadaannya oleh `verify_commands.py` / tanpa referensi sama sekali |
| **NEEDS_REVIEW** | `rppg_benchmark_face.py` | Kemungkinan draf awal; hanya kurang satu `]` (tidak saya perbaiki) |

## 7. Temuan yang sudah ada sebelum reorganisasi (tidak saya ubah)

- `.req.txt` tidak memuat `scikit-learn` (diimpor `rppg_algorithms.py`, yang diimpor engine), `torch` (p5–p10), `pytest`, `matplotlib`. Instalasi bersih dari file itu akan gagal saat `import rppg_core`.
- `P4_CLOSURE_REPORT` merujuk 5 dokumen P4 yang **tidak ada** di arsip (SCIENTIFIC_AUDIT, IMPLEMENTATION_REPORT, EXPERIMENT_MATRIX, ABLATION_REPORT, FAILURE_ANALYSIS).
- 12 file berisi path absolut `D:/main/Projects/Health`; di mesin lain script/test itu tidak jalan.
- `test_p3_quality.py` (0/4 lulus) dan `test_p3_comprehensive.py` (sebagian gagal) sudah gagal sebelum perubahan, di lingkungan verifikasi saya.
- `test_uncertainty.py` memakai `np.random` tanpa seed di beberapa bagian, sehingga angka di output berubah tiap run (pass/fail tetap 5/5).
- Test manual akan menulis ulang `validation_test_face_improved.png` / `validation_test_final.png` ke root saat dijalankan (perilaku asli).

## 8. Verifikasi

Pohon pristine dan pohon baru dijalankan dengan harness yang sama (dari root repo, `D:/…` diemulasikan dengan symlink):

- **29 file test**: 18 lulus → 18 lulus; 11 gagal → 11 gagal dengan penyebab sama (8 karena `torch` tidak terpasang, 3 yang disebut di bagian 7). Ringkasan output identik, kecuali angka acak `test_uncertainty` yang berubah juga antar-run pohon pristine.
- **123 modul**: 69 bisa diimpor → 69; tidak ada perubahan status.
- `verify_commands`, `run_test_inventory`, `rppg_main.py --help`: output sama (selain entri path yang sengaja diperbarui).
- **Integritas file**: tiap file di zip asli dicocokkan lewat CRC → 292 identik, 14 diedit (hanya baris bootstrap/path), 29 MD terkonsolidasi (29/29 muncul verbatim), 0 hilang, 0 berubah tak terduga. `Dataset_rPPG-10/` dan `rppg_sessions.db` identik.

**Belum terverifikasi:** `pytest` tidak terpasang di lingkungan saya (tanpa jaringan), jadi `pytest.ini` belum dijalankan dan test berbasis pytest dijalankan lewat shim minimal. Test P5–P10 butuh `torch`; file-nya tidak berubah, tetapi tidak bisa dijalankan di sini. Mohon jalankan `pytest` sekali dari root di mesin Anda.

## 9. Tindak lanjut yang sengaja tidak dikerjakan

Mengubah modul datar (engine + `rppg_benchmark*`) menjadi paket (`benchmarks/`, `rppg/`) akan membuat root benar-benar ramping, tetapi menyentuh sekitar 40 baris import termasuk di `rppg_core.py`. Itu layak dikerjakan sebagai perubahan tersendiri, dengan skrip rewriting import dan harness verifikasi yang sama seperti di atas.
