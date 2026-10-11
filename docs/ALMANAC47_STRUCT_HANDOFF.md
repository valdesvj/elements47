# Almanac 47: C47-only branch in STRUCT style, from what was done in Elements 47

Hand-off from an Elements 47 session (Oct 10, 2026; elements47 PR #6, merged as 5963a52 on main).
For a new session working on Almanac 47. Read elements47 DEVELOPMENT_NOTES.md, the sections
"Branch struct", "Branch struct-loops" and "Branch struct-pixel": they hold the details and the numbers.

## The task
A new branch of Almanac 47, C47 only, with the control flow rewritten in the C47 STRUCT commands
(no GTO for decisions and loops), then the same speed work as Elements 47. The Free42 build is not
converted on that branch (Free42 has no STRUCT): its build should stop with a clear message.

## The C47 STRUCT commands (firmware sources ~/opt/c43, also gitlab.com/rpncalculators/c43)
- Spec and guide: docs/appnotes/sources/AN0007_STRUCT/ (Structured Programming Guide, Specification,
  examples .txt, and the rejig patch rejig_C47_items_2920-2939_rejig-v0.31.0_9979c5e7c6.patch).
- Code: src/c47/programming/structured.c; items 2920-2939 in items.c. In every C47 build (OPTION_STRUCTURED_PGM).
- IF / ELSE / ENDIF: a test just before IF; true runs the body, false jumps to ELSE or ENDIF.
- DO / WHILE / ENDDO: the test just before WHILE, anywhere in the body (also right before ENDDO = do-while);
  false jumps past ENDDO; ENDDO goes back to the step after DO.
- REPEAT / UNTIL: the test just before UNTIL; true ends, false goes back after REPEAT.
- FOR / NEXT: take start, end, step off the stack and use local registers: not used in Elements 47
  (AGRAPH keeps its row and column on the stack).
- Tests that work: the comparisons, flag tests, DSE / ISG..., and KEY? (fnKey: TRUE when no key was pressed).
- Partner numbers: IF, DO and REPEAT in three series, 1-255 per program, in the order the openers appear
  (VALID). rejig (with that patch) writes them as "IF 01". The C47 checks only the LAST program of a file
  as it loads, so the build must write the numbers into the file.
- The firmware never skips a structure step after a legacy test (structNoLegacySkip): no test right before
  ELSE / ENDIF / DO / ENDDO / REPEAT / UNTIL. A test before one ordinary step (X<0? RTN, X≠0? XEQ) is fine.
- A RTN inside a structure is allowed (it closes what is open). A structure may not cross RTN + LBL.
- Speed: a STRUCT jump is a label lookup, like a local GTO; ENDIF / ENDDO count as steps.

## What was done in Elements 47 (do the same in Almanac 47)
1. Source (programs_rem) written with STRUCT, indented two spaces per level, without numbers.
   The build tool strips the indentation, checks the structures as VALID does (closer of the right kind,
   nothing open at END or across RTN/LBL, DO has its WHILE, test before IF/WHILE/UNTIL, no test before
   ELSE/ENDIF/DO/ENDDO/REPEAT/UNTIL) and writes the numbers (elements47 tools/build_elem47.py: structures(),
   is_test(), source_steps(), plain_steps()). The listing keeps the indentation.
2. Key wait: DO / PAUSE 50 / KEY? r / WHILE / ENDDO (same behaviour as LBL n / PAUSE 50 / KEY? r / GTO n).
3. The main part first: XEQ :INIT:, then the key loop as one DO ... ENDDO (the test for the end key before
   WHILE), the routines after it (each RTN counts the steps from the start of the program, so callers early).
4. Key dispatch by arithmetic where it fits, not one IF per key (Elements 47: direction = k div 10 - 6,
   k mod 10 - 3, a move when |rows| + |columns| = 1).
5. Every GTO loop / branch became IF / DO / REPEAT. Alternate entries by GTO into the middle of a routine
   were split into a small routine + the normal XEQ. Result in Elements 47: 0 GTO, 51 -> 24 labels.
6. Unrolled AGRAPH runs stay unrolled (rolling them into loops: +3 steps per column, the table +72 %).
   Longer unrolled bodies in a DO loop are fine (fewer rounds of the loop).
7. Data: one record per data label when the program has the labels for it (no skip loop; room to add fields).
8. PIXEL (screen.c fnPixel): X < 0 draws column |X| over the full height, Y < 0 row |Y| over the full width,
   black, one step, GRMOD ignored. Elements 47 draws its 11 table rows that way and clears the parts with no
   cell (AGRAPH in GRMOD 2, ATEXT of spaces in GRMOD 1: 7 x 20 pixels each in GRFNT 21): the table -31 %.
   Check whether any Almanac 47 screen has full-width or full-height lines drawn by AGRAPH.

## In Almanac 47 itself (the right place, then copied to elements47)
- c47sim.py: add the STRUCT commands natively (IF/ELSE/ENDIF, DO/WHILE/ENDDO, REPEAT/UNTIL, with the
  numbers; KEY? as a test). Elements 47 only lowers them to LBL/GTO in python/elem47sim.py lower() as a
  stop-gap; once c47sim has them, copy c47sim.py to elements47 and drop lower().
- c47sim.py bug: CLLCDxy clears whole rows and ignores x. The firmware (screen.c fnClLcd) clears from
  column x to the right edge and from row y up to the top.
- c47sim.py has no CLREGS yet (elements47 elem47sim.split works around it).
- Test tools that copy the program for T47 (like elements47 tests/test_fw.py testcopy and tools/bench_fw.py
  copy) must replace the new key wait DO n / PAUSE / KEY? r / WHILE n / ENDDO n too, or T47 waits for a key
  forever (that happened with bench_fw).
- Keep "Optimizations must keep the screens": compare every screen pixel for pixel with the release.

## Results in Elements 47 (simulator steps, main -> merged main)
the table 7 833 -> 7 624 (release) / 5 254 (PIXEL variant); a move 245 -> 235; the box 1 040 -> 991;
closing it 4 036 -> 3 910 / 2 737. ELEM47 810 -> 775 steps, 0 GTO. Firmware (T47 test_fw, bench_fw) still to run.
