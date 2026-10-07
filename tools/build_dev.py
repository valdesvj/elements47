#!/usr/bin/env python3
"""Build the development programs, kept apart from the release (ELEM47, tools/build_elem47.py).

  programs_rem/dev/NAME.txt   the commented source
  build/dev/NAME.txt          the program without REM lines (to convert with rejig)
  listings/dev/NAME_doc.txt   numbered steps with the comments

ELEM47P, the prototype of branch prototype-cells: the full table from a vector of x + iy, one
subroutine per job, the cells under the info box drawn again when it closes. Its DATA part (after
REM ==== DATA) is written here from python/elements.py: two data programs, ELP1 (Z 1-60) and ELP2
(Z 61-118), one label per element: the symbol, then the 3 lines of the info box.
  python3 tools/build_dev.py"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools')]
from elements import ELEMENTS, EXTRA                                    # noqa: E402
from build_elem47 import MARK, MAXSTR, estimate                         # noqa: E402

DEV = ('ELEM47P',)


def data_p():
    """The DATA part of ELEM47P: XEQ "ELP1" (Z 1-60) or "ELP2" (Z 61-118) with Z in R25 returns
    Y = the symbol and X = the text of the info box (3 lines, separated by the CR glyph)."""
    out = []
    for name, z0, z1 in (('ELP1', 1, 60), ('ELP2', 61, 118)):
        out += ['REM ---- %s: the symbol and the info box text of Z = R25 (%d-%d), label = Z%s ----' % (
                    name, z0, z1, ' - %d' % (z0 - 1) if z0 > 1 else ''),
                'LBL "%s"' % name, 'RCL 25']
        if z0 > 1:
            out += [str(z0 - 1), '-']
        out += ['STO 27', 'CLSTK', 'XEQ IND 27', 'RTN']
        for z in range(z0, z1 + 1):
            sym, nm, mass = ELEMENTS[z - 1]
            state, boil, cfg = EXTRA[z - 1]
            out += ['LBL %02d' % (z - z0 + 1), '"%s"' % sym,
                    '"%d  %s  %s↵%s  %s  %s↵%s"' % (z, sym, nm, mass, state, boil, cfg), 'RTN']
        out.append('END')
    long = [s for s in out if s.startswith('"') and len(s) - 2 > MAXSTR]
    if long:
        raise SystemExit('text longer than %d characters: %s' % (MAXSTR, long))
    return out


def build(name):
    src = os.path.join(ROOT, 'programs_rem', 'dev', name + '.txt')
    lines = [ln.rstrip() for ln in open(src, encoding='utf-8')]
    k = next((i for i, ln in enumerate(lines) if ln.startswith(MARK)), None)
    if k is not None and name == 'ELEM47P':
        lines = lines[:k + 1] + data_p()
        with open(src, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines) + '\n')
    steps, listing = [], []
    for ln in lines:
        if not ln.strip():
            continue
        if ln.startswith('REM'):
            listing.append('      ; ' + ln[3:].strip())
        else:
            steps.append(ln)
            listing.append('%4d  %s' % (len(steps), ln))
    with open(os.path.join(ROOT, 'build', 'dev', name + '.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(steps) + '\n')
    with open(os.path.join(ROOT, 'listings', 'dev', name + '_doc.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(listing) + '\n')
    return steps


if __name__ == '__main__':
    for name in DEV:
        st = build(name)
        progs, cur = [], []
        for s in st:
            cur.append(s)
            if s == 'END':
                progs.append(cur); cur = []
        for p in progs:
            print('%-8s %5d steps  about %5d bytes' % (p[0][5:-1], len(p), estimate(p)))
        print('%-8s %5d steps in build/dev/%s.txt' % (name, len(st), name))
