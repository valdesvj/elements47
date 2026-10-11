# Elements 47: handoff for the next session (Oct 11, 2026, evening)

Read CLAUDE.md and DEVELOPMENT_NOTES.md first (sections from "Branch struct" on, and the Oct 11 sections).
The Almanac 47 handoff (STRUCT branch there) is docs/ALMANAC47_STRUCT_HANDOFF.md.

## Released: v1.1.0 (C47 / R47), tag v1.1.0 = main 5f2b476 (merge of PR #9)
- The zip ships the PIXEL build: C47_R47/ELEM47.p47 (rejig of build/pixel/ELEM47.txt), the listing, the labels,
  ELEM47.p47u; MANUAL.html / .md, docs/*.png, README, QUICKSTART. Zip and release notes: build/release/
  (untracked). The zip on GitHub was replaced on Oct 11 with the 10-IF program (same version number, as Victor asked).
- New since v1.0.0: the arrows go around the edges (LBL :STEP: MOD), STRUCT only (no GTO), one record per data
  label, the table's rows by PIXEL, the user's manual (tools/build_manual.py writes MANUAL.md, MANUAL.html and two
  of the screens).
- Free42 / DM42 stock firmware: v1.0.0 (build/free42/ is still the v1.0.0 build; build_free42.py stops on STRUCT).

## Calculators (README "Which calculators", from the c43 sources)
- R47, DM42n (DMCP 5, NEW_HW), firmware 00.109.05.00a0.ALPHA or later: runs (T47, Victor's C47).
- Original DM42 (DMCP 3, OLD_HW, C47.pgm packages 1-4): STRUCT in packages 1-3 only, at most 10 IF / 10 DO /
  10 REPEAT per program and 10 levels (structured.h); ELEM47 now has 10 IF (XEQ :KELVIN: instead of an IF), 5 DO,
  1 REPEAT, 4 levels; build_elem47.py stops past the limit (DM42_MAX). Should run there, slower; NOT TRIED on a
  real original DM42. Package 4: no STRUCT. Master of 8 Oct had STRUCT/ATEXT/GRFNT out for the DM42, 10 Oct back.
- 00.109.04.00b0 and earlier: no STRUCT, ATEXT, GRFNT anywhere.

## Fixed this session
- PIXEL variant: columns 398-399 of rows 4/29/54 stayed black in the firmware (ATEXT space at x 393 wraps to the
  next line in _doShowString; c47sim does not). Now x 392. test_fw passes on both builds (955 of 955).

## How to build and test
    python3 tools/build_elem47.py && python3 tools/build_pixel.py && python3 tools/build_p47u.py
    python3 tools/build_manual.py
    python3 tests/test_elem47.py; python3 tests/test_opt.py; ELEM47_PROG=build/pixel/ELEM47.txt python3 tests/test_opt.py
    python3 tests/test_fw.py; ELEM47_PROG=build/pixel/ELEM47.txt python3 tests/test_fw.py   # T47, ~8 min each
    python3 tools/bench_fw.py build/pixel/ELEM47.txt      # T47 instructions: table 84.9 M, boxes 504.4 M

## Pending
1. GitHub release text: `gh release edit v1.1.0 --notes-file build/release/NOTES_v1.1.0.md` (the DM42 paragraph
   was not on GitHub at the last check).
2. Forum: Victor sends Jaymos the corrected build/p47u/ELEM47.p47u (md5 e1a535aaa27c1f5e7e9673905253390c, 10 IF).
3. A test on a real original DM42 (packages 1-3); Victor on his C47 with the released p47.
4. tools/bench_fw.py: its 'moves' keys now reach edges (wrap-around): change them so the numbers compare.
5. Almanac 47 session: STRUCT branch; c47sim.py fixes (native STRUCT, CLLCDxy, CLREGS, the GRFNT 21 line-wrap
   test x + adv + 1 > 400); then copy c47sim.py here and drop elem47sim.lower().
6. Optional: programs_rem/pixel as the only source; faster moves (panel + record ~95 of 235 steps).
7. Dropped on purpose: a LBL/GTO build for the DM42 (DEVELOPMENT_NOTES), the 9 x IP(row/8) form (+8 % table).

## Branches
main; local-registers and struct-loops kept as references (not merged).
