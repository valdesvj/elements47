#!/usr/bin/env python3
"""build_free42.py - ELEM47 for Free42 on the SwissMicros DM42 / DM42n (stock firmware, Free42 3.3).

The same program as the C47 release (programs_rem/ELEM47.txt), converted step by step, the way
Almanac 47 converts NAV (its tools/build_free42.py):

  screen       3 STO "GrMod": AGRAPH on the whole 400 x 240 screen (row 1 at the top, column 1 at
               the left; the C47 counts rows from the bottom, from 0: C47 row r = Free42 row 240 - r).
  AGRAPH       Free42 draws the ALPHA register, one character = one column of 8 pixels, bit 0 at the
               top. The cells, the cursor and the detail box frame (C47 columns of 24 to 60 bits in a
               register) become bands of 8 rows: :FCELL: (a cell), :FCURS: (the cursor), :FBOX: (any box).
  GRMOD        flags 34 and 35: CF CF = 0 (set the pixels), CF SF = 1 (write the pattern exactly),
               SF SF = 3 (flip). GRMOD 1 text: each character writes its whole box, as the C47 clears it.
  ATEXT Z      XEQ :FT21: (GRFNT 21) or :FT10: (GRFNT 10, the tinyFont): Z the text, Y the row of the
               bottom of the glyph box, X the column, as on the C47 (|X| and |Y|). The glyphs are the C47 fonts
               (python/stdfont.py, tinyfont.py, drawn by python/c47sim.py) as data: an index text and a table
               text per font (:FDATA: puts them in registers at the start); each character's record holds its
               box width, its advance and the columns of the glyph box in bands of 8 rows (20 rows: bands at
               0, 8 and 12), drawn with CLA, ARCL and AGRAPH.
  texts        a C47 "..." goes on the stack: XSTR "..."; the CR glyph is character 13 (€0d).
               x→α r: RCL r X<>Y APPEND STO r;  αIP r: CLA AIP ASTO ST X, then the same;
               αSL r: SUBSTR from X;  αLEFT r: SUBSTR 0 to X;  αPOS r: POS;  α→x r: HEAD r C→N.
  keys         PAUSE 50 / KEY? 33 / GTO: GETKEY, STO 33; the key codes of :KEYS: in Free42 codes
               (8 20, 2 30, 4 24, 6 26, 5 25, 0 34).
  registers    SIZE 90 if smaller (ELEM47 uses R20-R51, the text and box routines R60-R89); at the end
               CLRG and CLST, as CLREGS and CLSTK on the C47.
  one program  one global label, LBL "ELEM47"; everything else local (Free42 has numeric local labels only:
               the named labels get numbers, as in build/ELEM47_num.txt).
  labels       the named local labels numbered as in build/ELEM47_num.txt (Free42: 00-99 only).

Files: build/free42/ELEM47.txt (one program, to paste in Free42), listings/free42/.
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


def xstr(bs):
    """Steps that leave a string of these bytes (Free42 codes) in X: XSTR pieces joined with APPEND,
    cut after the bytes that start a paste alias (<= -> ...) and at 40 bytes."""
    out, cur = [], []

    def flush():
        if cur or not out:
            out.extend(['XSTR "%s"' % ''.join('€%02x' % b for b in cur)] + (['APPEND'] if out else []))
        del cur[:]
    for b in bs:
        cur.append(b)
        if b in SPLIT or len(cur) == 40:
            flush()
    if cur or not out:
        flush()
    return out


# the text engine's registers (Free42 only; ELEM47 uses R20-R51; all cleared by CLRG at the end)
TX, T0, TL, TS, TB, TK, TR, IDX, TAB = 60, 61, 62, 63, 64, 65, 66, 67, 68
FONTREG = {21: (69, 70), 10: (71, 72)}          # the index text and the glyph table of each font
LH_, RL_, WM_, W_, ADV_, OFF_, OFC_ = 73, 74, 75, 76, 77, 78, 79
BY, BX, BW, BH, BT, BR, BB, BC, BK, BN = range(80, 90)
SIZE = 90


def font_table(font, chars):
    """The index text (the Free42 codes of the characters, '?' first) and the glyph table: for each
    character its box width, its advance, then the bands of 8 rows, each WM bytes."""
    chars = ['?'] + sorted(set(chars) - {'?'})
    g, LH = glyphs(font, chars)
    offs = (0, 8, 12) if LH == 20 else (0,)
    WM = max(w for _, _, w in g.values())
    idx, tab = [], []
    for ch in chars:
        cols, adv, w = g[ch]
        idx.append(F42CODE.get(ch, ord(ch)))
        tab += [w, adv]
        for o, bs in bands(cols, LH, offs):
            tab += bs + [0] * (WM - len(bs))
    return idx, tab, LH, offs, WM


def text_routines(tables):
    """:FT21: / :FT10: = ATEXT Z in GRFNT 21 / 10: Z the text, Y the bottom row of the glyph box, X the
    column (|X|, |Y|, as the C47). Each character: its place in the index text (POS), its record in the
    glyph table (SUBSTR), then each band: CLA, ARCL the bytes, AGRAPH (row, column)."""
    L = []
    for font in (21, 10):
        idx, tab, LH, offs, WM = tables[font]
        L += ['LBL :FT%d:' % font, 'ABS', 'STO %d' % TX, 'STO %d' % T0, 'R↓', 'ABS', 'STO %d' % TL, 'R↓', 'STO %d' % TS,
              'RCL %d' % FONTREG[font][0], 'STO %d' % IDX, 'RCL %d' % FONTREG[font][1], 'STO %d' % TAB,
              str(LH), 'STO %d' % LH_, str(2 + len(offs) * WM), 'STO %d' % RL_, str(WM), 'STO %d' % WM_]
        L += xstr(list(offs)) + ['STO %d' % OFF_, 'GTO :FLINE:']
    L += ['LBL :FLINE:', '241', 'RCL %d' % LH_, '-', 'RCL %d' % TL, '-', 'STO %d' % TB,
          'LBL :FCHR:', 'RCL %d' % TS, 'LENGTH', 'X=0?', 'RTN', 'HEAD %d' % TS, 'C→N', '13', 'X=Y?', 'GTO :FNL:',
          'X<>Y', 'N→C', 'RCL %d' % IDX, 'X<>Y', 'POS', 'X<0?', 'CLX',
          'RCL %d' % RL_, '×', 'STO %d' % TK, 'RCL %d' % TAB, 'RCL %d' % TK, 'RCL %d' % TK, 'RCL %d' % RL_, '+', 'SUBSTR',
          'STO %d' % TR, 'HEAD %d' % TR, 'C→N', 'STO %d' % W_, 'HEAD %d' % TR, 'C→N', 'STO %d' % ADV_,
          'RCL %d' % OFF_, 'STO %d' % OFC_,
          'LBL :FBAND:', 'RCL %d' % OFC_, 'LENGTH', 'X=0?', 'GTO :FNEXT:',
          'CLA', 'RCL %d' % TR, '0', 'RCL %d' % W_, 'SUBSTR', 'ARCL ST X',
          'HEAD %d' % OFC_, 'C→N', 'RCL %d' % TB, '+', 'RCL %d' % TX, '1', '+', 'AGRAPH',
          'RCL %d' % TR, 'RCL %d' % WM_, 'SUBSTR', 'STO %d' % TR, 'GTO :FBAND:',
          'LBL :FNEXT:', 'RCL %d' % ADV_, 'STO+ %d' % TX, 'GTO :FCHR:',
          'LBL :FNL:', 'RCL %d' % T0, 'STO %d' % TX, 'RCL %d' % LH_, 'STO- %d' % TL, 'GTO :FLINE:']
    # :FDATA: the index texts and the glyph tables into their registers (once, at the start)
    L.append('LBL :FDATA:')
    for font in (21, 10):
        idx, tab, LH, offs, WM = tables[font]
        L += xstr(idx) + ['STO %d' % FONTREG[font][0]] + xstr(tab) + ['STO %d' % FONTREG[font][1]]
    return L + ['RTN']


def box_routine():
    """:FBOX: a box BW columns x BH rows, bottom row BY, left column BX (C47 coordinates), in the mode
    of flags 34 / 35, bands of 8 rows, 44 columns per AGRAPH (Almanac 47's FBX)."""
    r = lambda k: '%02d' % k
    return ['LBL :FBOX:', '241', 'RCL ' + r(BY), '-', 'RCL ' + r(BH), '-', 'STO ' + r(BT), 'RCL ' + r(BH), 'STO ' + r(BR),
            'LBL :FB1:', 'RCL ' + r(BR), 'X≤0?', 'RTN', '255', 'STO ' + r(BB), '8', 'RCL ' + r(BR), 'X<Y?', 'XEQ :FB2:',
            'RCL ' + r(BW), 'STO ' + r(BC), 'RCL ' + r(BX), '1', '+', 'STO ' + r(BK),
            'LBL :FB3:', 'RCL ' + r(BC), 'X≤0?', 'GTO :FB4:', '44', 'X>Y?', 'X<>Y', 'STO ' + r(BN), 'CLA',
            'LBL :FB5:', 'RCL ' + r(BB), 'XTOA', 'DSE ' + r(BN), 'GTO :FB5:',
            'RCL ' + r(BT), 'RCL ' + r(BK), 'AGRAPH', '44', 'STO+ ' + r(BK), '-44', 'STO+ ' + r(BC), 'GTO :FB3:',
            'LBL :FB4:', '8', 'STO+ ' + r(BT), '-8', 'STO+ ' + r(BR), 'GTO :FB1:',
            'LBL :FB2:', '2', 'RCL ' + r(BR), 'Y↑X', '1', '-', 'STO ' + r(BB), 'RTN']


def fbx(x, y, w, h, mode):
    return GRMOD[mode] + [str(y), 'STO %d' % BY, str(x), 'STO %d' % BX, str(w), 'STO %d' % BW, str(h), 'STO %d' % BH,
                          'XEQ :FBOX:']


# ------------------------------------------------------------------ ELEM47
def cell_routine():
    """:FCELL: the box of a cell (23 x 26, OR) at R39 (left column), R40 (bottom row): 4 bands."""
    cols = {0: set(range(26)), 22: set(range(26))}
    for x in range(1, 22):
        cols[x] = {0, 25}
    L = ['LBL :FCELL:'] + GRMOD[0] + ['215', 'RCL 40', '-', 'STO %d' % TB]
    for o, bs in bands(cols, 26, (0, 8, 16, 18)):
        L += alpha_literal(bs) + ['RCL %d' % TB] + ([str(o), '+'] if o else []) + ['RCL 39', '1', '+', 'AGRAPH']
    return L + ['RTN']


def cursor_routine():
    """:FCURS: the cursor: the inside of the cell (21 x 24) flipped, from column R39 + 1, row R40 + 1."""
    cols = {x: set(range(24)) for x in range(21)}
    L = ['LBL :FCURS:'] + GRMOD[3] + ['216', 'RCL 40', '-', 'STO %d' % TB]
    for o, bs in bands(cols, 24, (0, 8, 16)):
        L += alpha_literal(bs) + ['RCL %d' % TB] + ([str(o), '+'] if o else []) + ['RCL 39', '2', '+', 'AGRAPH']
    return L + GRMOD[0] + ['RTN']


def replace(L, old, new):
    for i in range(len(L) - len(old) + 1):
        if L[i:i + len(old)] == old:
            return L[:i] + new + L[i + len(old):]
    raise SystemExit('free42: not found: %s' % old[:4])


def text(s):
    return 'XSTR "%s"' % s[1:-1].replace('↵', '€0d')


def main_program(steps, tables):
    S = list(steps)
    # the user's registers: REGS saved (SIZE 52 at least), given back at the end
    # the registers: SIZE 52 at least; at the end CLRG, CLST (CLREGS, CLSTK on the C47)
    i = S.index('LBL "ELEM47"')
    S[i + 1:i + 1] = (['RCL "REGS"', 'DIM?', 'R↓', str(SIZE), 'X>Y?', 'SIZE %d' % SIZE, '3', 'STO "GrMod"'] + GRMOD[0]
                      + ['XEQ :FDATA:'])
    S = replace(S, ['0', 'GRMOD', '20', 'GRFNT', 'DELITM "PT"'], GRMOD[0] + ['CLV "PT"'])
    S = replace(S, ['CLLCD', 'CLREGS', 'CLSTK', 'RTN'], ['CLLCD', '0', 'STO "GrMod"', 'CLRG', 'CLST', 'CLD', 'RTN'])
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
            out.append('XEQ :FT%d:' % font)
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
    out = out[:k] + cell_routine() + cursor_routine() + box_routine() + text_routines(tables) + out[k:]
    bad = [s for s in out if s.endswith('#2') or s.split(' ')[0] in (
        'GRMOD', 'GRFNT', 'ATEXT', 'KEY?', 'PAUSE', 'LocR', 'WSIZE', 'x→α', 'αIP', 'αSL', 'αLEFT', 'αPOS',
        'α→𝑥', 'DELITM', 'CLSTK', 'CLREGS', 'CHS') or s.startswith('AGRAPH ') or 'R.' in s]
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
    big, tiny = chars_used(steps)
    tables = {21: font_table(21, big), 10: font_table(10, tiny)}
    main, num = B.resolve(main_program(steps, tables))
    labs = [x for x in main if re.fullmatch(r'LBL \d\d', x)]
    if len(labs) != len(set(labs)) or sum(1 for x in main if x.startswith('LBL "')) != 1:
        raise SystemExit('free42: one global label, each local label once')
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LST, exist_ok=True)
    with open(os.path.join(OUT, 'ELEM47.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(main) + '\n')
    with open(os.path.join(LST, 'ELEM47_doc.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join('%4d  %s' % (i + 1, x) for i, x in enumerate(main)) + '\n')
    return main, num


if __name__ == '__main__':
    m, num = build()
    print('ELEM47 (Free42) %5d steps, 1 global label, %d local labels -> build/free42/ELEM47.txt' % (
        len(m), sum(1 for x in m if re.fullmatch(r'LBL \d\d', x))))
