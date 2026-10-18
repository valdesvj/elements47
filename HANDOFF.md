# Elements 47: handoff for the next session (Oct 11, 2026, night)

Read CLAUDE.md and DEVELOPMENT_NOTES.md first (sections from "Branch struct" on, and the Oct 11 sections, the last
one "Branch keep-stack"). The Almanac 47 handoff (STRUCT branch there) is docs/ALMANAC47_STRUCT_HANDOFF.md.

## Released: v1.2.0 (C47 / R47), tag v1.2.0 = main 1319374 (squash of PR #11), "Latest" on GitHub
- New since v1.1.0: the user's stack (4 or 8 levels) and LASTx kept (LocR 10 at the start: 8 x STO / R↓ into
  R.00-R.07, LASTx into R.08; at the end RCL L ... 8 RCL); only R20-R56 cleared (20.37 R-CLR), no CLREGS / CLSTK.
  In the detail box F1 F2 F3 (KEY? 11-13, LBL :FKEY:) end with Z, the mass or the boiling point (K) pushed on
  the stack (R49 -> R.09, local flag F.00); "-" pushes nothing. There is no text -> number command on the
  C47: LBL :TONUM: reads the digits (αPOS in "0123456789."). The box: "F1: Z  F2: Mass  F3: Boil" in GRFNT 21
  under a line (row 75), the box down to row 56, the texts 4 rows up. Still 10 IF (DO 6).
- The zip ships the PIXEL build as v1.1.0 did: C47_R47/ELEM47.p47 (rejig of build/pixel/ELEM47.txt), the listing,
  the labels, ELEM47.p47u (1.2.0, md5 20dacd071ae08c3863c9f8b48239e17c); MANUAL.html / .md, docs/*.png, README,
  QUICKSTART. Zip and notes: build/release/ (untracked).
- Checked: test_elem47, test_opt, test_fw (T47, stack on 4 and 8 levels) on both builds. The final box (GRFNT 21
  line) not yet run on Victor's C47 (the tiny-font try was, "too small"); the release notes say "on a C47".
- Free42 / DM42 stock firmware (Oct 18): build/free42/ is now the v1.2.0 PIXEL source converted (STRUCT as labels
  and GTO, the stack / ALPHA / registers kept, F1-F3), tests/test_f42.py ALL OK in f42run (Free42 3.3.10); not
  released yet (the last Free42 release is v1.0.0). Before Oct 18: build/free42/ was the v1.0.0 build; build_free42.py stopped on STRUCT,
  and does not know LocR, R-CLR, local flags).

## Calculators (README "Which calculators", from the c43 sources)
- R47, DM42n (DMCP 5, NEW_HW), firmware 00.109.05.00a0.ALPHA or later: runs (T47, Victor's C47).
- Original DM42 (DMCP 3, OLD_HW, C47.pgm packages 1-4): STRUCT in packages 1-3 only, at most 10 IF / 10 DO /
  10 REPEAT per program and 10 levels (structured.h); ELEM47 has 10 IF, 6 DO, 1 REPEAT, 4 levels;
  build_elem47.py stops past the limit (DM42_MAX). Should run there, slower; NOT TRIED on a real original DM42.
  Package 4: no STRUCT.
- 00.109.04.00b0 and earlier: no STRUCT, ATEXT, GRFNT anywhere.

## How to build and test
    python3 tools/build_elem47.py && python3 tools/build_pixel.py && python3 tools/build_p47u.py
    python3 tools/build_manual.py
    python3 tests/test_elem47.py; python3 tests/test_opt.py; ELEM47_PROG=build/pixel/ELEM47.txt python3 tests/test_opt.py
    python3 tests/test_fw.py; ELEM47_PROG=build/pixel/ELEM47.txt python3 tests/test_fw.py   # T47, ~8 min each
    python3 tools/bench_fw.py build/pixel/ELEM47.txt      # T47 instructions (numbers of v1.1.0: table 84.9 M)
A change goes into both sources: programs_rem/ELEM47.txt and programs_rem/pixel/ELEM47.txt (the release).
test_opt leaves out the inside of the box under the header bar (x 50-349, rows 56-157) against the optimize
reference, since v1.2.0 moved it; test_elem47 and test_fw check it.

## Pending
1. Victor on his C47 with the released v1.2.0 p47 (the GRFNT 21 line under the rule, F1 F2 F3, the stack).
2. Forum: Victor sends Jaymos the v1.2.0 build/p47u/ELEM47.p47u (md5 20dacd071ae08c3863c9f8b48239e17c).
3. A test on a real original DM42 (packages 1-3).
4. tools/bench_fw.py: its 'moves' keys now reach edges (wrap-around): change them so the numbers compare;
   then measure v1.2.0 (the box: 1008 steps in the simulator against 1000).
5. Almanac 47 session: STRUCT branch; c47sim.py fixes (native STRUCT, CLLCDxy, CLREGS, R-CLR, local flags F.nn,
   LASTx, the GRFNT 21 line-wrap test x + adv + 1 > 400); then copy c47sim.py here and drop the lowering in
   elem47sim.split() / lower().
6. Optional: programs_rem/pixel as the only source; faster moves (panel + record ~95 of 235 steps).
7. Dropped on purpose: a LBL/GTO build for the DM42 (DEVELOPMENT_NOTES), the 9 x IP(row/8) form (+8 % table),
   (a Free42 version of v1.2.0: done after all on Oct 18, Victor's request).
8. c47sim.py is Almanac's of Oct 18 (STRUCT, R-CLR, local flags, LASTx native): elem47sim has no workarounds left.
9. Free42 release of v1.2.0 (the .raw by rejig, the zip): Victor's call. f42run: Almanac's tools/f42/setup.sh.
10. Firmware PROGRAMS folder has ELEM47 v1.1.0: Jaymos to get v1.2.0 (item 2).
11. Almanac 47 task: docs/ALMANAC47_STACK_KEYS_TASK.md (stack, NAV's registers only, keys 1-8 on ALMANAC / SPLIT).
Done since the last handoff: the v1.1.0 release text on GitHub has the DM42 paragraph (checked Oct 11).

## Branches
main; local-registers and struct-loops kept as references (not merged).
