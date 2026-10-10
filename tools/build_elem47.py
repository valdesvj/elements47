#!/usr/bin/env python3
"""Build the ELEM47 files from the commented source programs_rem/ELEM47.txt.

Three programs, three global labels:
  ELEM47  the code. Its labels are written by name in the source (LBL :PANEL:, XEQ :PANEL:, GTO :KEYS:,
          1-7 letters and digits); the build gives each name a free local number 00-99 (the calculator
          files have numeric local labels only; listings/ELEM47_labels.txt says which number is which): the
          data labels 00-01 first, then the names in order, no gaps.
          The segments of the table (count, row, first column) are written into LBL :CELLS:, after the
          line SEG_MARK. Its data labels stay numeric (reached with XEQ IND): LBL 00-01 the symbols (65 elements each: the symbol in 2 characters, then a digit, the column of
          the symbol in its cell).
          Branch struct (C47 only): the code is written with the C47 STRUCT commands (app note AN0007 of the
          firmware: IF / ELSE / ENDIF, DO / WHILE / ENDDO, REPEAT / UNTIL), indented in the source (two spaces
          per level), without numbers: the build checks the structures as VALID does and gives the partner
          numbers (IF, DO and REPEAT in three series, from 01, in the order the openers appear), as rejig
          writes them (IF 01). The build/ELEM47.txt file holds three programs and the C47 checks only the
          last one as it loads, so the numbers must be in the file.
  ELD1    the element records of Z 1-60: LBL 00-14; ELD2 those of Z 61-118: LBL 15-29. 4 elements per
  ELD2    label, each one "name/mass/state letter/boiling point/configuration|" (the fields joined by "/",
          "|" after each record).
          XEQ "ELD1" (or "ELD2") with R43 the label: XEQ IND 43 there.
The DATA part at the end of programs_rem/ELEM47.txt (from the end of ELEM47) is written from
python/elements.py.

Files written:
  programs/ELEM47.txt        the three programs without REM lines, numeric labels (to convert with rejig)
  build/ELEM47.txt           the calculator file (the same steps)
  listings/ELEM47_doc.txt    numbered steps with the comments and the label names
  listings/ELEM47_labels.txt the local labels of ELEM47: name, number, what it does
  python3 tools/build_elem47.py"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'python'))
from elements import ELEMENTS, EXTRA, SEGMENTS

NAME = 'ELEM47'
MARK = 'REM ==== DATA'
SEG_MARK = 'REM ==== SEGMENTS'
SYM0, SYMS = 0, 65   # the symbol pieces: LBL 00, 01; 65 elements (195 characters) each
REC0, PER = 0, 4     # the element records: LBL 00-29, 4 elements each (176 characters at most)
SPLIT = 60           # ELD1: Z 1-60 (LBL 00-14), ELD2: Z 61-118 (LBL 15-29)
DATA = ('ELD1', 'ELD2')    # the names of the two record programs (global labels)
MAXSTR = 196         # the longest text the C47 keeps in one string (MAX_NUMBER_OF_GLYPHS_IN_STRING of the
                     # firmware); 69 checked on the C47 so far: tests/calc/LTEST.txt checks 196
NAMED_RE = re.compile(r'(LBL|GTO|XEQ) :([A-Za-z0-9]{1,7}):$')
# the C47 STRUCT commands (AN0007): the openers, the closers, and the series of the partner numbers
OPENERS = {'IF': 'ENDIF', 'DO': 'ENDDO', 'REPEAT': 'UNTIL'}
STRUCT = ('IF', 'ELSE', 'ENDIF', 'DO', 'WHILE', 'ENDDO', 'REPEAT', 'UNTIL')
NOT_USED = ('FOR', 'NEXT', 'FORₓ', 'NEXTₓ', 'FOR𝑦ˣ', 'FORᵀᴼᴾ')       # FOR takes its three values off the stack


def is_test(step):
    """A step that leaves a test answer (the firmware's structTest list: the comparisons, the flag and type
    tests ending with ?, the counters, KEY?)."""
    op = step.split(' ')[0]
    return op.endswith('?') or op in ('DSE', 'ISG', 'DSZ', 'ISZ', 'DSL', 'ISE')


def structures(steps):
    """The steps with the partner numbers of the STRUCT commands, as VALID numbers them (manage.c /
    structured.c structWalkProgram): per program, IF, DO and REPEAT in three series from 1, in the order
    the openers appear; ELSE, WHILE, ENDDO, ENDIF, UNTIL take the number of their opener. Stops on what
    VALID refuses (a closer without its opener or of another kind, a structure left open at END or across
    a routine (RTN then LBL), a DO without WHILE, an IF / WHILE / UNTIL without a test just before it) and
    on a test before ELSE, ENDIF, DO, ENDDO, REPEAT or UNTIL: the firmware never skips those (structured.c
    structNoLegacySkip)."""
    out, open_, n = [], [], {}

    def fail(i, msg):
        raise SystemExit('STRUCT, step %d (%s): %s' % (i + 1, steps[i], msg))
    for i, s in enumerate(steps):
        op = s.split(' ')[0]
        prev = steps[i - 1] if i else ''
        if op in NOT_USED:
            fail(i, 'FOR / NEXT not used here (they take the start, end and step off the stack)')
        if op in STRUCT and s != op:
            fail(i, 'written without a number: the build numbers the structures')
        if op in ('IF', 'WHILE', 'UNTIL') and not is_test(prev):
            fail(i, 'no test just before it')
        if op in ('ELSE', 'ENDIF', 'DO', 'ENDDO', 'REPEAT', 'UNTIL') and is_test(prev) and not op == 'UNTIL':
            fail(i, 'a test before it: the firmware never skips a structure step')
        if s == 'END' or (s.startswith('LBL ') and prev == 'RTN'):
            if open_:
                fail(i, 'structure %s %02d still open' % tuple(open_[-1][:2]))
            if s == 'END':
                n = {}
        if op in OPENERS:
            n[op] = n.get(op, 0) + 1
            open_.append([op, n[op], False])
            out.append('%s %02d' % (op, n[op]))
            continue
        if op in STRUCT:
            want = {'ELSE': 'IF', 'ENDIF': 'IF', 'WHILE': 'DO', 'ENDDO': 'DO', 'UNTIL': 'REPEAT'}[op]
            if not open_ or open_[-1][0] != want:
                fail(i, 'no %s open here' % want)
            top = open_[-1]
            if op in ('ELSE', 'WHILE'):
                if top[2]:
                    fail(i, 'a second %s' % op)
                top[2] = True
            if op == 'ENDDO' and not top[2]:
                fail(i, 'a DO without WHILE')
            if op in ('ENDIF', 'ENDDO', 'UNTIL'):
                open_.pop()
            out.append('%s %02d' % (op, top[1]))
            continue
        out.append(s)
    if open_:
        raise SystemExit('STRUCT: %s %02d still open at the end' % tuple(open_[-1][:2]))
    return out


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


def segments():
    """The steps of the segment list in LBL :CELLS: (the RTN after them stays in the source)."""
    out = []
    for z0, n, r, c in SEGMENTS:
        out += [str(n), str(r), str(c), 'XEQ :SEGMENT:']
    return out


def data():
    out = []
    sym = ''.join((s + ' ')[:2] + str(offset(s)) for s, _, _ in ELEMENTS)
    out.append('REM the symbols: %d elements per label' % SYMS)
    for k in range((len(ELEMENTS) + SYMS - 1) // SYMS):
        out += ['LBL %02d' % (SYM0 + k), '"%s"' % sym[3 * SYMS * k:3 * SYMS * (k + 1)], 'RTN']
    out.append('END')
    for name, z0, z1 in ((DATA[0], 1, SPLIT), (DATA[1], SPLIT + 1, len(ELEMENTS))):
        out += ['REM ==== %s: the records of Z %d-%d (%d per label): LBL %d + (Z-1) div %d, then (Z-1) mod %d records'
                ', "|" after each one; R43 the label ====' % (name, z0, z1, PER, REC0, PER, PER),
                'LBL "%s"' % name, 'XEQ IND 43', 'RTN']
        for k in range((z0 - 1) // PER, (z1 + PER - 1) // PER):
            recs = [record(z) for z in range(PER * k + 1, min(PER * k + PER, len(ELEMENTS)) + 1)]
            out += ['LBL %02d' % (REC0 + k), '"%s"' % ''.join(r + '|' for r in recs), 'RTN']
        out.append('END')
    long = [s for s in out if s.startswith('"') and len(s) - 2 > MAXSTR]
    if long:
        raise SystemExit('text longer than %d characters: %s' % (MAXSTR, long))
    return out


def resolve(steps):
    """The steps with each named label replaced by a free local number (the fallback file), and the
    numbers: the numbers 00-99 not taken by a numeric label of the first program (the other programs
    have their own local labels), in order. Stops on a name defined twice, a name used but not defined,
    more labels than 00-99."""
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
    first = steps[:steps.index('END') + 1] if 'END' in steps else steps
    taken = {int(m.group(1)) for s in first for m in [re.fullmatch(r'LBL (\d\d)', s)] if m}
    free = [n for n in range(100) if n not in taken]
    if len(defs) > len(free):
        raise SystemExit('%d named labels, only %d local numbers free' % (len(defs), len(free)))
    num = dict(zip(defs, free))
    return [NAMED_RE.sub(lambda m: '%s %02d' % (m.group(1), num[m.group(2)]), s) for s in steps], num


def labels_text(lines, num):
    """listings/ELEM47_labels.txt: each named label, its number in this build, and the first comment
    line above it."""
    out = ['ELEM47 local labels: name (programs_rem/ELEM47.txt), number (build/ELEM47.txt), what it does', '']
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
    out += ['', 'Numeric data labels (XEQ IND): %02d-%02d the symbols; the records %02d-%02d in %s, '
            '%02d-%02d in %s.' % (SYM0, SYM0 + (len(ELEMENTS) - 1) // SYMS, REC0, REC0 + SPLIT // PER - 1, DATA[0],
                                REC0 + SPLIT // PER, REC0 + (len(ELEMENTS) - 1) // PER, DATA[1])]
    return '\n'.join(out) + '\n'


def build():
    src = os.path.join(ROOT, 'programs_rem', NAME + '.txt')
    lines = [ln.rstrip() for ln in open(src, encoding='utf-8')]
    k = next(i for i, ln in enumerate(lines) if ln.startswith(MARK))
    lines = lines[:k + 1] + data()
    a = next(i for i, ln in enumerate(lines) if ln.startswith(SEG_MARK))
    while lines[a].startswith('REM'):
        a += 1
    b = lines.index('RTN', a)
    lines[a:b] = segments()
    r = lines.index('LBL :RECORD:')
    rec = source_steps(lines[r:])
    rec = ' / ' + ' / '.join(rec[:rec.index('RTN')]) + ' / '

    def has(*seq):
        return ' / ' + ' / '.join(seq) + ' / ' in rec
    if not (has('STO 24', str(PER), '÷') and has('RCL 24', str(PER), 'MOD')
            and has(str(REC0 + SPLIT // PER - 1), 'X<Y?', 'IF', 'XEQ "%s"' % DATA[1], 'ELSE', 'XEQ "%s"' % DATA[0], 'ENDIF')) \
            or REC0 or SYM0 or SPLIT % PER:
        raise SystemExit('LBL :RECORD: must divide by PER = %d, split at LBL %d and call %s, %s (REC0 = SYM0 = 0: '
                         'no + before XEQ IND)' % ((PER, REC0 + SPLIT // PER - 1) + DATA))
    with open(src, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    steps = source_steps(lines)
    numeric, num = resolve(steps)
    numeric = structures(numeric)
    if [s for s in steps if s.startswith('LBL "')] != ['LBL "ELEM47"'] + ['LBL "%s"' % d for d in DATA] \
            or steps.count('END') != 3:
        raise SystemExit('three programs: ELEM47, %s, %s' % DATA)
    for p in programs(numeric):
        nums = [s for s in p if re.fullmatch(r'LBL \d\d', s)]
        dup = sorted({t for t in nums if nums.count(t) > 1})
        if dup:
            raise SystemExit('labels used twice in %s: %s' % (p[0], ', '.join(dup)))
    listing, n = [], 0
    for ln in lines:
        if not ln.strip():
            continue
        ind = ln[:len(ln) - len(ln.lstrip())]
        if ln.lstrip().startswith('REM'):
            listing.append('      ' + ind + '; ' + ln.lstrip()[3:].strip())
        else:
            listing.append('%4d  %s' % (n + 1, ind + steps[n] + ('' if numeric[n] == steps[n] else '    (%s)' % numeric[n].split(' ', 1)[1])))
            n += 1
    plain = '\n'.join(numeric) + '\n'
    for d in ('programs', 'build'):
        with open(os.path.join(ROOT, d, NAME + '.txt'), 'w', encoding='utf-8') as fh:
            fh.write(plain)
    with open(os.path.join(ROOT, 'listings', NAME + '_doc.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(listing) + '\n')
    with open(os.path.join(ROOT, 'listings', NAME + '_labels.txt'), 'w', encoding='utf-8') as fh:
        fh.write(labels_text(lines, num))
    return steps, num


def programs(steps):
    """The programs of a list of steps (each ends with END)."""
    out, cur = [], []
    for s in steps:
        cur.append(s)
        if s == 'END':
            out.append(cur); cur = []
    return out


def label_numbers():
    """name -> number of the named labels of ELEM47 in build/ELEM47.txt (for the tests)."""
    lines = [ln.rstrip() for ln in open(os.path.join(ROOT, 'programs_rem', NAME + '.txt'), encoding='utf-8')]
    return resolve(source_steps(lines))[1]


def source_steps(lines):
    """The steps of the source lines: no REM, no empty lines, the indentation off."""
    return [ln.strip() for ln in lines if ln.strip() and not ln.lstrip().startswith('REM')]


def plain_steps(lines):
    """The steps of build/ELEM47.txt from the source lines: local numbers for the named labels, partner
    numbers for the structures (for the tests)."""
    return structures(resolve(source_steps(lines))[0])


if __name__ == '__main__':
    st, num = build()
    for p in programs(st):
        txt = [s for s in p if s.startswith('"')]
        print('%-8s %5d steps, %2d local labels  %5d text characters, longest %3d  about %5d bytes (.p47, estimated)' % (
            p[0][5:-1], len(p), sum(1 for s in p if re.match(r'LBL (\d\d|:)', s)), sum(len(s) - 2 for s in txt),
            max(len(s) - 2 for s in txt), estimate(p)))
