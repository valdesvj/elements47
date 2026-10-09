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
- Drawn in the order of Z by segments (python/elements.py SEGMENTS, written into LBL :CELLS:: count, row, first column); each
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

## Oct 6, 2026 - State, boiling point, configuration; the data in ELD1 / ELD2

- Detail box (Victor): Symbol | Mass, State | Boil, Group number and name, Config. Two columns, each one
  ATEXT of labels and one of values (CR lines): left "Symbol↵State↵Group↵Config" at x 58, values at 130;
  right "Mass↵Boil" at 226, values at 272. Og's configuration ends at x 293.
- Data from the PubChem periodic table CSV (Victor): StandardState ("Expected to be ..." -> "-"),
  BoilingPoint in K (one decimal below 100 K), ElectronConfiguration in noble-gas notation with the
  subshells sorted in shell order ([Ar] 3d6 4s2, as Victor asked; PubChem writes the filling order) and
  "(predicted)" dropped. Masses stay IUPAC (CIAAW 2024).
- One label per element now (a record of up to 51 characters), so the data left ELEM47: ELD1 (Z 1-60) and
  ELD2 (Z 61-118), each with its own 100 local labels and one global label, in the same file as ELEM47.
  LBL 30 calls XEQ "ELD1" / "ELD2" and splits the record with LBL 62 / 31. ELEM47 is down to 51 labels.
- elem47sim.split: one simulator file per program (numeric labels local, as on the C47).

## Oct 6, 2026 - Branch optimize (docs/OPTIMIZATIONS.md)

- Same screens as prototype-h pixel for pixel (tests/test_opt.py); steps run: table 20 210 -> 9 307, a move
  1 540 -> 233, the detail box 5 009 -> 2 119. File about 8 480 -> 7 980 bytes (estimated).
- Unrolled cell boxes and cursor, the position once per segment, DSE counter for the symbol pieces, no idle
  CLSTK / DROP, GRMOD / GRFNT from X; the panel and the inside of the detail box cleared by ATEXT in GRMOD 1
  (spaces); records "name/mass/state letter/boiling point/configuration"; registers renumbered R20-R51 and
  saved with LocR 32 / given back at the end (as Almanac 47 v2). No outlining: nothing repeats enough.
- tools/build_elem47.py prints the estimated .p47 size of each program.

## Oct 7, 2026 - One global label, local named labels (branch local-labels, from optimize)

- The C47 has local named labels (LBL + the label menu, shown as :NAME:, at most 7 characters), besides
  the numeric 00-99 and the letters. Local labels are searched forwards from the GTO / XEQ, before the
  global ones. So ELEM47 now shows one name only: LBL "ELEM47"; ELD1 and ELD2 are gone.
- programs_rem/ELEM47.txt writes the code labels by name (LBL :PANEL:, XEQ :DETAIL:, 46 of them).
  tools/build_elem47.py gives each a free local number (LABELS = 'numeric'), stops on a name defined twice
  or used and not defined, and writes listings/ELEM47_labels.txt (name, number, job). The calculator file
  keeps numeric labels until rejig's text form of a local named label is known (key one in on the C47,
  export the program, look at the text); then NAMED and LABELS = 'named' in the build tool. Also to check
  then: whether the forward search wraps to the start of the program (as the HP-42S does), since
  :KEYS:, :SEGLOOP:, :STEPLP: and the others are reached by GTO backwards.
- The data labels stay numeric: they are reached with XEQ IND. The element records are 3 per label
  (LBL 60-99, up to 126 characters); :RECORD: skips (Z-1) mod 3 records of 5 fields. The symbols are
  65 elements per label (LBL 36-37, 195 characters). Texts up to 196 characters, the firmware limit for
  one string (MAX_NUMBER_OF_GLYPHS_IN_STRING), as in branch detail-redraw: tests/calc/LTEST.txt checks it
  on the C47 (XEQ "LTEST" returns 196); only 69 had been checked there. 89 local numbers used of 100.
- From branch detail-redraw: closing the detail box draws only what the box covered (:CLOSE:): the cursor
  off, the box area cleared (:BOXCLR:, the clearing part of :DETAIL:), the cells of rows 3-7, columns 3-16
  again from PT (:CELLZ: finds the symbol of any Z, :CELL: is the cell drawing shared with the table), then
  the key legend, the cursor and the panel (the box covers part of both). Simulator steps: closing about
  9 400 -> 6 100; the table 9 427 -> 9 633 (+2 %, the XEQ :CELL:). Its other changes (category and
  electronegativity in the box) were made before the box got state, boiling point and configuration
  (branch prototype-h), so they are not taken.
- tests/test_opt.py now compares with branch optimize (prototype-h no longer matches since c47sim stores
  the αLEFT result as the firmware does): every screen the same, pixel for pixel; tests/test_elem47.py all ok.

## Oct 7, 2026 - Local named labels in the calculator file

- Victor keyed in a test program on the C47 (LBL "T", GTO :B:, LBL :A:, RTN, LBL :B:, GTO :A:) and sent its
  .p47 bytes: a global label is 1 253 len name, a local named label 1 249 len name (LBL) and 2 249 len name
  (GTO); RTN 4, END 133 178. rejig reads LBL :NAME: as a local named label since 0.30.0 (its ChangeLog:
  colons always significant; :A:-:L: need the colons to differ from the letter labels A-L).
- build/ELEM47.txt now has the local named labels as they are; build/ELEM47_num.txt is the same program
  with numeric local labels (the fallback, if the C47 or an older rejig refuses the named ones).
  Tests: both give the same screens; test_opt runs the named one.
- Cost: a named label takes 3 + its length bytes at each LBL / GTO / XEQ (a numeric one 2): about 8.5 KB
  instead of 7.8 KB (estimate). Speed of the search by name on the C47: to be timed.
- Still to check on the C47: XEQ "T" runs to the RTN without an error = GTO :A: finds a label before it
  (the search wraps to the start of the program). ELEM47 needs that (:KEYS:, :SEGLOOP:, :STEPLP: ...).

## Oct 7, 2026 - Checked in the firmware sources (~/opt/c43 master)

- The local label search wraps: manage.c findNamedLabelWithDuplicate takes the first matching label after
  the current step, else the first one in the program. So GTO :KEYS:, :SEGLOOP:, :STEPLP: backwards work;
  XEQ "T" on the C47 only confirms it.
- The string limit is 508 glyphs (defines.h MAX_NUMBER_OF_GLYPHS_IN_STRING, since January 2024; 196 was
  the WP43 value). But a 508-character text in a program does not come through in T47 (next section):
  the data stays at 196 characters per text.
- Closing the detail box, checked in the simulator over the whole table (190 open / close, every row
  both ways): the screen after closing is the screen before opening, pixel for pixel.

## Oct 7, 2026 - ELEM47 in the C47 firmware (T47)

- T47 is the PC simulator built from the firmware sources with a Tcl script mode. Built from a copy of
  ~/opt/c43 (master ef39ddb6c, 6 Oct 2026), never in ~/opt/c43 itself:
  `rsync -a --exclude=.git --exclude='build.*' --exclude=t47bench ~/opt/c43/ ~/.cache/c47fw/`, then
  `cd ~/.cache/c47fw && make simc47 t47` (about 10 minutes) gives ~/.cache/c47fw/t47.
- tests/test_fw.py runs a test copy of build/ELEM47.txt there (rejig for the .p47): each key wait becomes
  PAUSE 1, SNAP and the next key from the text TKS (α→x). The firmware shows what a program drew only at a
  PAUSE: a SNAP right after the drawing still has the screen before it.
- Results: XEQ "T" (GTO :A: backwards) gives 42, so the search wraps; LTEST gives 196; a 508-character text
  in a program does not come through (the register gets a garbled text of about 196), so the data stays
  at 196 characters per text. The whole table both ways, 190 detail boxes opened and closed: every screen
  the same as python/c47sim.py pixel for pixel, the table back each time; ELEM47_num the same; R00-R99 kept.

## Oct 7, 2026 - The records 4 per label

- With 196 characters confirmed in the firmware, the element records go 4 per label (LBL 60-89, 172
  characters at most; 5 per label would be 210): 1 036 -> 1 006 steps, 90 -> 80 labels. :RECORD: divides
  by 4 (the build stops if it does not match PER). The screens are the same (test_opt, test_fw); a cursor
  move runs 1-2 % more steps (on average 7.5 fields skipped in place of 5).
- Branch detail-redraw packed 8 elements in 175 characters, but its records had less in them (no state,
  boiling point or configuration then); with today's five fields 4 is the most.

## Oct 7, 2026 - The development programs apart: programs_rem/dev, build/dev

- ELEM47P (branch prototype-cells: the table from a vector of x + iy, one subroutine per job, RESTORE
  draws again only the cells under the info box) is kept as a development program:
  programs_rem/dev/ELEM47P.txt, built by tools/build_dev.py into build/dev/ and listings/dev/ (the release
  files of tools/build_elem47.py are not touched). Its data programs ELP1 and ELP2 are written from
  python/elements.py. 902 steps (ELEM47P 414, ELP1 247, ELP2 241); global labels ELEM47P, ELP1, ELP2.
- build/dev/dev_test/ELEM47_H.txt: prototype 1 (the H cell), kept for reference.
- tests/test_dev.py: ELEM47P (moves, the info box closed three times: the table back each time) and
  prototype 1, in c47sim and in T47, the same screens.

## Oct 7, 2026 - Free42 (DM42 / DM42n stock firmware)

- tools/build_free42.py converts programs_rem/ELEM47.txt step by step into build/free42/ELEM47.txt, the
  way Almanac 47 converts NAV: 3 STO "GrMod" (the 400 x 240 screen), AGRAPH as ALPHA columns of 8 pixels
  (bit 0 at the top, row 1 at the top: C47 row r = Free42 row 240 - r), GRMOD as flags 34 / 35, GETKEY
  for the key waits, REGS saved and given back for LocR (the SIZE too), XSTR for the texts.
- ATEXT: E47T (GRFNT 21) and E47S (GRFNT 10) draw the C47 fonts, one local label per character (the
  Free42 code - 32), the glyph box in bands of 8 rows (20 rows: 0, 8, 12), written exactly in GRMOD 1
  (as the C47 clears each character's box), |X| and |Y| as the C47. The glyphs come from c47sim.
- What Free42 needed: a string in a program holds 15 characters, 14 after the append marker, and may
  not start with a byte >= 128 (the append marker): the ALPHA literals are cut in pieces. The CR glyph
  breaks a pasted line: it is written €0d. N→S follows the display format: αIP is CLA AIP ASTO ST X.
  Free42 Paste leaves out the commands it does not know, without a message: tests/test_f42.py pastes
  every different command and lists it back.
- tests/test_f42.py (f42run, the Free42 3.3 core of Almanac 47): the whole table both ways with the box
  at each cell, 571 screens, every one the same as the C47 pixel for pixel; R00-R99 and SIZE kept.
- Sizes (estimated): ELEM47 1 094 steps, E47T 1 855 (the font, 9.7 KB), E47S 329. The speed on the DM42
  is not known yet (f42run counts no steps): to be timed there.

## Oct 7, 2026 - v1.0.0: registers cleared at the end, Free42 as one program

- Victor's choice for the release: ELEM47 works in the global registers R20-R51 and clears the registers
  and the stack at the end (CLREGS, CLSTK), as Almanac 47 v2.2.0; the LocR copy of R20-R51 is gone
  (1 006 -> 878 steps). Local registers for the work itself are not possible: in the firmware every XEQ
  level starts without local registers (lblGtoXeq.c fnExecute), so the subroutines could not reach the
  caller's, and KEY? takes no local register (input.c fnKey).
- python/c47sim.py has no CLREGS yet (Almanac 47's copy has it in the working tree, uncommitted):
  python/elem47sim.py runs it as 0 STO 00 ... STO 99. T47 (tests/test_fw.py) checks the real one.
- Free42: one program, one global label. The fonts are data now: per font an index text (the Free42 codes)
  and a table text (box width, advance, the bands of 8 rows), put in R69-R72 by :FDATA: at the start; a
  character is POS in the index, SUBSTR of its record, then per band CLA, ARCL, AGRAPH. The text and box
  routines use R60-R89 (SIZE 90), cleared by CLRG at the end. 3 programs of 3 278 steps -> 1 program of
  1 447 steps, 93 local labels. XSTR keeps every byte (checked 0-255) except the paste aliases: <= becomes
  one character, so the pieces are cut after < > - ! | \ as for ALPHA.

## Oct 7, 2026 - Global labels again: ELEM47 + ELD1 + ELD2 (C47 and Free42)

- Victor: the one-program builds were slow (the labels far from the code that calls them) and the local
  named labels did not work well; the compact build is not released. Back to separate programs with
  global labels, on both calculators:
- C47: ELEM47 the code (795 steps), ELD1 the records of Z 1-60 (LBL 60-74), ELD2 Z 61-118 (LBL 75-89);
  :RECORD: puts the label in R43 and calls XEQ "ELD1" or "ELD2" (each starts XEQ IND 43, RTN). The code
  labels keep their names in programs_rem; build/ELEM47.txt has numeric local labels only (no _num file).
- Free42: ELEM47, ELD1, ELD2 as on the C47; the fonts back as programs, one local label per character
  (XEQ IND from the text loop, as in the first port): E47T (GRFNT 21, with E47B the boxes) and E47S
  (GRFNT 10). Their work registers are R60-R75 (no named variables left behind), SIZE 76; CLRG, CLST at
  the end as before.

## Oct 7, 2026 - Speed: fewer steps, the calling routines first

- Measured in the firmware (tools/bench_fw.py: T47's CPU instructions with perf, the start of T47 taken
  off) and profiled (perf record): a step costs about 11 000 instructions whatever it does (the
  interpreter, the stack and register copies, the memory blocks), AGRAPH and ATEXT themselves under 10 %.
  So the steps run count, and one more thing: at every RTN the firmware finds the step after the XEQ again
  by counting the steps from the start of the program (lblGtoXeq.c fnReturn -> nextStep.c
  defineCurrentStep), about 190 instructions per step counted. An XEQ at step 600 costs about 10 steps
  more on its return than one at step 10. A local GTO / XEQ goes straight to the label (labelList).
- The routines that call others on a move or a detail box are now at the start of ELEM47 (LBL "ELEM47",
  GTO :INIT:, then :MOVE:, :CURSOR:, :PANEL:, :RECORD:, :INFO:, :CLOSE:, :CLSEG:, :DETAIL:); the code run
  once and the routines that call nothing come after. Steps counted at RTNs: a move 3 180 -> 430, a box
  opened and closed 69 600 -> 11 500.
- The cell (118 in the table, 58 again when the box closes): drawn inside the segment loop (no XEQ),
  22 columns each (the right edge is the next cell's left edge; the last one after the segment), the rows
  of the number and the symbol computed once per segment (R52, R53 in :CELLPOS:), the symbol "Fe3" (the
  digit after it) taken with αLEFT and α→x straight from the piece, PT filled by STOSEQ after one STOIJ
  per segment: 51 + 17 steps -> 57 steps per cell (with the loop).
- Closing the box: the 5 segments under it (rows 3-7, columns 3-16, :CLSEG: finds the symbols of the
  first Z) through the table's segment loop, instead of 70 cells by PT with the symbol found per cell.
- The bottom line and the header bar of the box (298 columns each): one routine :HLINE:, 4 + 21 x 14
  AGRAPH unrolled, 340 steps instead of 894 each.
- The records end with "|": skipping a record is one αPOS, not five; the configuration is cut at "|".
- The cursor off uses the position of the last cursor drawn (:CURSXOR:, no :CELLPOS:); FBLOCK is inline.
- The same screens pixel for pixel: tests/test_opt.py (simulator), tests/test_fw.py (T47),
  tests/test_f42.py (Free42). ELEM47 795 -> 805 steps (Free42 1 008 -> 1 004).

| | simulator steps before | after | firmware instructions before | after |
|---|---|---|---|---|
| the table | 9 573 | 7 897 (-18 %) | 120 M | 101 M (-16 %) |
| a cursor move | 315 | 245 (-22 %) | 3.75 M | 2.71 M (-28 %) |
| the detail box | 2 185 | 1 039 (-52 %) | | |
| closing it | 6 079 | 4 065 (-33 %) | | |
| box opened and closed | | | 121 M | 72 M (-41 %) |

- Then (branch segments-detail): the segment list is in the code, at the end of LBL :CELLS: (the build writes
  it after the line "REM ==== SEGMENTS"; no LBL 29 at the end of ELEM47), and :CELLS: sits right after the
  routines of a move and of the box, so each RTN of :SEGMENT: counts 353-405 steps instead of 745-797. R54 the
  column of the number (once per segment, then STO+ 54 with the 22 of R39): 1 step less per cell.
  ELEM47 805 steps (the same). Simulator: the table 7 897 -> 7 833 steps. Firmware (tools/bench_fw.py):
  the table 101.3 -> 98.3 M (-3 %), moves - table 124.9 -> 124.8 M, boxes - table 429.9 -> 426.4 M (-0.8 %).

- Then (branch box-moves): with the detail box open the arrows move the cursor and show the box of the new
  element (LBL :MOVE: then LBL :DETREC:, the record the panel has just read); 5 closes the box (R36 = 1 while
  it is open; one key loop, :INFOKEY: gone), other keys are ignored, 0 still ends. The box reads its data
  first and draws after (BOXCLR and the header in R55, the left values stay in R38), so a move shows no
  empty box. The hint "5: BACK" (x 304, ends where "ANY KEY: BACK" ended). The panel and the cursor follow
  in the table too (the cursor may be under the box: the box is drawn over it, :CLOSE: turns it off as before).
  tests/test_opt.py: the reference closed the box with any key (the key after 5 becomes 5 for this build),
  the hint area left out of the box screens. Firmware (tools/bench_fw.py): table 98.3 -> 99.4 M, moves -
  table 124.8 -> 127.9 M (2 more steps per move: RCL 36, X≠0?), boxes - table 426.4 -> 427.7 M; inbox (the
  46 moves of 'moves' with the box open) 801.8 M - table = 702 M, about 14 M a move (a plain move 2.7 M).
  ELEM47 816 steps.

- Free42 as the C47: the screen shows only when ELEM47 waits for a key (Almanac 47's RLCD build).
  tools/build_free42.py: 0 STO "RefLCD" at the start, -1 STO "RefLCD" before each GETKEY (one refresh),
  7 STO "RefLCD" at the end. tests/test_f42.py takes what the LCD shows (f42run lcd, RefLCD modelled), not
  the drawing buffer, and films the table being drawn (a capture every 1024 steps): 40 captures, all the
  screen before it, then the whole table (main's build: 40 different screens, the table building up).
  Free42 ELEM47 1 022 steps. Free42 on a PC or phone has no RefLCD (and draws only 131 x 16).

## Oct 8, 2026 - Branch compact (experimental): labels from 00
- The symbols are LBL 00-01 in ELEM47 and the named labels follow, 02-50, no gaps; the records are
  LBL 00-14 in ELD1 (Z 1-60) and 15-29 in ELD2 (Z 61-118) (tools/build_elem47.py: only ELEM47's own numeric
  labels are taken, the other programs have their own).
- With the data labels from 0, no offset: "36 +" (symbols, twice) and "60 +" (records) are gone, :CELLS:
  starts R50 at -1 (was 35), the split compares with 14 (was 74). ELEM47 810 steps (816); Free42 1 016
  steps (1 022). The screens are the same (tests/test_opt.py).
- Tried and dropped: the record programs named "A" and "B" (they worked in T47 and f42run; the names
  ELD1 / ELD2 kept).

## Oct 9, 2026 - Branch local-registers (a dev build, the release stays)
- The release does not save the globals: it works in R20-R55, keeps the key in R33, and CLREGS at key 0.
  This branch does not change programs_rem/ELEM47.txt or build/ELEM47.txt. tools/build_locr.py reads that
  source and writes build/dev/locr/ (ELEM47.txt, VERSION.txt, ELEM47.p47) and listings/dev/locr/.
  The .p47 is gitignored, same as the others.
- The working registers are local, R.00-R.35, one LocR 48 at LBL "ELEM47". An XEQ starts a level with no
  local registers (and KEY? takes no local), so an internal XEQ is a same-level call: ISG stores the return
  label in R90-R97 and GTO enters the routine; its RTN is GTO 99, which DSE-pops the label. The label number
  sits in X for a moment, so T is parked in R.47 and put back (LBL :CLSEG: reads T, the first Z of a segment).
  The key, and the label ELD1/ELD2 execute, is the global R00. Key 0 copies R00 and R90-R97 back. No CLREGS.
  EXIT or R/S does not run that copy. WSIZE 64 is still left as the release leaves it.
- Inlined, one call and one block: :CLOSE:, :CELLS:, :SYMPCE:, :KELVIN:, :STATES:, :GRPNAME:. :FIELDK: counts
  down with DSE. 47 internal calls, deepest 3, return sequence LBL 99, 5 local labels free.
  ELEM47 1 377 steps (the release is 810), ELD1 49, ELD2 49.
- The screens are the release's, pixel for pixel (tests/test_locr.py: the tour, the gaps, the f-block, the
  edges, other keys, closing the box, moves inside the box), in c47sim and in T47 for the close and the
  inbox sequences. R00-R99 seeded before the run are back at key 0, and the stack is clear.
  python/c47sim.py and python/elem47sim.py are the same as main.
- It is slower. Each internal call is several steps instead of XEQ and RTN. Simulator steps, release then
  this build: the table 7 833 -> 8 526 (+693), a move 243 -> 399, the detail box 1 038 -> 1 259, closing it
  4 029 -> 4 391. A whole tour 27 412 -> 35 512.

## Next
- On the C47: time the table (TICKS); the screens are checked in T47 (tests/test_fw.py).
- More data in the detail box (category, electronegativity, state).
- Free42: time the table on a DM42; build/free42/ELEM47.txt goes in by Paste in Free42 (export a .raw there).
