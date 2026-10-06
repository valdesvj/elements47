# Elements 47 - development notes

## Oct 6, 2026 - Prototype 1: Hydrogen

- One program, ELEM47 (programs_rem/ELEM47.txt). The table has only the H cell, drawn where it will be in the
  full 18 x 9 grid: 22 x 26 pixels at x 2-23, rows 212-237 (row 0 = bottom). Atomic number in the tinyFont
  (GRFNT 10), symbol in GRFNT 21, title ELEMENTS 47 and a key hint.
- + (keycode 85) draws the detail box over the table, centred: x 80-319, rows 60-179. The inside is cleared
  first (GRMOD 2, AGRAPH full columns), then the frame (GRMOD 0), the text (ATEXT, two columns of label and
  value), and the header bar inverted with GRMOD 3. The key hint changes to ANY KEY: BACK (ATEXT with
  GRMOD 1, spaces to clear the old hint). Any key redraws the table; on the table any other key ends.
- Boxes: LBL 50 draws columns with AGRAPH (X = column, moved by AGRAPH; Y = bottom row), R21 the edge column
  pattern, R22 the inner pattern, R20 inner columns. 64-bit words (WSIZE 64), so the 120-row box is two
  halves of 60 rows.
- Key waits as Almanac 47: LBL n / PAUSE 50 / KEY? 39 / GTO n.
- The data of H is in the program as text (prototype only). For 118 elements: a packed table (see README).
- Checked in python/c47sim.py (tests/test_elem47.py); not yet run on the C47.

## Next
- Run on the C47 (rejig, then XEQ "ELEM47"); compare with docs/ELEM47_*.png.
- Grid of 118 cells, cursor with the arrows (XOR), data table for all elements.
