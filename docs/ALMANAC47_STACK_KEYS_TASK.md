# Almanac 47 task: keep the stack, clear only NAV's registers, keys 1-8 push a body (C47 STRUCT)

For a new Claude Code session working on the Almanac 47 repository (valdesvj/almanac47). Written from an
Elements 47 session on Oct 18, 2026, which only read Almanac 47. Read CLAUDE.md and DEVELOPMENT_NOTES.md there
first (the sections from "Oct 10, 2026 - STRUCT" on, and "v2.2.0 Struct on Attack").

## Where to start
- A new branch from main (v2.2.0, the C47 / R47 STRUCT release). Source: programs_struct/ (STRUCT, indented, no
  partner numbers, no GTO); build: tools/build_struct_src.py, tools/build_release_c47.py, tools/build_forum.py;
  tests: tests/test_struct_src.py (pixel for pixel), tests/test_fw_c47.py (the firmware simulator, Victor's machine).
- C47 / R47 only. Free42 / DM42 (v2.1.0) and NAVLITTLE are not part of this task unless Victor asks.

## 1. Keep the user's stack
- Today NAV clears the stack when it ends (CLSTK in several places of ALMA47) and sets the 8-level stack while it
  runs, then puts the user's stack size back. New: the stack the user had before XEQ "ALMA47" (4 or 8 levels, and
  LASTx) is the stack after it ends, except for the result of point 3.
- How Elements 47 v1.2.0 does it (elements47 DEVELOPMENT_NOTES, "Branch keep-stack"): at the start LocR 10, the
  8 levels with STO / R↓ into R.00-R.07 and LASTx into R.08; at the end RCL L ... 8 RCL back. In the firmware every
  XEQ level starts without local registers (lblGtoXeq.c fnExecute), so the copy must live where the main part runs
  (NAV's main level), and KEY? takes no local register (input.c fnKey). Check what NAV's text routines need from
  the 8-level stack (QUICKSTART: "NAV uses the 8-level stack while it runs").

## 2. Clear only the registers NAV uses
- No CLREGS of R00-R99: only the registers the calculation uses (the notes say R43-R98; check the source for every
  register written). R-CLR with X = sss.nn (Elements 47: 20.37 R-CLR clears R20-R56). The user's other registers stay.
- Today "0 on the menu ends NAV, gives your registers back": check whether that save / restore already exists and
  whether point 2 replaces it (fewer steps, less memory) or keeps it. Ask Victor if both are possible.
- Matrices and named variables NAV keeps on purpose (ALMC, ALMQ, SBR, VAL ...): unchanged unless Victor says.

## 3. Keys 1-8 on the views 1 ALMANAC and 2 SPLIT
- On a drawn ALMANAC or SPLIT view, keys 1 to 8 pick a body: 1 = the Sun, 2-8 = the next bodies in the order of the
  list on that view. The key ends the program and leaves on the stack the body's name (a text), its Zn and its Hc
  (numbers, from matrix ALMC: GHA Dec Hc Zn per row). Then the normal end (GRMOD 0, GRFNT 20, the user's stack size,
  point 1 and 2) with the result pushed on the user's stack.
- + still goes back to the menu; 9 still SNAP; the arrows still ±1 hour; other keys ignored, as now.
- QUESTIONS for Victor before coding (Elements 47 asked them, not answered yet):
  a. Stack layout: Z = name text, Y = Zn, X = Hc (proposed)? Or one text "Sun Zn 123.4 Hc 45.6"?
  b. Number format: decimal degrees, or degrees.minutes (D.MS, as navigators write Hc 45°36.2')?
  c. Which bodies are 2-8: the first 8 rows the view shows (ALMANAC: Sun, Moon, planets, brightest stars; SPLIT: its
     8 rows), and on a view with more rows than 8? Same 8 on both views, or each view its own list?
  d. A body below the horizon (Hc shown white on black): push it too?
  e. Keys 1-8 on the other views (SKY, ANIM, ALLSKY) and on the menu: unchanged (menu: 1-6 pick a view)?
- The key wait is the STRUCT form (DO / PAUSE / KEY? / WHILE / ENDDO or SKY's PAUSE 20 / KEY? / IF): the test copies
  of tests/test_fw.py and tests/test_fw_c47.py must replace any new key wait too (else T47 waits forever).
- Text to number: the C47 has no string -> number command; Elements 47's :TONUM: reads the digits with αPOS in
  "0123456789." if needed. Here the numbers come from ALMC, so no conversion should be needed.

## Checks
- Every page still pixel for pixel (test_struct_src.py), the menu keys, the arrows; new tests: keys 1-8 on ALMANAC
  and SPLIT give the right name, Zn, Hc (against python/ ephemeris), the user's stack (4 and 8 levels, LASTx) kept,
  the registers outside NAV's kept, only NAV's cleared.
- Firmware: tests/test_fw_c47.py on Victor's machine (the firmware simulator); then the calculator.
- Forum / release files: build_forum.py, build_release_c47.py, the manual (tools/generators/manual_nav.py), QUICKSTART,
  README; the '@ Tested:' lines say only what was run.
- CLAUDE.md there: Victor opens and merges the PRs; never force-push; commit author Victor Valdes.

## Also from the Elements 47 session (Oct 18)
- c47sim.py: Elements 47 now uses Almanac's c47sim.py of Oct 11 (native STRUCT). Elements 47 v1.2.0 still needs, in
  c47sim, R-CLR, local flags F.nn and LASTx (worked around in elements47 python/elem47sim.py split()); adding them
  here would let Elements 47 drop its last workarounds, and this task needs R-CLR and LocR too.
