#!/usr/bin/env python3
"""Build the ELEM47 files from the commented source programs_rem/ELEM47.txt:
  - the DATA part at the end of programs_rem/ELEM47.txt is written from python/elements.py:
    LBL 29 the segments of the table, LBL 36-41 the symbols (20 elements each: a digit, the column
    of the symbol in its cell, then the symbol in 2 characters); then two data programs, ELD1 (Z 1-60)
    and ELD2 (Z 61-118), one label per element: "name/mass/state letter/boiling point/configuration"
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
REG_Z, REG_IND = 30, 43    # ELEM47's registers: Z of the cursor, the label for XEQ IND
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


def estimate(steps):
    """Estimated .p47 bytes of a program: 2.3 bytes per command, 2 + its characters per number and
    per binary number, 2 + its UTF-8 bytes per text. Calibrated on Almanac 47's MOON47 (4 836 bytes) and
    NAVFULL (24 160 bytes), within 3 % of both; rejig gives the real size."""
    b = 0.0
    for s in steps:
        if s.startswith('"'):
            b += 2 + len(s.encode('utf-8')) - 2
        elif re.fullmatch(r'-?[\d.]+(E-?\d+)?|[01]+#2', s):
            b += 2 + len(s)
        else:
            b += 2.3
    return int(round(b))


def record(z):
    """The text of element z in ELD1 / ELD2: name/mass/state/boiling point/configuration; the state as
    one letter (S L G -, the order of "SLG-" in ELEM47), the boiling point without " K" (ELEM47 adds it)."""
    sym, name, mass = ELEMENTS[z - 1]
    state, boil, cfg = EXTRA[z - 1]
    letter = {'Solid': 'S', 'Liquid': 'L', 'Gas': 'G', '-': '-'}[state]
    return '/'.join((name, mass, letter, boil[:-2] if boil.endswith(' K') else boil, cfg))


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
        out += ['REM ---- %s: the text "name/mass/state/boiling point/configuration" of Z = R36 (%d-%d) ----' % (name, z0, z1),
                'LBL "%s"' % name, 'RCL %02d' % REG_Z]
        if z0 > 1:
            out += [str(z0 - 1), '-']
        out += ['STO %02d' % REG_IND, 'XEQ IND %02d' % REG_IND, 'RTN']
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
    progs, cur = [], []
    for s in st:
        cur.append(s)
        if s == 'END':
            progs.append(cur); cur = []
    total = 0
    for p in progs:
        txt = [s for s in p if s.startswith('"')]
        n = estimate(p); total += n
        print('%-8s %5d steps %3d labels %5d text characters  about %5d bytes' % (
            p[0][5:-1], len(p), sum(1 for s in p if re.fullmatch(r'LBL \d\d', s)), sum(len(s) - 2 for s in txt), n))
    print('%-8s %5d steps %35s about %5d bytes (.p47, estimated)' % ('file', len(st), '', total))
