#!/usr/bin/env python3
"""ELEM47 in the C47 simulator (python/c47sim.py):
  - programs/ and build/ are up to date with programs_rem/ (tools/build_elem47.py)
  - the table: the frame of every one of the 118 cells, the matrix PT = the positions of python/elements.py
  - the data lookup (LBL 30, ELD1 / ELD2) for every element: symbol, name, mass, state, boil, config
  - the detail texts (symbol, state, group, config; mass, boiling point)
  - the cursor: 8 4 6 2, gaps skipped, the edges of the table
  - 5: the detail box (frame), any key: the table again with the cursor kept; 0: the end
  python3 tests/test_elem47.py"""
import os, sys
from decimal import Decimal as D
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools')]
import c47sim, elem47sim as E
from elements import ELEMENTS, EXTRA, position

fails = []


def check(ok, msg):
    print(('ok    ' if ok else 'FAIL  ') + msg)
    if not ok:
        fails.append(msg)


def box(pix, x0, x1, r0, r1):
    """A 1-pixel frame from column x0 to x1, row r0 to r1 (rows from the top)?"""
    edge = {(x, r) for x in range(x0, x1 + 1) for r in (r0, r1)} | {(x, r) for x in (x0, x1) for r in range(r0, r1 + 1)}
    return edge <= pix


def cell(r, c):
    """The frame of the cell at row r, column c: x0, x1, top row, bottom row (rows from the top)."""
    x0 = 22 * c - 21
    y0 = 238 - 25 * r - (9 if r > 7 else 0)          # bottom row, row 0 = bottom
    return x0, x0 + 22, 239 - (y0 + 25), 239 - y0


def cursor_after(keys):
    _, c = E.frames(list(keys) + [E.END])
    return int(c.reg['36'])


def main():
    plain = open(os.path.join(ROOT, 'programs', 'ELEM47.txt'), encoding='utf-8').read().splitlines()
    check(sum(1 for ln in plain if ln.startswith('LBL "')) == 3 and plain.count('END') == 3,
          'one file, three programs: ELEM47, ELD1, ELD2')
    src = [ln.rstrip() for ln in open(os.path.join(ROOT, 'programs_rem', 'ELEM47.txt'), encoding='utf-8')
           if ln.strip() and not ln.startswith('REM')]
    check(plain == src, 'programs/ELEM47.txt = programs_rem/ELEM47.txt without REM (run tools/build_elem47.py)')
    check(open(os.path.join(ROOT, 'build', 'ELEM47.txt')).read().splitlines() == plain, 'build/ELEM47.txt = programs/ELEM47.txt')

    shots, c = E.frames([E.INFO])
    table = shots[0]
    bad = [z for z in range(1, 119) if not box(table, *cell(*position(z)))]
    check(not bad, 'table: the frames of the 118 cells %s' % (bad[:5] or ''))
    pt = c.mats['PT']
    want = [[0] * 18 for _ in range(9)]
    for z in range(1, 119):
        r, col = position(z); want[r - 1][col - 1] = z
    check([[int(v) for v in row] for row in pt] == want, 'the matrix PT: the Z of every cell, 0 in the gaps')
    check(all(0 <= x < 400 and 0 <= r < 240 for x, r in table), 'everything on the 400 x 240 screen')

    # LBL 30 for every element: symbol, name, mass, state, boiling point, configuration
    wrong = []
    for z in range(1, 119):
        c.s = [D(0)] * 4; c.reg['36'] = D(z)
        c.run('0_30')
        s_, n, m = ELEMENTS[z - 1]
        got = (str(c.reg['35']).strip(), c.reg['43'], c.reg['41'], c.reg['51'], c.reg['52'], c.reg['53'])
        if got != (s_, n, m) + tuple(EXTRA[z - 1]):
            wrong.append((z,) + got)
    check(not wrong, 'data of the 118 elements: symbol, name, mass, state, boil, config %s' % (wrong[:2] or ''))

    # the two value texts of the detail box (LBL 45): left R44 symbol, state, group, config; right R54 mass, boil
    CR = '\u21b5'
    for z, group in [(1, '1  Nonmetal'), (2, '18  Noble gases'), (5, '13  Boron group'), (26, '8  Transition metals'),
                     (56, '2  Alkaline earth metals'), (62, 'Lanthanides'), (92, 'Actinides'), (117, '17  Halogens'),
                     (118, '18  Noble gases')]:
        r, col = position(z); sym, _, mass = ELEMENTS[z - 1]; state, boil, cfg = EXTRA[z - 1]
        c.s = [D(0)] * 4; c.reg.update({'36': D(z), '37': D(r), '38': D(col)})
        c.run('0_45')
        left = CR.join(((sym + ' ')[:2], state, group, cfg)); right = CR.join((mass, boil))
        check(c.reg['44'] == left and c.reg['54'] == right,
              'detail of %s: %s || %s' % (sym, c.reg['44'].replace(CR, ' | '), c.reg['54'].replace(CR, ' | ')))

    R, L, U, Dn = E.RIGHT, E.LEFT, E.UP, E.DOWN
    for keys, z, what in [((R,), 2, 'H right: He (the gap of period 1 skipped)'),
                          ((Dn, Dn, Dn), 19, 'H down x3: K'),
                          ((L,), 1, 'H left: stays (edge)'), ((U,), 1, 'H up: stays (edge)'),
                          ((Dn,) * 5 + (R,), 56, 'Cs right: Ba'),
                          ((Dn,) * 5 + (R, R), 72, 'Ba right: Hf (the empty column 3 skipped)'),
                          ((Dn,) * 4 + (R, R, Dn), 57, 'Y down: La (periods 6, 7 of column 3 and the gap skipped)'),
                          ((Dn,) * 4 + (R, R, Dn, U), 39, 'La up: Y'),
                          ((Dn,) * 4 + (R, R, Dn, Dn, Dn), 89, 'Ac down: stays (edge)'),
                          ((R, Dn, Dn, Dn, Dn, Dn, Dn, Dn), 118, 'He down to the end of column 18: Og')]:
        got = cursor_after(keys)
        check(got == z, '%s (%d)' % (what, got))

    shots, c = E.frames([E.DOWN] * 6 + [E.RIGHT] * 17 + [E.INFO])
    E.png(os.path.join(ROOT, 'docs', 'ELEM47_detail_og.png'), shots[-1])
    line = [x for x, r in shots[-1] if 146 <= r <= 165 and 51 <= x <= 348]     # the Config line (rows from the top)
    check(line and max(line) < 340, 'detail of Og: the longest configuration ends at x %d, inside the box (x 50-349)'
          % max(line or [0]))

    shots, c = E.frames([E.RIGHT, E.INFO, 1, E.END])
    check(len(shots) == 4, 'screens: table, He, detail, table (%d)' % len(shots))
    check(box(shots[2], 50, 349, 60, 179), 'detail: the frame, x 50-349, rows 60-179')
    check(shots[3] == shots[1], 'a key on the detail box: the table again, the cursor still on He')
    check(getattr(c, 'grfnt', 20) == 20 and getattr(c, 'grmod', 0) == 0 and 'PT' not in c.mats,
          '0: the end, GRFNT 20 and GRMOD 0 restored, PT deleted')
    check(not c.keys, 'the end: all keys used')
    print('\n%s' % ('ALL OK' if not fails else '%d FAILED' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
