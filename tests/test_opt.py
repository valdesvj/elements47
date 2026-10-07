#!/usr/bin/env python3
"""ELEM47 (this branch) against the reference build of another branch (default optimize), as Almanac 47's
test_v2: the same screens pixel for pixel for many key sequences, the same data for every element
(LBL 30 / the detail box), the same end state, and the step counts of both.
  python3 tests/test_opt.py [REF]     REF: a git branch or commit (default optimize; prototype-h no longer
  matches since c47sim stores the αLEFT result as the firmware does)"""
import os, subprocess, sys, tempfile
from decimal import Decimal as D
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python')]
import c47sim, elem47sim as E
from elements import ELEMENTS, position
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from build_elem47 import label_numbers                                  # noqa: E402
NUM = label_numbers()

REF = sys.argv[1] if len(sys.argv) > 1 else 'optimize'
fails = []
REF_REG = E.REG_V1 if REF == 'prototype-h' else E.REG     # the registers of the reference build


def check(ok, msg):
    print(('ok    ' if ok else 'FAIL  ') + msg)
    if not ok:
        fails.append(msg)


def ref_file():
    txt = subprocess.run(['git', '-C', ROOT, 'show', '%s:build/ELEM47.txt' % REF], capture_output=True, text=True,
                         check=True).stdout
    fn = os.path.join(tempfile.mkdtemp(prefix='elem47ref_'), 'ELEM47.txt')
    open(fn, 'w', encoding='utf-8').write(txt)
    return fn


R, L, U, Dn, I, END = E.RIGHT, E.LEFT, E.UP, E.DOWN, E.INFO, E.END
RUNS = {
    'tour': [R] + [Dn] * 8 + [L] * 17 + [U] * 8 + [R, R, I, 1] + [Dn] * 4 + [I, 1, END],
    'gaps': [Dn] * 5 + [R, R, R, Dn, Dn, U, U, U, L, L, L, I, 9, END],
    'f-block': [Dn] * 4 + [R, R, Dn, Dn] + [R] * 14 + [I, 1, U, U, I, 2, END],
    'edges': [U, L, I, 1, Dn] * 2 + [R] * 20 + [Dn] * 10 + [I, 3, END],
    'other keys': [1, 2, 3, R, 42, I, 7, END],
}


def run(prog, keys):
    shots, c = E.frames(keys, prog)
    return shots, c


def main():
    ref = ref_file()
    tot = {}
    for name, keys in RUNS.items():
        a, ca = run(ref, keys)
        b, cb = run(E.PROG, keys)
        same = len(a) == len(b) and all(x == y for x, y in zip(a, b))
        bad = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
        check(same, '%-11s %2d screens the same as %s%s' % (name, len(b), REF, '' if same else ' (first difference: screen %s)' % bad))
        check(cb.keys == [] and getattr(cb, 'grfnt', 20) == 20 and getattr(cb, 'grmod', 0) == 0 and 'PT' not in cb.mats,
              '%-11s the end: GRFNT 20, GRMOD 0, PT deleted' % name)
        tot[name] = (ca.steps, cb.steps)
    # the end (key 0): R00-R99 and the stack cleared (CLREGS, CLSTK), whatever was there before
    mine = {str(i): D(1000 + i) for i in range(100)}
    b, cb = E.frames([R, Dn, I, 1, END], E.PROG, regs=dict(mine))
    left = [k for k in mine if cb.reg.get(k, D(0)) != 0]
    check(not left and all(v == 0 for v in cb.s), 'the end: R00-R99 and the stack cleared %s' % (sorted(left, key=int)[:8] or ''))
    # every element: the panel and the detail box through the program itself (cursor placed on it)
    a, ca = run(ref, [I])
    b, cb = run(E.PROG, [I])
    wrong = []
    for z in range(1, 119):
        r, col = position(z)
        outs = []
        for c, g, lab in ((ca, REF_REG, ('0_26', '0_45')), (cb, E.REG, tuple('0_%02d' % NUM[k] for k in ('PANEL', 'DETAIL')))):
            c.s = [D(0)] * 4; c.pix = []
            c.reg.update({g['Z']: D(z), g['ROW']: D(r), g['COL']: D(col)})
            c.run(lab[0]); c.run(lab[1])
            outs.append(frozenset(c.pix))
        if outs[0] != outs[1]:
            wrong.append(ELEMENTS[z - 1][0])
    check(not wrong, 'panel and detail box of the 118 elements the same as %s %s' % (REF, wrong[:5] or ''))
    print('\nsteps run (%s -> this branch):' % REF)
    for name, (x, y) in tot.items():
        print('  %-11s %7d -> %7d  (%+.1f %%)' % (name, x, y, 100.0 * (y - x) / x))
    a1, c1 = run(ref, []); b1, c2 = run(E.PROG, [])
    print('  %-11s %7d -> %7d  (%+.1f %%)' % ('table', c1.steps, c2.steps, 100.0 * (c2.steps - c1.steps) / c1.steps))
    print('\n%s' % ('ALL OK' if not fails else '%d FAILED' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
