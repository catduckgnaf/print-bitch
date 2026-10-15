# Print Buddy Internal Release Notes — Version 1.9.1

**Release Date:** 2026-10-15  
**Target Hardware:** FlashForge Adventurer 5X (AD5X / AD5M architecture) on ZMod Klipper + Moonraker (`192.168.250.51:7125`) with 4-slot IFS (Internal Filament System) multi-material feeder.

---

## 1. Hardware Boundary Analysis & Margin Tuning

### Mechanical & Stepper Analysis
- **Physical Build Plate:** FlashForge spring steel build sheet measures **235 x 235 mm**.
- **Klipper Stepper Limits (`printer.cfg`):**
  - **X Stepper:** `position_min: -20.0`, `position_max: 225.0`, `position_endstop: 220.0` (Total physical stroke: 245 mm).
  - **Y Stepper:** `position_min: -20.0`, `position_max: 232.0`, `position_endstop: 220.0` (Total physical stroke: 252 mm).
  - **Z Stepper:** `position_min: -10.0`, `position_max: 230.0`.
- **Slicer Bed Configuration:** Nominal printable area remains **220 x 220 mm** (origin `[0, 0]` to `[220, 220]`), preserving standard slicer profile compatibility.

### Margin Contracts
- **`color_geometry.py`**:
  - Centering bounding box margin reduced from `5.0 mm` to `1.0 mm`.
- **`orca_adapter.py`**:
  - `SINGLE_COPY_EDGE_MM`: Reduced from `3.0 mm` to `1.0 mm`.
  - `MULTI_COPY_EDGE_MM`: Reduced from `8.0 mm` to `3.0 mm`.
- **Empirical Validation**:
  - Strandbeest Plate 1 (legs), spanning 215.9 x 217.3 mm, previously threw `RuntimeError: part group does not fit the target bed without cropping` because centered width 217.3 mm exceeded `220 - 2 * 2.5 = 215 mm`.
  - Under the 1.0 mm margin, Plate 1 fits at 100% scale and sliced cleanly to G-code with actual extrusion/travel extents:
    - X: `[2.23, 217.76]` (span: 215.53 mm)
    - Y: `[1.53, 218.47]` (span: 216.94 mm)
  - Both extents remain safely within the 220x220 mm origin coordinates and well clear of the physical stepper travel limits (`-20.0` to `225.0` / `232.0`).

---

## 2. Multi-Plate Capacity Evaluation & Bounding Box Decoupling

### Problem Statement
- In prior versions, `orca_adapter.py:orca_plate_capacity` blindly returned `1` for any multi-plate 3MF file to avoid false negative zero-capacity reports.
- Meanwhile, `verified_scale_choices` evaluated model dimensions by extracting `source_triangles` across the entire 3MF file. In multi-plate Bambu/Orca projects, plates are placed side-by-side in global coordinate space. For the 4-plate Strandbeest, this produced a global bounding box of **501 x 529 mm**, causing `verified_scale_choices` to conclude the model required scaling to `<= 0.41`.

### Implementation Details
- **`_multi_plate_capacity(source, state, scale, single_margin)`**:
  - Inspects `plate_manifest(source)` to extract individual plate object assignments.
  - Uses `color_geometry._world_bounds(archive, object_ids)` to compute the bounding box of each plate independently.
  - Compares each plate's scaled dimensions `(dx, dy, dz)` against usable bed boundaries (`eff_w = bed[0] - 2 * margin`, `eff_d = bed[1] - 2 * margin`, `max_h`).
  - Supports 90-degree bed rotation (`fits = (dx <= eff_w and dy <= eff_d) or (dy <= eff_w and dx <= eff_d)`).
  - Returns `0` if any plate exceeds usable dimensions; returns `1` only if all plates fit.
- **`verified_scale_choices(source, state)`**:
  - Multi-plate 3MF files bypass whole-canvas `source_triangles` extraction.
  - If capacity at 1.0 is `> 0`, returns `[1.0]`.
  - If capacity at 0.5 is `< 1`, returns `[]`.
  - Runs an integer binary search `low, high = 50, 99` over `orca_plate_capacity(..., scale=middle / 100.0)` to find the maximal scale where all plates fit.
  - Returns `_scale_ladder(best_scale)` (for Strandbeest, Plate 3 circular fan at 231 mm yields best scale `0.94`, returning `[0.94, 0.75, 0.5]`).

---

## 3. Multi-Plate Slicing Isolation & Per-Part Grouping Fix

### Problem Statement
1. In `model_job.py:1668`, `_slice_per_plate` contained:
   ```python
   if fit is not None:
       object_plate = {key: 1 for key in object_plate}
   ```
   If a scale factor was passed to a multi-plate model, all parts across all plates were reassigned to Plate 1 and sliced together onto a single plate.
2. In `model_job.py:per_part_fit_options`, parts were grouped strictly by filament slot:
   ```python
   groups.setdefault(slot, []).append(part['key'])
   ```
   For multi-plate models where multiple parts on different plates share slot 3, this attempted to fit all parts from all plates simultaneously onto one bed during fit testing, triggering `RuntimeError` and yielding empty fit options `{'scales': [], 'rotations': []}`.

### Implementation Details
- **`_slice_per_plate`**:
  - Guard updated to `if fit is not None and len(plates) <= 1:`, preserving plate boundaries when scaling multi-plate projects.
  - Added support for per-plate scale overrides via `job.get('plate_scales')`, enabling individual plates to scale independently (e.g. Plate 3 fan at 94%, Plates 1, 2, 4 at 100%).
- **`per_part_fit_options`**:
  - Updated grouping to use `(plate_id, slot)` tuples:
    ```python
    p_id = object_plate.get(str(part['object_id']), 1) if plates else 1
    slot = view['choices']['part:' + part['key']]['slot']
    groups.setdefault((p_id, slot) if plates else slot, []).append(part['key'])
    ```
  - Fit choices `[0.94, 0.75, 0.5]` now correctly evaluate to `honored: True` across all plates.

---

## 4. Conversational Continuity & Link Recovery

### Problem Statement
- When the bot recommended a model and the user replied affirmatively ("Let's do it", "Print it", "Go ahead"), the gateway link dispatcher did not find a URL in `event.text`, skipped the intake pipeline, fell through to LLM chat, and prompted the user to send the link again ("Send a new link to try again").

### Implementation Details
- **`plugins/print-feedback/__init__.py`**:
  - Added `_is_affirmative_followup(text)` matching affirmative intent patterns (`let's do it`, `lets print that`, `go ahead`, `do it`, `start printing`, `yes please print`, `sounds good`, `yep`).
  - Added `_recent_model_link_from_db()`: Queries the 25 most recent messages in `state.db` for MakerWorld or Printables URLs.
  - If affirmative intent is detected without a link, prepends the retrieved URL to `event.text`, automatically triggering the full fresh model intake pipeline.
- **Intake Cleanup**:
  - Removed `"Send a new link to try again."` from `link_intake.py`, `prepared_intake.py`, and `plugins/print-feedback/__init__.py`.

---

## 5. Test Suite Verification

- **Repository Unit Tests (`tests/`):**
  - `python3 -m unittest discover -s tests -v`: 13/13 passed.
- **Scripts & Integration Test Suite (`scripts/`):**
  - `test_orca_adapter.py`, `test_model_job.py`, `test_prepared_intake.py`: 171 passed, 41 subtests passed.
  - `test_plate_merge.py`, `test_source_colors.py`, `test_color_geometry.py`: 42 passed.
  - Total: 213 unit/integration tests passed with 0 regressions.
- **Full Slice Verification:**
  - Strandbeest 4-plate project with scale `0.94` sliced end-to-end via `slice_job`, producing 4 valid G-code plates (Plate 1: 2h 22m, Plate 2: 2h 11m, Plate 3: 1h 14m, Plate 4: 1h 37m).
