#!/usr/bin/env python3
"""ELEM47 in the C47 simulator (python/c47sim.py):
  - programs/ and build/ are up to date with programs_rem/ (tools/build_elem47.py)
  - the table: the frame of every one of the 118 cells, the matrix PT = the positions of python/elements.py
  - three programs: ELEM47 (the code, numeric local labels), ELD1 and ELD2 (the element records)
  - the detail box data of every element (LBL :DETAIL:, the records 4 per label): name, symbol, mass, state,
    boil, group, config
  - the detail texts (symbol, state, group, config; mass, boiling point)
  - the cursor: 8 4 6 2, gaps skipped, the edges of the table
  - 5: the detail box (frame), 5 again: the table again with the cursor kept; the arrows with the box open:
    the box of the next element; other keys ignored; 0: the end
  python3 tests/test_elem47.py"""
import os, sys
from decimal import Decimal as D
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools')]
import c47sim, elem47sim as E
from elements import ELEMENTS, EXTRA, position
from build_elem47 import label_numbers

DETAIL = '0_%d' % label_numbers()['DETAIL']    # its local number in ELEM47 (c47sim: program 0, no leading 0)

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


GROUPS = ['Nonmetal', 'Alkali metals', 'Alkaline earth metals', 'Transition metals', 'Boron group', 'Carbon group',
          'Pnictogens', 'Chalcogens', 'Halogens', 'Noble gases', 'Lanthanides', 'Actinides']


def group(z):
    """The group text of the detail box: number and name, or the name of the series (rows 8-9)."""
    r, col = position(z)
    if r > 7:
        return GROUPS[r + 2]
    k = 0 if z == 1 else col if col <= 2 else 3 if col <= 12 else col - 9
    return '%d  %s' % (col, GROUPS[k])


def cursor_after(keys):
    """Z under the cursor after the keys (read before the end: key 0 gives the registers back)."""
    _, c = E.frames(list(keys))
    return int(c.reg[E.REG['Z']])


def main():
    plain = open(os.path.join(ROOT, 'programs', 'ELEM47.txt'), encoding='utf-8').read().splitlines()
    check([ln for ln in plain if ln.startswith('LBL "')] == ['LBL "ELEM47"', 'LBL "ELD1"', 'LBL "ELD2"']
          and plain.count('END') == 3, 'three programs: ELEM47 (the code), ELD1 and ELD2 (the records)')
    import re
    num = label_numbers()
    src = [ln.rstrip() for ln in open(os.path.join(ROOT, 'programs_rem', 'ELEM47.txt'), encoding='utf-8')
           if ln.strip() and not ln.startswith('REM')]
    check(plain == [re.sub(r' :(\w+):$', lambda m: ' %02d' % num[m.group(1)], ln) for ln in src],
          'programs/ELEM47.txt = programs_rem/ELEM47.txt without REM, each named label its local number')
    check(not any(re.search(r' :\w+:$', ln) for ln in plain), 'numeric local labels only')
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

    # the detail box (LBL 45) of every element: name, symbol, and its two value texts:
    # left R44 symbol, state, group number and name, configuration; right R54 mass, boiling point
    CR = '\u21b5'
    wrong = []
    for z in range(1, 119):
        r, col = position(z); sym, name, mass = ELEMENTS[z - 1]; state, boil, cfg = EXTRA[z - 1]
        c.s = [D(0)] * 4; c.reg.update({E.REG['Z']: D(z), E.REG['ROW']: D(r), E.REG['COL']: D(col)})
        c.run(DETAIL)
        left = CR.join(((sym + ' ')[:2], state, group(z), cfg)); right = CR.join((mass, boil))
        if (c.reg[E.REG['NAME']], c.reg[E.REG['LEFT']], c.reg[E.REG['RIGHT']]) != (name, left, right):
            wrong.append((z, c.reg[E.REG['NAME']], c.reg[E.REG['LEFT']].replace(CR, ' | '), c.reg[E.REG['RIGHT']].replace(CR, ' | ')))
    check(not wrong, 'detail box data of the 118 elements: name, symbol, state, group, config, mass, boil %s'
          % (wrong[:2] or ''))
    for z in (1, 26, 62, 118):
        c.s = [D(0)] * 4; r, col = position(z); c.reg.update({E.REG['Z']: D(z), E.REG['ROW']: D(r), E.REG['COL']: D(col)})
        c.run(DETAIL)
        print('      %s: %s || %s' % (ELEMENTS[z - 1][0], c.reg[E.REG['LEFT']].replace(CR, ' | '), c.reg[E.REG['RIGHT']].replace(CR, ' | ')))

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

    shots, c = E.frames([E.RIGHT, E.INFO, 1, E.INFO, E.END])
    check(len(shots) == 5, 'screens: table, He, detail, detail, table (%d)' % len(shots))
    check(box(shots[2], 50, 349, 60, 179), 'detail: the frame, x 50-349, rows 60-179')
    check(shots[3] == shots[2], 'key 1 on the detail box: ignored')
    check(shots[4] == shots[1], '5 on the detail box: the table again, the cursor still on He')
    inbox, _ = E.frames([E.INFO, E.RIGHT, E.INFO])
    direct, _ = E.frames([E.RIGHT, E.INFO])
    check(inbox[2] == direct[2], 'box open on H, right: the box of He, as opened on He')
    check(inbox[3] == direct[1], 'then 5: the table with the cursor and the panel on He')
    edge, _ = E.frames([E.INFO, E.LEFT])
    check(edge[2] == edge[1], 'box open on H, left (edge): the same box')
    check(getattr(c, 'grfnt', 20) == 20 and getattr(c, 'grmod', 0) == 0 and 'PT' not in c.mats,
          '0: the end, GRFNT 20 and GRMOD 0 restored, PT deleted')
    check(not c.keys, 'the end: all keys used')
    print('\n%s' % ('ALL OK' if not fails else '%d FAILED' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
