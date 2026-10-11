#!/usr/bin/env python3
"""Write build/p47u/ELEM47.p47u, the file for the PROGRAMS folder of the C47 release (res/PROGRAMS of the
firmware: BUILD.md there). A rejig source: the '@' header the index reads (Index, Author, Version) and the
other fields, then the three programs of the PIXEL variant, build/pixel/ELEM47.txt (ELEM47, ELD1, ELD2), with
the indentation and the comments of programs_rem/pixel/ELEM47.txt ('@' lines: not compiled). The steps are
those of build/pixel/ELEM47.txt, numeric labels and numbered structures (tests/test_elem47.py checks it). The
file name is the main program's name. SUB = '' would take the release (build/ELEM47.txt) instead.
  python3 tools/build_pixel.py && python3 tools/build_p47u.py"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_elem47 as B

VERSION = '1.2.0'
SUB = 'pixel'          # the variant of programs_rem/ and build/ submitted (the table's lines by PIXEL)
# what a run produced; after tests/test_fw.py passes in T47, say so here
TESTED = ('in the C47 firmware (T47, sources of 8 Oct 2026): the whole table both ways with the detail box\n'
          '@          opened and closed at every cell, every screen pixel for pixel the same as the simulator; the\n'
          '@          stack kept and F1 F2 F3 on 4 and 8 levels (SSIZE4, SSIZE8); v1.1.0 run on a C47 by the author')
HEADER = '''@ Index:   Interactive periodic table of the 118 elements
@ Author:  Victor Valdes
@ Version: %s
@ Source:  https://github.com/valdesvj/elements47
@ Tested:  %s
@ Input:   none (XEQ 'ELEM47')
@ Output:  the periodic table on the screen; key 0 ends with the stack as it was; in the detail box
@          F1 F2 F3 end with Z, the standard atomic weight or the boiling point (K) pushed on the stack
@
@ The 118 elements in an 18 x 9 grid (periods 1-7, then the lanthanides and the actinides), the symbol
@ and Z in each cell, the selected element (name, Z, standard atomic weight) in the empty part of periods 1-3.
@ Keys: 8 4 6 2 move the cursor (empty cells skipped; at an edge around to the other side), 5 the detail
@ box (symbol, mass, state, boiling point, group, electron configuration; 8 4 6 2 move in it, 5 closes it,
@ F1 F2 F3 end the program with Z, the mass or the boiling point in X: a value shown as "-" is not pushed),
@ 0 the end.
@
@ Three programs: ELEM47 (the code) and ELD1, ELD2 (the element records, Z 1-60 and 61-118).
@ C47 / R47 only: written with the STRUCT commands (IF / ELSE / ENDIF, DO / WHILE / ENDDO, REPEAT / UNTIL,
@ AN0007); a build without OPTION_STRUCTURED_PGM does not run it. Original DM42: packages 1-3 only (its STRUCT
@ limit, 10 IF a program: ELEM47 has 10), slower, not tried on one yet; package 4 has no STRUCT. Draws with AGRAPH and ATEXT (GRFNT 21
@ and 10), restores GRMOD 0 and GRFNT 20 at the end.
@ Style: no GTO in any of the three programs; every decision and loop is a STRUCT (the key loop and the key
@ wait are DO / WHILE / ENDDO), and a test before one step remains only where it guards a single XEQ or
@ RTN. No tail calls or jumps between routines; two routines have a second entry label that the first runs
@ into (the cursor runs into the cursor XOR, the detail box into the box from a record already read). The labels are the
@ routines (XEQ) and the data (XEQ IND).
@ The horizontal lines of the table are PIXEL with Y < 0 (one full screen row, one step each), the parts
@ without cells cleared again (AGRAPH in GRMOD 2, ATEXT of spaces in GRMOD 1): about 30 %% faster than drawing
@ them cell by cell. Each cell draws only its left edge.
@ Speed: the drawing is unrolled where it runs most: 21 AGRAPH for the cursor, 37 per round of the loop
@ for the box lines (a loop costs about 3 steps per AGRAPH); the routines of the key loop come first in the
@ program (each RTN counts the steps from the top).
@ The user's stack is kept: at the start LocR 10 and X..T (A..D on 8 levels) and LASTx in R.00-R.08, one
@ STO and one R↓ each, 8 times (on 4 levels R↓ goes round twice: no test of the stack size); at the end 8 RCL
@ (and STO L) give them back, then the value of F1-F3 (R.09, local flag F.00) is pushed: the top level goes,
@ as for any number keyed in. The local registers are released at the end (RTN).
@ ELEM47 uses R20-R56 and the matrix PT, and clears R20-R56 (R-CLR) and deletes PT at the end; the other
@ registers are the user's.
@ Data: standard atomic weights CIAAW 2024 (abridged, as the IUPAC periodic table; "-" where there is none),
@ state, boiling point and configuration from the PubChem periodic table.
@
''' % (VERSION, TESTED)


def build():
    lines = [ln.rstrip() for ln in open(os.path.join(ROOT, 'programs_rem', SUB, B.NAME + '.txt'), encoding='utf-8')]
    steps = B.plain_steps(lines)
    out, n = [], 0
    start = lines.index('LBL "%s"' % B.NAME)      # the REM header of the source: replaced by HEADER
    n = len(B.source_steps(lines[:start]))
    for ln in lines[start:]:
        if not ln.strip():
            continue
        ind = ln[:len(ln) - len(ln.lstrip())]
        if ln.lstrip().startswith('REM'):
            out.append(ind + '@ ' + ln.lstrip()[3:].strip())
        else:
            out.append(ind + steps[n]); n += 1
    assert n == len(steps)
    d = os.path.join(ROOT, 'build', 'p47u')
    os.makedirs(d, exist_ok=True)
    fn = os.path.join(d, B.NAME + '.p47u')
    with open(fn, 'w', encoding='utf-8') as fh:
        fh.write(HEADER + '\n'.join(out) + '\n')
    return fn


def steps_of(fn):
    """The steps of a .p47u: no '@' lines, no indentation (for the test)."""
    return [ln.strip() for ln in open(fn, encoding='utf-8') if ln.strip() and not ln.lstrip().startswith('@')]


if __name__ == '__main__':
    print(os.path.relpath(build(), ROOT))
