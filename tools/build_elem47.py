#!/usr/bin/env python3
"""Build the ELEM47 files from the commented source programs_rem/ELEM47.txt:
  - the DATA part at the end of programs_rem/ELEM47.txt is written from python/elements.py:
    LBL 29 the segments of the table, LBL 36-41 the symbols (20 elements each: a digit, the column
    of the symbol in its cell, then the symbol in 2 characters); then two data programs, ELD1 (Z 1-60)
    and ELD2 (Z 61-118), one label per element: "state/mass/boiling point/name/configuration"
  One file holds the three programs (ELEM47, ELD1, ELD2), each ending with END.
  programs/ELEM47.txt        the program without REM lines (to convert with rejig)
  build/ELEM47.txt           the calculator file (the same steps for now)
  listings/ELEM47_doc.txt    numbered steps with the comments (step numbers = lines of programs/)
  python3 tools/build_elem47.py"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'python'))
from elements import ELEMENTS, EXTRA, SEGMENTS

NAME = 'ELEM47'
MARK = 'REM ==== DATA'
MAXSTR = 64          # the longest text literal used so far on the C47 (Almanac 47: 69)


def offset(sym):
    """The column of the symbol in its cell (from the left edge), so that it is centred in the 21 inner
    columns: GRFNT 21 = the standardFont with one column less per character."""
    from stdfont import STD, code
    x, lo, hi = 0, None, 0
    for ch in sym:
        cb, cg, ca = STD[code(ch)][:3]
        if cg:
            lo = x + cb if lo is None else lo
            hi = x + cb + cg
        x += cb + cg + ca - 1
    o = 1 + (21 - (hi - lo)) // 2 - lo
    assert 0 <= o <= 9 and hi - lo <= 21, sym
    return o


def record(z):
    """The text of element z in ELD1 / ELD2: state/mass/boiling point/name/configuration."""
    sym, name, mass = ELEMENTS[z - 1]
    state, boil, cfg = EXTRA[z - 1]
    return '/'.join((state, mass, boil, name, cfg))


def data():
    out = ['LBL 29', 'REM the segments: count, row, first column (in the order of Z)']
    for z0, n, r, c in SEGMENTS:
        out += [str(n), str(r), str(c), 'XEQ 21']
    out.append('RTN')
    sym = ''.join(str(offset(s)) + (s + ' ')[:2] for s, _, _ in ELEMENTS)
    for k in range(6):
        out += ['LBL %d' % (36 + k), '"%s"' % sym[60 * k:60 * k + 60], 'RTN']
    out.append('END')
    # the data programs: XEQ "ELD1" (Z 1-60) or "ELD2" (Z 61-118) with Z in R36 returns the text in X
    for name, z0, z1 in (('ELD1', 1, 60), ('ELD2', 61, 118)):
        out += ['REM ---- %s: the text "state/mass/boiling point/name/configuration" of Z = R36 (%d-%d) ----' % (name, z0, z1),
                'LBL "%s"' % name, 'RCL 36']
        if z0 > 1:
            out += [str(z0 - 1), '-']
        out += ['STO 49', 'XEQ IND 49', 'RTN']
        for z in range(z0, z1 + 1):
            out += ['LBL %02d' % (z - z0 + 1), '"%s"' % record(z), 'RTN']
        out.append('END')
    long = [s for s in out if s.startswith('"') and len(s) - 2 > MAXSTR]
    if long:
        raise SystemExit('text longer than %d characters: %s' % (MAXSTR, long))
    return out


def build():
    src = os.path.join(ROOT, 'programs_rem', NAME + '.txt')
    lines = [ln.rstrip() for ln in open(src, encoding='utf-8')]
    k = next(i for i, ln in enumerate(lines) if ln.startswith(MARK))
    lines = lines[:k + 1] + data()
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
    prog = []
    for s in steps:                                  # local labels: once in each program (END ends one)
        if s == 'END':
            labels = [t for t in prog if re.fullmatch(r'LBL \d\d', t)]
            dup = sorted({t for t in labels if labels.count(t) > 1})
            if dup:
                raise SystemExit('labels used twice: %s' % ', '.join(dup))
            prog = []
        else:
            prog.append(s)
    plain = '\n'.join(steps) + '\n'
    for d in ('programs', 'build'):
        with open(os.path.join(ROOT, d, NAME + '.txt'), 'w', encoding='utf-8') as fh:
            fh.write(plain)
    with open(os.path.join(ROOT, 'listings', NAME + '_doc.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(listing) + '\n')
    return steps


if __name__ == '__main__':
    st = build()
    txt = [s for s in st if s.startswith('"')]
    print('%s: %d steps, %d text literals (%d characters, longest %d)' % (
        NAME, len(st), len(txt), sum(len(s) - 2 for s in txt), max(len(s) - 2 for s in txt)))
