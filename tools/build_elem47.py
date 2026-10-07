#!/usr/bin/env python3
"""Build the ELEM47 files from the commented source programs_rem/ELEM47.txt.

One program, one global label: LBL "ELEM47". Everything else is local to it:
  - the code labels are written by name in the source, as the C47 shows local named labels:
    LBL :PANEL:, XEQ :PANEL:, GTO :KEYS: (at most 7 characters, letters and digits)
  - the data labels stay numeric (they are reached with XEQ IND): LBL 29 the segments of the table,
    LBL 36-37 the symbols (65 elements each: a digit, the column of the symbol in its cell, then the
    symbol in 2 characters), LBL 60-89 the element records, 4 elements each,
    "name/mass/state letter/boiling point/configuration" joined by "/" (15 fields).
The DATA part at the end of programs_rem/ELEM47.txt is written from python/elements.py.

The named labels go to the calculator file as they are: rejig (0.30.0 and later) reads LBL :NAME: as a
local named label (byte 249 in the .p47, the global labels are 253: checked with a test program keyed in
on the C47, Oct 7, 2026). A second file keeps the old way, each name a free local number 00-99, in case
the C47 or an older rejig refuses the named ones; listings/ELEM47_labels.txt says which number is which.

Files written:
  programs/ELEM47.txt        the program without REM lines (to convert with rejig)
  build/ELEM47.txt           the calculator file (the same steps), local named labels
  build/ELEM47_num.txt       the same program with numeric local labels (the fallback)
  listings/ELEM47_doc.txt    numbered steps with the comments (step numbers = lines of programs/)
  listings/ELEM47_labels.txt the local labels: name, number, what it does
  python3 tools/build_elem47.py"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'python'))
from elements import ELEMENTS, EXTRA, SEGMENTS

NAME = 'ELEM47'
MARK = 'REM ==== DATA'
SYM0, SYMS = 36, 65  # the symbol pieces: LBL 36, 37; 65 elements (195 characters) each
REC0, PER = 60, 4    # the element records: LBL 60-89, 4 elements each (172 characters at most)
MAXSTR = 196         # the longest text the C47 keeps in one string (MAX_NUMBER_OF_GLYPHS_IN_STRING of the
                     # firmware); 69 checked on the C47 so far: tests/calc/LTEST.txt checks 196
NAMED_RE = re.compile(r'(LBL|GTO|XEQ) :([A-Za-z0-9]{1,7}):$')


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
        elif NAMED_RE.match(s):
            b += 3 + len(s.split(':')[1])      # command, 249, length, the name (bytes of the test program)
        else:
            b += 2.3
    return int(round(b))


def record(z):
    """The text of element z: name/mass/state/boiling point/configuration; the state as one letter
    (S L G -, the order of "SLG-" in ELEM47), the boiling point without " K" (ELEM47 adds it)."""
    sym, name, mass = ELEMENTS[z - 1]
    state, boil, cfg = EXTRA[z - 1]
    letter = {'Solid': 'S', 'Liquid': 'L', 'Gas': 'G', '-': '-'}[state]
    return '/'.join((name, mass, letter, boil[:-2] if boil.endswith(' K') else boil, cfg))


def data():
    out = ['LBL 29', 'REM the segments: count, row, first column (in the order of Z)']
    for z0, n, r, c in SEGMENTS:
        out += [str(n), str(r), str(c), 'XEQ :SEGMENT:']
    out.append('RTN')
    sym = ''.join(str(offset(s)) + (s + ' ')[:2] for s, _, _ in ELEMENTS)
    out.append('REM the symbols: %d elements per label' % SYMS)
    for k in range((len(ELEMENTS) + SYMS - 1) // SYMS):
        out += ['LBL %02d' % (SYM0 + k), '"%s"' % sym[3 * SYMS * k:3 * SYMS * (k + 1)], 'RTN']
    out.append('REM the records of Z (%d per label): LBL %d + (Z-1) div %d, then (Z-1) mod %d records of 5 fields'
               % (PER, REC0, PER, PER))
    for k in range((len(ELEMENTS) + PER - 1) // PER):
        recs = [record(z) for z in range(PER * k + 1, min(PER * k + PER, len(ELEMENTS)) + 1)]
        out += ['LBL %02d' % (REC0 + k), '"%s"' % '/'.join(recs), 'RTN']
    out.append('END')
    long = [s for s in out if s.startswith('"') and len(s) - 2 > MAXSTR]
    if long:
        raise SystemExit('text longer than %d characters: %s' % (MAXSTR, long))
    return out


def resolve(steps):
    """The steps with each named label replaced by a free local number (the fallback file), and the
    numbers. Stops on a name defined twice, a name used but not defined, more labels than 00-99."""
    defs = [m.group(2) for s in steps for m in [NAMED_RE.match(s)] if m and m.group(1) == 'LBL']
    dup = sorted({d for d in defs if defs.count(d) > 1})
    if dup:
        raise SystemExit('named labels defined twice: %s' % ', '.join(dup))
    used = {m.group(2) for s in steps for m in [NAMED_RE.match(s)] if m}
    if used - set(defs):
        raise SystemExit('named labels used but not defined: %s' % ', '.join(sorted(used - set(defs))))
    bad = [s for s in steps if re.match(r'(LBL|GTO|XEQ) :', s) and not NAMED_RE.match(s)]
    if bad:
        raise SystemExit('a named label is 1-7 letters or digits between colons: %s' % bad[:3])
    taken = {int(m.group(1)) for s in steps for m in [re.fullmatch(r'LBL (\d\d)', s)] if m}
    free = [n for n in range(100) if n not in taken]
    if len(defs) > len(free):
        raise SystemExit('%d named labels, only %d local numbers free' % (len(defs), len(free)))
    num = dict(zip(defs, free))
    return [NAMED_RE.sub(lambda m: '%s %02d' % (m.group(1), num[m.group(2)]), s) for s in steps], num


def labels_text(lines, num):
    """listings/ELEM47_labels.txt: each named label, its number in this build, and the first comment
    line above it."""
    out = ['ELEM47 local labels: name (build/ELEM47.txt), number (build/ELEM47_num.txt), what it does', '']
    for i, ln in enumerate(lines):
        m = NAMED_RE.match(ln)
        if m and m.group(1) == 'LBL':
            j = i
            while j > 0 and lines[j - 1].startswith('REM'):
                j -= 1
            note = lines[j][3:].strip(' -') if j < i else ''
            note = re.sub(r'^(LBL )?:%s:\s*' % m.group(2), '', note)
            out.append(':%s:%s %s  %s' % (m.group(2), ' ' * (8 - len(m.group(2))),
                                          '%02d' % num[m.group(2)], note[:90]))
    out += ['', 'Numeric data labels (XEQ IND): 29 the segments, %d-%d the symbols, %d-%d the records.' % (
        SYM0, SYM0 + (len(ELEMENTS) - 1) // SYMS, REC0, REC0 + (len(ELEMENTS) - 1) // PER)]
    return '\n'.join(out) + '\n'


def build():
    src = os.path.join(ROOT, 'programs_rem', NAME + '.txt')
    lines = [ln.rstrip() for ln in open(src, encoding='utf-8')]
    k = next(i for i, ln in enumerate(lines) if ln.startswith(MARK))
    lines = lines[:k + 1] + data()
    r = lines.index('LBL :RECORD:')
    if lines[r + 4:r + 6] != ['STO 24', str(PER)] or lines[r + 14:r + 15] != [str(PER)]:
        raise SystemExit('LBL :RECORD: must divide by PER = %d (the records per label)' % PER)
    with open(src, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    steps = [ln for ln in lines if ln.strip() and not ln.startswith('REM')]
    numeric, num = resolve(steps)
    if sum(1 for s in steps if s.startswith('LBL "')) != 1 or steps.count('END') != 1:
        raise SystemExit('ELEM47 is one program with one global label')
    nums = [s for s in numeric if re.fullmatch(r'LBL \d\d', s)]
    dup = sorted({t for t in nums if nums.count(t) > 1})
    if dup:
        raise SystemExit('labels used twice: %s' % ', '.join(dup))
    listing, n = [], 0
    for ln in lines:
        if not ln.strip():
            continue
        if ln.startswith('REM'):
            listing.append('      ; ' + ln[3:].strip())
        else:
            listing.append('%4d  %s' % (n + 1, steps[n] + ('' if numeric[n] == ln else '    (%s)' % numeric[n].split(' ', 1)[1])))
            n += 1
    plain = '\n'.join(steps) + '\n'
    for d in ('programs', 'build'):
        with open(os.path.join(ROOT, d, NAME + '.txt'), 'w', encoding='utf-8') as fh:
            fh.write(plain)
    with open(os.path.join(ROOT, 'build', NAME + '_num.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(numeric) + '\n')
    with open(os.path.join(ROOT, 'listings', NAME + '_doc.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(listing) + '\n')
    with open(os.path.join(ROOT, 'listings', NAME + '_labels.txt'), 'w', encoding='utf-8') as fh:
        fh.write(labels_text(lines, num))
    return steps, num


def label_numbers():
    """name -> number of the named labels in build/ELEM47_num.txt (for the tests)."""
    lines = [ln.rstrip() for ln in open(os.path.join(ROOT, 'programs_rem', NAME + '.txt'), encoding='utf-8')]
    return resolve([ln for ln in lines if ln.strip() and not ln.startswith('REM')])[1]


if __name__ == '__main__':
    st, num = build()
    txt = [s for s in st if s.startswith('"')]
    print('%-8s %5d steps, labels: 1 global, %d local named, %d numeric (data)  %5d text characters, longest %d  about %5d bytes (.p47, estimated)' % (
        NAME, len(st), len(num), sum(1 for s in st if re.fullmatch(r'LBL \d\d', s)), sum(len(s) - 2 for s in txt),
        max(len(s) - 2 for s in txt), estimate(st)))
