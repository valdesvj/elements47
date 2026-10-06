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

## Oct 6, 2026 - The full table

- 118 cells in an 18 x 9 grid: rows 1-7 the periods, 8 lanthanides (La-Lu), 9 actinides (Ac-Lr), columns 3-17
  (group 3 of periods 6 and 7 left empty). Cells 23 x 26 sharing their edges (pitch 22 x 25): column c from
  x = 22c - 21, period r bottom row 238 - 25r; rows 8-9 9 rows lower (a gap under period 7). The table uses
  x 1-397, rows 4-238 (row 0 = bottom).
- Drawn in the order of Z by segments (python/elements.py SEGMENTS, LBL 29: count, row, first column); each
  cell fills the matrix PT (STOIJ / STOEL), so the cursor finds its neighbours with RCLEL (0 = empty, go on
  in the same direction; outside the table: stay).
- Number: tinyFont, written as " " + αIP (a leading space instead of an empty string, 4 columns to the left).
  Symbol: GRFNT 21, centred: the symbol pieces (LBL 36-41, 20 elements of 3 characters) hold a digit, the
  column of the symbol in its cell (build_elem47.offset, from the glyph widths), then the 2 characters.
  The symbols are read in order: α→𝑥 for the digit, αLEFT 2 for the symbol, αSL 2 to move on.
- Data for the panel and the detail box (LBL 30): labels 60-99 "mass name/mass name/mass name"; αPOS "/" and
  αSL skip to the element, αLEFT cuts at the next "/", then αPOS " " splits mass and name. Group = column
  ("-" for rows 8-9), period = row (rows 8-9: 6-7), block from the column (He: s).
- Keys (Victor): 8 4 6 2 move, 5 the detail box, 0 the end; other keys ignored (as NAV's menu).
- The panel (x 47-263, rows 166-228) in the empty part of periods 1-3: name, Z, mass, the keys; cleared with
  GRMOD 2 (one 63-row word) before each update. Title in row 1, columns 13-17.
- c47sim: αLEFT and αPOS added (from the C47 index text: αLEFT drops X; αPOS from 0, -1 not found, X
  replaced). To be checked on the calculator, with α→𝑥 on a register and αSL with X = 0.
- Two label clashes found in the simulator (data labels over the key handlers, then over the move
  routine): build_elem47.py now stops on a label used twice.
- Simulator steps: table 19 700, a move about 1 050, detail box 3 900; closing the box draws the whole table
  again. Text literals up to 60 characters (Almanac 47 uses up to 69 on the C47).

## Oct 6, 2026 - Key legend, IUPAC masses, group names, CR texts

- Key legend (Victor): the digit cross (8 above, 4 6, 2 below, 5 left of 4, 0 under 2) and beside it the
  same places as INFO, arrows and END, in the tinyFont (monospaced: 6 columns for digits, letters, arrows
  and the space), one ATEXT per cross with CR (U+21B5) between the lines (8-row lines). Drawn once
  (LBL 05); the panel now clears only the name (x 47-263, rows 209-228) and Z / mass (x 47-147).
- Masses: CIAAW Abridged Standard Atomic Weights 2024 (the values of the IUPAC periodic table): H 1.0080,
  Zr 91.222; the 34 elements without a standard atomic weight show "-" (no mass numbers in brackets).
- Detail box x 50-349: labels in one ATEXT ("Symbol↵Mass↵Group↵Period"), the values built in R44 with
  x→α (texts) and αIP (numbers) and drawn with one ATEXT: symbol, mass, group number + group name, period
  and block. Group names (LBL 58, one text of 3 pieces of 64 characters at most, joined with x→α):
  Nonmetal (H), Alkali metals, Alkaline earth metals, Transition metals, Boron group, Carbon group,
  Pnictogens, Chalcogens, Halogens, Noble gases, Lanthanides, Actinides; chosen from the cell (LBL 47),
  no data per element. LBL 31 = field k of a "/" text, used for the element data and the group names.
- CR texts cut the detail box from 16 ATEXT (with their coordinates) to 2. The element data did not grow.

## Oct 6, 2026 - Detail box: symbol, mass, group

- Period and block removed (Victor): the box shows symbol, mass, group number and name (3 CR lines,
  from row 126). LBL 48 and 53-57 gone: 853 steps, 88 local labels.

## Next
- Run on the C47 (rejig, then XEQ "ELEM47"); time the table (TICKS) and compare with docs/ELEM47_*.png.
- Closing the detail box: redraw only the cells under it instead of the whole table.
- More data in the detail box (category, electronegativity, state); Free42 port (AGRAPH fonts, no ATEXT).
