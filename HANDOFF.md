# Elements 47: handoff for the next session (Oct 11, 2026)

Read CLAUDE.md and DEVELOPMENT_NOTES.md first (sections from "Branch struct" on). Everything below is on main.
The Almanac 47 handoff (STRUCT branch there) is docs/ALMANAC47_STRUCT_HANDOFF.md.

## State of main (5963a52 + b5efff0)
- C47 only, STRUCT style (firmware app note AN0007: IF/ELSE/ENDIF, DO/WHILE/ENDDO, REPEAT/UNTIL). No GTO in
  ELEM47, ELD1, ELD2. Source indented in programs_rem/ELEM47.txt, without partner numbers; the build checks
  the structures like VALID and writes the numbers (IF 01 ...) into build/ELEM47.txt.
- One element record per data label: ELD1 LBL 01-60 (Z 1-60), ELD2 LBL 01-58 (Z - 60).
- Key dispatch by arithmetic (k div 10 - 6, k mod 10 - 3), R56 = R39 - 48 for the symbol column,
  :HLINE: unrolled by 37.
- Two builds:
  - release: programs_rem/ELEM47.txt -> tools/build_elem47.py -> programs/, build/ELEM47.txt, listings/
  - PIXEL variant (the one submitted): programs_rem/pixel/ELEM47.txt -> tools/build_pixel.py -> build/pixel/,
    listings/pixel/. The table's 11 horizontal rows by PIXEL (Y < 0 = full screen row), the parts without
    cells cleared (AGRAPH GRMOD 2 for columns 0/398/399, ATEXT spaces GRMOD 1); :ROWS: also for :CLOSE:.
    Victor ran it on his C47: works.
- Forum file: tools/build_p47u.py -> build/p47u/ELEM47.p47u (PIXEL variant, Version 1.1.0, '@' header for the
  C47 release res/PROGRAMS, 1 372 lines, md5 03292e0835fdaf279807ed6320a68e14). SUB, VERSION, TESTED at its top.
- Free42: tools/build_free42.py stops on purpose (no STRUCT in Free42); build/free42/ is the old v1.0.0.

## Numbers (simulator steps: main before -> now release / PIXEL)
table 7 833 -> 7 624 / 5 254; move 245 -> 235 / 235; box 1 040 -> 991 / 991; closing it 4 036 -> 3 910 / 2 737.
ELEM47 810 -> 775 (release) / 865 (PIXEL) steps; labels 51 -> 24 (26).

## How to build and test
    python3 tools/build_elem47.py && python3 tools/build_pixel.py && python3 tools/build_p47u.py
    python3 tests/test_elem47.py                                  # ~1 min; also checks the .p47u steps
    python3 tests/test_opt.py                                     # ~2 min, every screen vs tests/ref
    ELEM47_PROG=build/pixel/ELEM47.txt python3 tests/test_opt.py  # the same for a variant
    python3 tests/test_fw.py / tools/bench_fw.py [file]           # T47 + rejig: Victor's machine only
- ELEM47_PROG selects a variant in python/elem47sim.py, test_opt, test_fw.
- tests print nothing for long stretches: not hung. bench_fw prints only at the end of each of its 4 lines.
- Any new key-wait form must be replaced in tests/test_fw.py testcopy AND tools/bench_fw.py copy, or T47 waits
  for a key forever (happened once).

## Simulator caveats
- python/c47sim.py comes from Almanac 47 (fix there first, then copy). It has no STRUCT: python/elem47sim.py
  lower() rewrites the numbered structures as LBL/GTO before running (step counts close, not exact).
- c47sim CLLCDxy clears whole rows and ignores x (firmware: from column x right, from row y up): don't use it.
- c47sim has no CLREGS (elem47sim.split expands it).

## Cloud session limits
- No ~/opt (Almanac 47, c43, rejig) and no T47 in the cloud container: clone the firmware read-only from
  https://gitlab.com/rpncalculators/c43 into the scratchpad when its sources are needed (AN0007 in
  docs/appnotes/sources/AN0007_STRUCT, structured.c, screen.c fnPixel / fnAGraph / fnClLcd, res/PROGRAMS).
- rejig not available: the .p47u and builds are not compiled there; Victor checks with rejig.

## Branches
- main: everything. claude/wonderful-shannon-qu84ke and struct-pixel: merged (can be deleted by Victor).
- struct-loops: not merged, the comparison (unrolled AGRAPH as loops: table +72 %, kept only as a reference).
- CLAUDE.md: Victor opens and merges PRs; never force-push; commit author "Victor Valdes"
  <valdesvj@users.noreply.github.com>; never commit .p47 binaries.

## Pending
1. Victor: test_fw and bench_fw on the release and the PIXEL variant; rejig build/p47u/ELEM47.p47u. Then update
   TESTED in tools/build_p47u.py if T47 passes.
2. Forum: Jaymos to accept ELEM47.p47u (1 372 lines; 1 261 without the code comments if asked).
3. Optional: make the PIXEL variant the release (move programs_rem/pixel into programs_rem/ELEM47.txt).
4. Optional: tag v1.1.0, README heading still says v1.0.0.
5. Almanac 47 (other session): STRUCT branch from ALMANAC47_STRUCT_HANDOFF.md; STRUCT + CLLCDxy fix in
   c47sim.py there; then copy c47sim.py here and drop lower().
6. Free42: keep v1.0.0 or decide a new conversion path.
7. Faster moves: the panel + record read is ~95 of the 235 steps of a move (the next place to look).
