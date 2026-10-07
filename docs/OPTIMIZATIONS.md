# Elements 47 — the optimizations (branch `optimize`)

What changed under the hood against branch `prototype-h`. Every change keeps the screens the same: each
screen is compared pixel for pixel with the `prototype-h` build (`tests/test_opt.py`, as Almanac 47's
`test_v2.py`).

| | prototype-h | optimize |
|---|---|---|
| Program file (ELEM47 + ELD1 + ELD2) | 1 142 steps, about 8 480 bytes | 1 198 steps, about 7 980 bytes (−6 %) |
| ELEM47 alone | 774 steps, about 2 970 bytes | 830 steps, about 3 070 bytes (with the register save, +152 steps) |
| Element data (ELD1 + ELD2) | 4 694 characters | 4 092 characters (−13 %) |
| Steps run: drawing the table | 20 210 | 9 307 (−54 %) |
| Steps run: one cursor move | 1 540 | 233 (−85 %) |
| Steps run: the detail box | 5 009 | 2 119 (−58 %) |
| Your numbered registers | R20–R54 overwritten | R20–R51 used, saved and given back |

Bytes are estimated by `tools/build_elem47.py` (calibrated on Almanac 47's MOON47 and NAVFULL, within 1.5 %);
rejig gives the real size. Steps are counted in the C47 simulator; the time on the calculator decides.

## 1. The table

* **Unrolled cell boxes.** A cell's frame was a loop of `AGRAPH`, `DSE`, `GTO` over 23 columns (3 steps per
  column, 7 670 steps for the table). Now 23 `AGRAPH` steps in a row: the column moves by itself (AGRAPH adds 1
  to X).
* **The position once per segment.** The column and row of a cell were computed for every cell (18 steps);
  now once per segment of the table, then `22 STO+` for the next cell.
* **The symbol pieces on a DSE counter.** `(Z−1) mod 20 = 0?` before each cell (7 steps) became `DSE`, `GTO`
  (2 steps); the piece label counts up in a register (`STO+`, `XEQ IND`).
* **No idle stack work.** `CLSTK` after each `ATEXT`, `DROP` after `GRFNT`: gone where nothing reads the
  stack afterwards (`ATEXT Z` takes X, Y, Z only). `GRMOD` and `GRFNT` take X directly: rejig writes
  `GRMOD r` as `GRMOD` and the number r anyway (found in Almanac 47), so `3 GRMOD` instead of
  `3 STO r GRMOD r`.

## 2. The panel and the cursor

* **The panel clears itself.** It was cleared with two `AGRAPH` loops (217 and 101 columns, 990 steps per
  move). Now the name, Z and mass are written with `GRMOD 1` (each character clears its glyph box first) and
  followed by spaces that cover the longest text before: name + 13 spaces, Z + 2, mass + 5. Z is written
  without the leading space now (`αSL 1` after `αIP`), so its glyph boxes never touch the cells of column 2.
* **Only what the panel shows.** The record is read field by field (`LBL 32` takes the next field and keeps
  the rest), so the panel stops after the name and the mass; the detail box reads the other three.
* **The cursor unrolled**: 21 `AGRAPH` steps in XOR mode, no loop.

## 3. The detail box

* **Cleared by one ATEXT.** The inside (298 × 120 pixels) was cleared by two `AGRAPH` passes of 298 columns
  each. Now one `ATEXT` in `GRMOD 1` of 6 lines of 42 spaces (7 columns × 20 rows each, from x 50), and one of
  6 single spaces at x 343 for the last columns.
* **The top line comes with the header bar.** The XOR pass of the header covers rows 158–179: the cleared
  row 179 turns black, as the top line before. The sides are 4 `AGRAPH` steps; only the bottom line is a loop.

## 4. The data

* **Records `name/mass/state/boiling point/configuration`**, the state as one letter (S L G −, expanded with
  `αPOS` in "SLG-" and the field of "Solid/Liquid/Gas/-") and the boiling point without " K" (added by the
  program unless it is "-"): 602 characters less.

## 5. The registers

* **Renumbered** (the registers the program really uses, in one block): R20–R51.
* **Your registers are kept.** At the start ELEM47 does `LocR 32` and copies R20–R51 into its local registers
  (`RCL 20`, `STO R.00`, …); key 0 copies them back, as Almanac 47 v2. `KEY?` keeps a global register (it refuses
  a local one). If ELEM47 is interrupted (EXIT, R/S, an error) the copy back does not run.

## 6. Not done

* **Outlining** (repeated runs of steps as subroutines, Almanac 47's `outline`): no run of 3 or more steps
  repeats often enough in ELEM47 to save a step; the unrolled boxes are kept for speed.
* **ISG loops:** the remaining loops (the bottom line and the header bar of the detail box) already use
  `DSE` with 2 steps per pass.

## 7. To check on the calculator

* `ATEXT` in `GRMOD 1` clearing the glyph box of a space (the panel and the inside of the detail box).
* `LocR`, `RCL r` / `STO R.nn` at the start and the copy back at the end.
* `αPOS`, `αLEFT`, `αSL` (with X = 0), `α→𝑥` on a register, as before.

## 8. How it was tested

* `tests/test_opt.py`: five key sequences (a tour of the table, the gaps, the f-block, the edges, other keys):
  every screen the same as `prototype-h`; the panel and the detail box of all 118 elements the same; GRFNT,
  GRMOD and the matrix PT after the end; your R00–R99 the same before and after.
* `tests/test_elem47.py`: every cell, the matrix PT, the detail box data of all 118 elements, the cursor moves.
