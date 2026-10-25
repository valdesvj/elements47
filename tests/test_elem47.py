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
  - F1 F2 F3 with the box open (LBL :FKEY:): Z, the mass, the boiling point of every element (none for "-");
    the end: the user's stack and LASTx back (the value pushed on it), R20-R56 cleared, the other registers kept
  python3 tests/test_elem47.py"""
import os, sys
from decimal import Decimal as D
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools')]
import c47sim, elem47sim as E
from elements import ELEMENTS, EXTRA, position
from build_elem47 import label_numbers, plain_steps

DETAIL = '0_%d' % label_numbers()['DETAIL']    # its local number in ELEM47 (c47sim: program 0, no leading 0)
FKEY = '0_%d' % label_numbers()['FKEY']
F1, F2, F3 = 11, 12, 13                          # KEY? codes of the function keys (keyboard.c setLastKeyCode)

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
    src = [ln.rstrip() for ln in open(os.path.join(ROOT, 'programs_rem', 'ELEM47.txt'), encoding='utf-8')]
    check(plain == plain_steps(src),
          'programs/ELEM47.txt = programs_rem/ELEM47.txt without REM and indentation, each named label its local '
          'number, the structures numbered')
    check(not any(re.match(r'GTO ', ln) for ln in plain[:plain.index('END')]), 'ELEM47: no GTO (STRUCT)')
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import build_p47u
    p47u = build_p47u.build()
    head = [ln for ln in open(p47u, encoding='utf-8').read().split('\n')[:3]]
    sub = os.path.join(ROOT, 'build', build_p47u.SUB, 'ELEM47.txt')
    want = open(sub, encoding='utf-8').read().splitlines()
    check(build_p47u.steps_of(p47u) == [ln for ln in want if ln] and head[0].startswith('@ Index:')
          and os.path.basename(p47u) == 'ELEM47.p47u',
          'build/p47u/ELEM47.p47u (the C47 release PROGRAMS folder): the @ header, the same steps as %s'
          % os.path.relpath(sub, ROOT))
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
    # F1 F2 F3 on the box of every element: R49 = Z, the mass, the boiling point (0: "-", nothing pushed),
    # R33 = 82 (the end)
    wrong = []
    for z in range(1, 119):
        r, col = position(z); mass, boil = ELEMENTS[z - 1][2], EXTRA[z - 1][1]
        for key, want in ((F1, D(z)), (F2, D(mass) if mass != '-' else D(0)),
                          (F3, D(boil[:-2]) if boil != '-' else D(0))):
            c.s = [D(0)] * 4; c.reg.update({E.REG['Z']: D(z), E.REG['ROW']: D(r), E.REG['COL']: D(col)})
            c.run(DETAIL)
            c.reg.update({'36': D(1), '33': D(key)})
            c.run(FKEY)
            if c.reg['49'] != want or c.reg['33'] != 82:
                wrong.append((z, key, str(c.reg['49']), str(want)))
    check(not wrong, 'F1 F2 F3: Z, mass, boiling point of the 118 elements (0 for "-") %s' % (wrong[:3] or ''))
    c.reg.update({'36': D(0), '33': D(F1)}); c.run(FKEY)
    check(c.reg['33'] == F1, 'F1 with the box closed: ignored')

    for z in (1, 26, 62, 118):
        c.s = [D(0)] * 4; r, col = position(z); c.reg.update({E.REG['Z']: D(z), E.REG['ROW']: D(r), E.REG['COL']: D(col)})
        c.run(DETAIL)
        print('      %s: %s || %s' % (ELEMENTS[z - 1][0], c.reg[E.REG['LEFT']].replace(CR, ' | '), c.reg[E.REG['RIGHT']].replace(CR, ' | ')))

    R, L, U, Dn = E.RIGHT, E.LEFT, E.UP, E.DOWN
    for keys, z, what in [((R,), 2, 'H right: He (the gap of period 1 skipped)'),
                          ((Dn, Dn, Dn), 19, 'H down x3: K'),
                          ((L,), 2, 'H left: around to He'), ((U,), 87, 'H up: around, rows 9 and 8 of column 1 skipped: Fr'),
                          ((R, R), 1, 'He right: around to H'),
                          ((Dn,) * 5 + (R,), 56, 'Cs right: Ba'),
                          ((Dn,) * 5 + (R, R), 72, 'Ba right: Hf (the empty column 3 skipped)'),
                          ((Dn,) * 4 + (R, R, Dn), 57, 'Y down: La (periods 6, 7 of column 3 and the gap skipped)'),
                          ((Dn,) * 4 + (R, R, Dn, U), 39, 'La up: Y'),
                          ((Dn,) * 4 + (R, R, Dn, Dn), 89, 'La down: Ac'),
                          ((Dn,) * 4 + (R, R, Dn, Dn, Dn), 21, 'Ac down: around, rows 1-3 of column 3 skipped: Sc'),
                          ((Dn,) * 4 + (R, R, Dn, Dn, L), 103, 'Ac left: around, columns 18 and 17 of row 9: Lr'),
                          ((R,) + (Dn,) * 6, 118, 'He down to the end of column 18: Og'),
                          ((R,) + (Dn,) * 7, 2, 'Og down: around, rows 8 and 9 of column 18 skipped: He')]:
        got = cursor_after(keys)
        check(got == z, '%s (%d)' % (what, got))

    shots, c = E.frames([E.DOWN] * 6 + [E.RIGHT] * 16 + [E.INFO])
    E.png(os.path.join(ROOT, 'docs', 'ELEM47_detail_og.png'), shots[-1])
    line = [x for x, r in shots[-1] if 142 <= r <= 161 and 51 <= x <= 348]     # the Config line (rows from the top)
    check(line and max(line) < 340, 'detail of Og: the longest configuration ends at x %d, inside the box (x 50-349)'
          % max(line or [0]))

    shots, c = E.frames([E.RIGHT, E.INFO, 1, E.INFO, E.END])
    check(len(shots) == 5, 'screens: table, He, detail, detail, table (%d)' % len(shots))
    check(box(shots[2], 50, 349, 60, 183), "detail: the frame, x 50-349, rows 56-179")
    check(shots[3] == shots[2], 'key 1 on the detail box: ignored')
    check(shots[4] == shots[1], '5 on the detail box: the table again, the cursor still on He')
    inbox, _ = E.frames([E.INFO, E.RIGHT, E.INFO])
    direct, _ = E.frames([E.RIGHT, E.INFO])
    check(inbox[2] == direct[2], 'box open on H, right: the box of He, as opened on He')
    check(inbox[3] == direct[1], 'then 5: the table with the cursor and the panel on He')
    edge, _ = E.frames([E.INFO, E.LEFT])
    check(edge[2] == direct[2], 'box open on H, left (around the edge): the box of He')
    check(getattr(c, 'grfnt', 20) == 20 and getattr(c, 'grmod', 0) == 0 and 'PT' not in c.mats,
          '0: the end, GRFNT 20 and GRMOD 0 restored, PT deleted')
    check(not c.keys, 'the end: all keys used')

    # the user's stack, LASTx and registers: kept; the value of F1-F3 pushed (the top level goes); R20-R56 cleared
    fe = [E.DOWN] * 3 + [E.RIGHT] * 7 + [E.INFO]
    user = {'5': D(5), '19': D(19), '57': D(57), '99': D(99), '20': D(20), '56': D(56)}
    for keys, top, what in [(fe + [E.END], None, 'Fe, 0'), (fe + [F1], D(26), 'Fe, F1: Z'),
                            (fe + [F2], D('55.845'), 'Fe, F2: the mass'), (fe + [F3], D(3134), 'Fe, F3: the boiling point'),
                            ([E.DOWN] * 6 + [E.LEFT, E.INFO, F3], None, 'Og, F3: "-", nothing pushed'),
                            ([F1, E.END], None, 'F1 with the box closed: ignored, then 0')]:
        c = c47sim.load(E.split(E.PROG))
        c.s = [D(11), D(22), D(33), D(44)]; c.lastx = D(77); c.pix = []; c.keys = list(keys); c.steps = 0
        c.frames = E._Frames(c); c.reg.update(user)
        c.run('ELEM47')
        want = [D(11), D(22), D(33), D(44)] if top is None else [top, D(11), D(22), D(33)]
        regs = all(c.reg.get(k) == v for k, v in user.items() if not 20 <= int(k) <= 56)
        work = all(c.reg.get(str(k), D(0)) in (D(0), '') for k in range(20, 57))
        check(c.s == want and c.lastx == D(77) and regs and work and not c.keys,
              'the end, %s: stack %s, LASTx %s, R20-R56 cleared, the user\'s registers kept'
              % (what, ' '.join(str(v) for v in c.s), c.lastx))
    print('\n%s' % ('ALL OK' if not fails else '%d FAILED' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
