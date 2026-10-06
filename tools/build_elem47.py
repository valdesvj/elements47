#!/usr/bin/env python3
"""Build the ELEM47 files from the commented source programs_rem/ELEM47.txt:
  - the DATA part at the end of programs_rem/ELEM47.txt is written from python/elements.py:
    LBL 29 the segments of the table, LBL 36-41 the symbols (20 elements each: a digit, the column
    of the symbol in its cell, then the symbol in 2 characters), LBL 60-99 "mass name/mass name/mass name" (three elements each)
  programs/ELEM47.txt        the program without REM lines (to convert with rejig)
  build/ELEM47.txt           the calculator file (the same steps for now)
  listings/ELEM47_doc.txt    numbered steps with the comments (step numbers = lines of programs/)
  python3 tools/build_elem47.py"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'python'))
from elements import ELEMENTS, SEGMENTS

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


def data():
    out = ['LBL 29', 'REM the segments: count, row, first column (in the order of Z)']
    for z0, n, r, c in SEGMENTS:
        out += [str(n), str(r), str(c), 'XEQ 21']
    out.append('RTN')
    sym = ''.join(str(offset(s)) + (s + ' ')[:2] for s, _, _ in ELEMENTS)
    for k in range(6):
        out += ['LBL %d' % (36 + k), '"%s"' % sym[60 * k:60 * k + 60], 'RTN']
    for k in range(40):
        out += ['LBL %d' % (60 + k), '"%s"' % '/'.join('%s %s' % (m, n) for _, n, m in ELEMENTS[3 * k:3 * k + 3]), 'RTN']
    long = [s for s in out if s.startswith('"') and len(s) - 2 > MAXSTR]
    if long:
        raise SystemExit('text longer than %d characters: %s' % (MAXSTR, long))
    return out + ['END']


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
    labels = [s for s in steps if re.fullmatch(r'LBL \d\d', s)]
    dup = sorted({s for s in labels if labels.count(s) > 1})
    if dup:
        raise SystemExit('labels used twice: %s' % ', '.join(dup))
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
