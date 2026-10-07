#!/usr/bin/env python3
"""build_free42.py - ELEM47 for Free42 on the SwissMicros DM42 / DM42n (stock firmware, Free42 3.3).

The same program as the C47 release (programs_rem/ELEM47.txt), converted step by step, the way
Almanac 47 converts NAV (its tools/build_free42.py):

  screen       3 STO "GrMod": AGRAPH on the whole 400 x 240 screen (row 1 at the top, column 1 at
               the left; the C47 counts rows from the bottom, from 0: C47 row r = Free42 row 240 - r).
  AGRAPH       Free42 draws the ALPHA register, one character = one column of 8 pixels, bit 0 at the
               top. The cells, the cursor and the detail box frame (C47 columns of 24 to 60 bits in a
               register) become bands of 8 rows: E47C (a cell), E47X (the cursor), E47B (any box).
  GRMOD        flags 34 and 35: CF CF = 0 (set the pixels), CF SF = 1 (write the pattern exactly),
               SF SF = 3 (flip). GRMOD 1 text: each character writes its whole box, as the C47 clears it.
  ATEXT Z      XEQ "E47T" (GRFNT 21) or "E47S" (GRFNT 10, the tinyFont): Z the text, Y the row of the
               bottom of the glyph box, X the column, as on the C47 (|X| and |Y|). The glyphs are the C47 fonts
               (python/stdfont.py, tinyfont.py, drawn by python/c47sim.py), one local label each, the
               columns of the glyph box in bands of 8 rows (20 rows: bands at 0, 8 and 12).
  texts        a C47 "..." goes on the stack: XSTR "..."; the CR glyph is character 13 (€0d).
               x→α r: RCL r X<>Y APPEND STO r;  αIP r: CLA AIP ASTO ST X, then the same;
               αSL r: SUBSTR from X;  αLEFT r: SUBSTR 0 to X;  αPOS r: POS;  α→x r: HEAD r C→N.
  keys         PAUSE 50 / KEY? 33 / GTO: GETKEY, STO 33; the key codes of :KEYS: in Free42 codes
               (8 20, 2 30, 4 24, 6 26, 5 25, 0 34).
  registers    LocR: the user's registers saved as RCL "REGS" STO "E47R" (SIZE 52 if smaller) and
               given back at 0 (STO "REGS": the SIZE too).
  labels       the named local labels numbered as in build/ELEM47_num.txt (Free42: 00-99 only).

Files: build/free42/ELEM47.txt (ELEM47, E47T, E47S; paste or rejig to .raw), listings/free42/.
  python3 tools/build_free42.py"""
import os, re, sys
from decimal import Decimal as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools')]
import build_elem47 as B                                                # noqa: E402

OUT = os.path.join(ROOT, 'build', 'free42')
LST = os.path.join(ROOT, 'listings', 'free42')
KEYS = {53: 20, 73: 30, 62: 24, 64: 26, 63: 25, 82: 34}       # C47 KEY? code -> Free42 GETKEY code
GRMOD = {0: ['CF 34', 'CF 35'], 1: ['CF 34', 'SF 35'], 2: ['SF 34', 'CF 35'], 3: ['SF 34', 'SF 35']}


# ------------------------------------------------------------------ ALPHA literals (as Almanac 47)
SPLIT = {33, 45, 60, 62, 92, 124}      # first bytes of the paste aliases (<= >= != -> <- |- \\)
XBYTE = {34}                           # " ends a string: added with XTOA


def alpha_literal(bs):
    """ALPHA = these bytes. A string in a program holds 15 characters (14 after the append marker);
    it may not start with a byte >= 127 (the append marker): CLA and append. Free42 Paste turns
    <= -> != ... into single characters, so the string is split there."""
    out, cur = [], []

    def flush():
        if not cur:
            return
        s = ''.join('€%02x' % b for b in cur)
        if out:
            out.append('├"%s"' % s)
        elif cur[0] >= 127:
            out.extend(['CLA', '├"%s"' % s])
        else:
            out.append('"%s"' % s)
        del cur[:]
    for b in bs:
        if b in XBYTE:
            flush()
            out.extend(([] if out else ['CLA']) + [str(b), 'XTOA'])
            continue
        cur.append(b)
        if b in SPLIT or len(cur) == (14 if out or cur[0] >= 127 else 15):   # 15 characters at most
            flush()
    flush()
    return out


def bands(cols, H, offsets):
    """{column: set of rows from the top (0 = top)} -> [(offset, bytes)] for the bands of 8 rows."""
    w = max(cols) + 1 if cols else 0
    return [(o, [sum(1 << v for v in range(8) if o + v < H and o + v in cols.get(x, ())) for x in range(w)])
            for o in offsets]


# ------------------------------------------------------------------ the fonts (from c47sim)
def glyphs(font, chars):
    """{char: (columns {x: rows from the top}, advance, box width)} for GRFNT font, as c47sim draws."""
    import c47sim
    from stdfont import STD, code as stdcode
    from tinyfont import TINY
    tab = TINY if font == 10 else STD
    LH = tab[0x41][3] + tab[0x41][4] + tab[0x41][5]
    CP = 1 if font == 21 else 0
    out = {}
    for ch in chars:
        cb, cg, ca, ra, rg, rb, rows = tab.get(stdcode(ch), tab[0x3f])
        adv = cb + cg + ca - CP
        c = c47sim.Calc('END')
        c.grfnt, c.grmod, c.pix = font, 0, []
        c.s = [D(100), D(100), D(0), D(0)]
        c.atext(ch)
        cols = {}
        for r, x in c.pix:
            cols.setdefault(x - 100, set()).add(100 + LH - 1 - r)
        assert all(0 <= x < adv + CP for x in cols) and all(0 <= v < LH for s in cols.values() for v in s), ch
        for x in range(adv + CP):
            cols.setdefault(x, set())
        out[ch] = (cols, adv, adv + CP)
    return out, LH


F42CODE = {'↵': 13, '↓': 14, '→': 15, '←': 16, '↑': 94}


def label_of(ch):
    """The local label of a glyph: the Free42 character code - 32 (the arrows 14-16: 94-96)."""
    k = F42CODE.get(ch, ord(ch))
    return k - 32 if k >= 32 else k + 80


def textprog(name, font, chars):
    """E47T / E47S: ATEXT with Z the text, Y the bottom row of the glyph box, X the column."""
    g, LH = glyphs(font, sorted(chars))
    offs = (0, 8, 12) if LH == 20 else (0,)
    L = ['LBL "%s"' % name, 'ABS', 'STO "TX"', 'STO "T0"', 'R↓', 'ABS', 'STO "TL"', 'R↓', 'STO "TS"',
         'LBL 99', str(241 - LH), 'RCL "TL"', '-', 'STO "TB"',
         'LBL 98', 'RCL "TS"', 'LENGTH', 'X=0?', 'RTN', 'HEAD "TS"', 'C→N', '13', 'X=Y?', 'GTO 97',
         'X<>Y', '80', '+', '112', 'MOD', 'STO "TK"', 'XEQ IND "TK"', 'GTO 98',
         'LBL 97', 'RCL "T0"', 'STO "TX"', str(LH), 'STO- "TL"', 'GTO 99']
    # the label: (code + 80) MOD 112 = code - 32, the arrows (14-16) 94-96
    for ch in sorted(g, key=label_of):
        cols, adv, w = g[ch]
        L.append('LBL %02d' % label_of(ch))
        for o, bs in bands(cols, LH, offs):
            L += alpha_literal(bs) + ['RCL "TB"'] + ([str(o), '+'] if o else []) + ['RCL "TX"', '1', '+', 'AGRAPH']
        L += [str(adv), 'STO+ "TX"', 'RTN']
    return L


def boxes():
    """E47B: a box BW columns x BH rows, bottom row BY, left column BX (C47 coordinates), in the mode of
    flags 34 / 35, bands of 8 rows, 44 columns per AGRAPH (Almanac 47's FBX)."""
    return ['LBL "E47B"', '241', 'RCL "BY"', '-', 'RCL "BH"', '-', 'STO "BT"', 'RCL "BH"', 'STO "BR"',
            'LBL 01', 'RCL "BR"', 'X≤0?', 'RTN', '255', 'STO "BB"', '8', 'RCL "BR"', 'X<Y?', 'XEQ 02',
            'RCL "BW"', 'STO "BC"', 'RCL "BX"', '1', '+', 'STO "BK"',
            'LBL 03', 'RCL "BC"', 'X≤0?', 'GTO 04', '44', 'X>Y?', 'X<>Y', 'STO "BN"', 'CLA',
            'LBL 05', 'RCL "BB"', 'XTOA', 'DSE "BN"', 'GTO 05',
            'RCL "BT"', 'RCL "BK"', 'AGRAPH', '44', 'STO+ "BK"', '-44', 'STO+ "BC"', 'GTO 03',
            'LBL 04', '8', 'STO+ "BT"', '-8', 'STO+ "BR"', 'GTO 01',
            'LBL 02', '2', 'RCL "BR"', 'Y↑X', '1', '-', 'STO "BB"', 'RTN']


def fbx(x, y, w, h, mode):
    return GRMOD[mode] + [str(y), 'STO "BY"', str(x), 'STO "BX"', str(w), 'STO "BW"', str(h), 'STO "BH"', 'XEQ "E47B"']


# ------------------------------------------------------------------ ELEM47
def cell_routine():
    """:FCELL: the box of a cell (23 x 26, OR) at R39 (left column), R40 (bottom row): 4 bands."""
    cols = {0: set(range(26)), 22: set(range(26))}
    for x in range(1, 22):
        cols[x] = {0, 25}
    L = ['LBL :FCELL:'] + GRMOD[0] + ['215', 'RCL 40', '-', 'STO "TB"']
    for o, bs in bands(cols, 26, (0, 8, 16, 18)):
        L += alpha_literal(bs) + ['RCL "TB"'] + ([str(o), '+'] if o else []) + ['RCL 39', '1', '+', 'AGRAPH']
    return L + ['RTN']


def cursor_routine():
    """:FCURS: the cursor: the inside of the cell (21 x 24) flipped, from column R39 + 1, row R40 + 1."""
    cols = {x: set(range(24)) for x in range(21)}
    L = ['LBL :FCURS:'] + GRMOD[3] + ['216', 'RCL 40', '-', 'STO "TB"']
    for o, bs in bands(cols, 24, (0, 8, 16)):
        L += alpha_literal(bs) + ['RCL "TB"'] + ([str(o), '+'] if o else []) + ['RCL 39', '2', '+', 'AGRAPH']
    return L + GRMOD[0] + ['RTN']


def replace(L, old, new):
    for i in range(len(L) - len(old) + 1):
        if L[i:i + len(old)] == old:
            return L[:i] + new + L[i + len(old):]
    raise SystemExit('free42: not found: %s' % old[:4])


def text(s):
    return 'XSTR "%s"' % s[1:-1].replace('↵', '€0d')


def main_program(steps):
    S = list(steps)
    # the user's registers: REGS saved (SIZE 52 at least), given back at the end
    i, j = S.index('LocR 32'), S.index('STO R.31')
    S[i:j + 1] = ['RCL "REGS"', 'STO "E47R"', 'DIM?', 'R↓', '52', 'X>Y?', 'SIZE 52', '3', 'STO "GrMod"'] + GRMOD[0]
    i, j = S.index('RCL R.00'), S.index('STO 51', S.index('RCL R.31'))
    S[i:j + 1] = ['RCL "E47R"', 'STO "REGS"', 'CLV "E47R"']
    S = replace(S, ['0', 'GRMOD', '20', 'GRFNT', 'DELITM "PT"'], GRMOD[0] + ['CLV "PT"'])
    S = replace(S, ['CLLCD', 'CLSTK', 'RTN'], ['CLLCD', '0', 'STO "GrMod"', 'CLST', 'CLD', 'RTN'])
    # the patterns of the C47 columns: not needed
    for pat in ('111111111111111111111111#2', '11111111111111111111111111#2', '10000000000000000000000001#2'):
        while pat in S:
            k = S.index(pat)
            assert S[k + 1].startswith('STO '), S[k:k + 2]
            del S[k:k + 2]
    S = [s for s in S if s != 'WSIZE 64']
    # the cell box, the cursor, the detail frame and the header bar
    S = replace(S, ['RCL 40', 'RCL 39', 'AGRAPH 20'] + ['AGRAPH 21'] * 21 + ['AGRAPH 20'], ['XEQ :FCELL:'])
    S = replace(S, ['3', 'GRMOD', 'RCL 40', '1', '+', 'RCL 39', '1', '+'] + ['AGRAPH 23'] * 21 + ['0', 'GRMOD'],
                ['XEQ :FCURS:'])
    i = S.index('111111111111111111111111111111111111111111111111111111111111#2')
    j = S.index('GTO :BOXLINE:')
    assert S[i - 2:i] == ['0', 'GRMOD']
    S[i - 2:j + 1] = fbx(50, 60, 1, 120, 0) + fbx(349, 60, 1, 120, 0) + fbx(51, 60, 298, 1, 0)
    i = S.index('1111111111111111111111#2')
    j = S.index('GTO :HDRBAR:')
    assert S[i - 2:i] == ['3', 'GRMOD'] and S[j + 1:j + 3] == ['0', 'GRMOD']
    S[i - 2:j + 3] = fbx(51, 158, 298, 22, 3) + GRMOD[0]
    # the key waits and the key codes
    for lab in (':KEYS:', ':INFOKEY:'):
        S = replace(S, ['PAUSE 50', 'KEY? 33', 'GTO ' + lab], ['GETKEY', 'STO 33'])
    i, j = S.index('LBL :KEYS:'), S.index('LBL :UP:')
    for k in range(i, j):
        if S[k] == 'X=Y?' and re.fullmatch(r'\d+', S[k - 1]) and int(S[k - 1]) in KEYS:
            S[k - 1] = str(KEYS[int(S[k - 1])])
    # step by step: fonts, GRMOD, texts, the text functions
    out, font = [], 21
    for k, s in enumerate(S):
        nxt = S[k + 1] if k + 1 < len(S) else ''
        if nxt in ('GRFNT', 'GRMOD') and re.fullmatch(r'\d+', s):
            continue
        if s == 'GRFNT':
            font = int(S[k - 1]); continue
        if s == 'GRMOD':
            out += GRMOD[int(S[k - 1])]; continue
        if s == 'XEQ :BOXCLR:':
            font = 21                                   # :BOXCLR: leaves GRFNT 21
        op, _, arg = s.partition(' ')
        if s == 'ATEXT Z':
            out.append('XEQ "E47T"' if font == 21 else 'XEQ "E47S"')
        elif s.startswith('"'):
            out.append(text(s))
        elif op == 'x→α':
            out += ['RCL ' + arg, 'X<>Y', 'APPEND', 'STO ' + arg, 'DROP', 'LASTX']
        elif op == 'αIP':
            out += ['CLA', 'AIP', 'ASTO ST X', 'RCL ' + arg, 'X<>Y', 'APPEND', 'STO ' + arg]
        elif op == 'αSL':
            out += ['RCL ' + arg, 'X<>Y', 'SUBSTR', 'STO ' + arg, 'DROP', 'LASTX']
        elif op == 'αLEFT':
            out += ['RCL ' + arg, 'X<>Y', '0', 'X<>Y', 'SUBSTR']
        elif op == 'αPOS':
            out += ['RCL ' + arg, 'X<>Y', 'POS']
        elif op == 'α→𝑥':
            out += ['HEAD ' + arg, 'C→N']
        elif s == 'CLSTK':
            out.append('CLST')
        elif s == 'CHS':
            out.append('+/-')
        else:
            out.append(s)
    k = next(i for i, s in enumerate(out) if s == 'LBL 29')
    out = out[:k] + cell_routine() + cursor_routine() + out[k:]
    bad = [s for s in out if s.endswith('#2') or s.split(' ')[0] in (
        'GRMOD', 'GRFNT', 'ATEXT', 'KEY?', 'PAUSE', 'LocR', 'WSIZE', 'x→α', 'αIP', 'αSL', 'αLEFT', 'αPOS',
        'α→𝑥', 'DELITM', 'CLSTK', 'CHS') or s.startswith('AGRAPH ') or 'R.' in s]
    if bad:
        raise SystemExit('free42: C47 steps left: %s' % bad[:5])
    return out


def chars_used(steps):
    """The characters each font draws: every text of the program and the data (records, symbols)."""
    from elements import ELEMENTS, EXTRA
    big = set('0123456789 -/.K')
    for s in steps:
        if s.startswith('"'):
            big |= set(s[1:-1])
    for e in ELEMENTS + EXTRA:
        big |= set(''.join(map(str, e)))
    big |= set('Solid Liquid Gas')
    big -= set('↵/↑←→↓')
    tiny = set('0123456789 ') | set('ANY KEY: BACK') | set('   8↵5 4 6↵   2↵   0      ↑↵INFO ← →↵      ↓↵     END') - {'↵'}
    return big, tiny


def build():
    lines = [ln.rstrip() for ln in open(os.path.join(ROOT, 'programs_rem', 'ELEM47.txt'), encoding='utf-8')]
    steps = [ln for ln in lines if ln.strip() and not ln.startswith('REM')]
    main = main_program(steps)
    main, num = B.resolve(main)
    big, tiny = chars_used(steps)
    T = textprog('E47T', 21, big) + boxes() + ['END']
    S = textprog('E47S', 10, tiny) + ['END']
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LST, exist_ok=True)
    for p in (main, T, S):
        labs = [x for x in p if re.fullmatch(r'LBL \d\d', x)]
        if len(labs) != len(set(labs)):
            raise SystemExit('free42: a local label twice in %s' % p[0])
    allp = main + T + S
    with open(os.path.join(OUT, 'ELEM47.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(allp) + '\n')
    with open(os.path.join(LST, 'ELEM47_doc.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join('%4d  %s' % (i + 1, s) for i, s in enumerate(allp)) + '\n')
    return main, T, S


if __name__ == '__main__':
    m, t, s = build()
    for n, p in (('ELEM47', m), ('E47T', t), ('E47S', s)):
        print('%-7s %5d steps  about %5d bytes' % (n, len(p), B.estimate(p)))
    print('build/free42/ELEM47.txt')
