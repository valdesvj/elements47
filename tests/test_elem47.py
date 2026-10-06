#!/usr/bin/env python3
"""ELEM47 in the C47 simulator (python/c47sim.py):
  - programs/ and build/ are up to date with programs_rem/ (tools/build_elem47.py)
  - the table: the H cell box (x 2-23, rows 2-27 from the top), nothing in the detail area
  - + opens the detail box: frame at x 80-319, rows 60-179 from the top, centred on the screen
  - a key on the detail box goes back to the table (the same screen as at the start)
  - another key on the table ends the program with GRFNT 20 and GRMOD 0 restored
  python3 tests/test_elem47.py"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools')]
import elem47sim, build_elem47

fails = []


def check(ok, msg):
    print(('ok    ' if ok else 'FAIL  ') + msg)
    if not ok:
        fails.append(msg)


def box(pix, x0, x1, r0, r1):
    """Is there a 1-pixel frame from column x0 to x1, row r0 to r1 (rows from the top)?"""
    edge = {(x, r) for x in range(x0, x1 + 1) for r in (r0, r1)} | {(x, r) for x in (x0, x1) for r in range(r0, r1 + 1)}
    return edge <= pix


def main():
    plain = [ln for ln in open(os.path.join(ROOT, 'programs', 'ELEM47.txt'), encoding='utf-8').read().splitlines()]
    src = [ln.rstrip() for ln in open(os.path.join(ROOT, 'programs_rem', 'ELEM47.txt'), encoding='utf-8')
           if ln.strip() and not ln.startswith('REM')]
    check(plain == src, 'programs/ELEM47.txt = programs_rem/ELEM47.txt without REM (run tools/build_elem47.py)')
    check(open(os.path.join(ROOT, 'build', 'ELEM47.txt')).read().splitlines() == plain, 'build/ELEM47.txt = programs/ELEM47.txt')

    shots, c = elem47sim.frames(keys=(85, 85, 82))
    check(len(shots) == 3, 'three screens: table, detail, table (%d)' % len(shots))
    table, detail, back = (shots + [set()] * 3)[:3]
    check(box(table, 2, 23, 2, 27), 'table: the H cell, x 2-23, rows 2-27')
    check(not any(80 <= x <= 319 and 80 <= r <= 179 for x, r in table), 'table: the detail area is empty')
    check(box(detail, 80, 319, 60, 179), 'detail: the frame, x 80-319, rows 60-179')
    check(not any((x, 59) in detail or (x, 180) in detail for x in range(80, 320)), 'detail: nothing just outside the frame')
    bar = sum(1 for x in range(81, 319) for r in range(61, 82) if (x, r) in detail)
    check(bar > 0.6 * 238 * 21, 'detail: the header bar is inverted (%d of %d pixels on)' % (bar, 238 * 21))
    check(box(detail, 2, 23, 2, 27), 'detail: drawn over the table (the H cell still there)')
    check(back == table, 'a key on the detail box: back to the same table')
    check(getattr(c, 'grfnt', 20) == 20 and getattr(c, 'grmod', 0) == 0, 'the end: GRFNT 20 and GRMOD 0 restored')
    check(not c.keys, 'the end: all keys used (the last one ended the program)')

    shots, c = elem47sim.frames(keys=(82,))
    check(len(shots) == 1 and not c.keys, 'a key other than + on the table ends at once')
    print('\n%s' % ('ALL OK' if not fails else '%d FAILED' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
