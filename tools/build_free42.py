#!/usr/bin/env python3
"""build_free42.py - ELEM47 for Free42 on the SwissMicros DM42 / DM42n (stock firmware, Free42 3.3.10).

The C47 release (v1.2.0, the PIXEL variant's source programs_rem/pixel/ELEM47.txt), converted step by step,
the way Almanac 47 converts NAV (its tools/build_free42.py):

  STRUCT       Free42 has none: the numbered structures become named local labels and GTO (lower(): a test
               before IF / WHILE / UNTIL inverted where it can be), numbered with the other labels (00-99).
  screen       3 STO "GrMod": AGRAPH on the whole 400 x 240 screen (row 1 at the top, column 1 at
               the left; the C47 counts rows from the bottom, from 0: C47 row r = Free42 row 240 - r).
  AGRAPH       Free42 draws the ALPHA register, one character = one column of 8 pixels, bit 0 at the
               top, up to 44 columns in one AGRAPH. The cells, the cursor and the detail box frame become bands
               of 8 rows: :FCELL: (a whole cell, 4 AGRAPH of 23 columns), :FCURS: (the cursor), E47B (any box).
               So the C47's PIXEL rows (:GRID:, :ROWS:) and their clearing are left out: on Free42 a whole cell
               takes as many AGRAPH as its left edge alone. The screens are the same.
  GRMOD        flags 34 and 35: CF CF = 0 (set the pixels), CF SF = 1 (write the pattern exactly),
               SF SF = 3 (flip). GRMOD 1 text: each character writes its whole box, as the C47 clears it.
  ATEXT Z      XEQ "E47T" (GRFNT 21) or "E47S" (GRFNT 10, the tinyFont): Z the text, Y the row of the
               bottom of the glyph box, X the column, as on the C47 (|X| and |Y|). The glyphs are the C47 fonts
               (python/stdfont.py, tinyfont.py, drawn by python/c47sim.py), one local label each (XEQ IND),
               the columns of the glyph box in bands of 8 rows (20 rows: bands at 0, 8 and 12).
  texts        a C47 "..." goes on the stack: XSTR "..."; the CR glyph is character 13 (€0d).
               x→α r: RCL r X<>Y APPEND STO r;  αIP r: CLA AIP ASTO ST X, then the same;
               αSL r: SUBSTR from X;  αLEFT r: SUBSTR 0 to X;  αPOS r: POS;  α→x r: HEAD r C→N; αLENG: LENGTH.
  matrix       STOSEQ: STOEL J+.
  LCD          as the C47: the screen shows only when ELEM47 waits for a key. RefLCD (DM42 / DM42n virtual
               variable, as Almanac 47's RLCD build): 0 at the start (no LCD refresh while drawing), -1 before
               each GETKEY (the screen shown once), 7 at the end (the normal refresh).
  keys         the key wait DO / PAUSE 50 / KEY? 33 / WHILE / ENDDO: -1 STO "RefLCD", GETKEY, then the Free42 code
               made the C47 code (KEYTAB: 8 4 6 2 5 0, F1-F3 = the keys under them), STO 33: the source's key
               arithmetic stays as it is.
  stack        v1.2.0 keeps the user's stack: the C47's local registers R.00-R.09 are local variables "L00" ...
               of ELEM47 (LSTO), its local flag F.00 is flag 81 (FS?C at the end), STO L is STO ST L. ALPHA is
               kept too (LXASTO "LA", ARCL at the end).
  registers    ELEM47 keeps a copy of REGS ("LR") at the start, sets SIZE 76 if smaller (E47T, E47S and E47B
               work in R60-R75); at the end REGS from the copy (the user's SIZE and registers back), then
               R20-R56 cleared as the C47's 20.37 R-CLR (:RCLR:, as far as SIZE goes).
  programs     ELEM47, ELD1 and ELD2 as on the C47 (the code; the element records); E47T (the GRFNT 21
               glyphs, and E47B); E47S (the GRFNT 10 glyphs).

Files: build/free42/ELEM47.txt (ELEM47, ELD1, ELD2, E47T, E47S: paste it into Free42), listings/free42/, and
build/free42/ELEM47.raw (the Free42 program file, not in git) when f42run is there (F42RUN, else
~/opt/almanac47/tools/f42/f42run): pasted into the Free42 core and exported, as Almanac 47 makes its .raw files.
rejig cannot make the .raw: its Free42 table does not know Free42's own commands (LSTO ...).
Test: tests/test_f42.py (f42run, the Free42 3.3.10 core of the DM42, against python/c47sim.py).
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


# the registers of E47T, E47S and E47B (Free42 only; ELEM47 uses R20-R54; all cleared by CLRG at the end)
TX, T0, TL, TS, TB, TK = range(60, 66)
BY, BX, BW, BH, BT, BR, BB, BC, BK, BN = range(66, 76)
SIZE = 76


def textprog(name, font, chars):
    """E47T / E47S: ATEXT with Z the text, Y the bottom row of the glyph box, X the column (|X|, |Y|, as
    the C47). One local label per character, reached with XEQ IND: its bands of 8 rows drawn with AGRAPH."""
    g, LH = glyphs(font, sorted(chars))
    offs = (0, 8, 12) if LH == 20 else (0,)
    L = ['LBL "%s"' % name, 'ABS', 'STO %d' % TX, 'STO %d' % T0, 'R↓', 'ABS', 'STO %d' % TL, 'R↓', 'STO %d' % TS,
         'LBL 99', str(241 - LH), 'RCL %d' % TL, '-', 'STO %d' % TB,
         'LBL 98', 'RCL %d' % TS, 'LENGTH', 'X=0?', 'RTN', 'HEAD %d' % TS, 'C→N', '13', 'X=Y?', 'GTO 97',
         'X<>Y', '80', '+', '112', 'MOD', 'STO %d' % TK, 'XEQ IND %d' % TK, 'GTO 98',
         'LBL 97', 'RCL %d' % T0, 'STO %d' % TX, str(LH), 'STO- %d' % TL, 'GTO 99']
    # the label: (code + 80) MOD 112 = code - 32, the arrows (14-16) 94-96
    for ch in sorted(g, key=label_of):
        cols, adv, w = g[ch]
        L.append('LBL %02d' % label_of(ch))
        for o, bs in bands(cols, LH, offs):
            L += alpha_literal(bs) + ['RCL %d' % TB] + ([str(o), '+'] if o else []) + ['RCL %d' % TX, '1', '+', 'AGRAPH']
        L += [str(adv), 'STO+ %d' % TX, 'RTN']
    return L


def box_routine():
    """E47B: a box BW columns x BH rows, bottom row BY, left column BX (C47 coordinates), in the mode
    of flags 34 / 35, bands of 8 rows, 44 columns per AGRAPH (Almanac 47's FBX)."""
    r = lambda k: '%02d' % k
    return ['LBL "E47B"', '241', 'RCL ' + r(BY), '-', 'RCL ' + r(BH), '-', 'STO ' + r(BT), 'RCL ' + r(BH), 'STO ' + r(BR),
            'LBL 01', 'RCL ' + r(BR), 'X≤0?', 'RTN', '255', 'STO ' + r(BB), '8', 'RCL ' + r(BR), 'X<Y?', 'XEQ 02',
            'RCL ' + r(BW), 'STO ' + r(BC), 'RCL ' + r(BX), '1', '+', 'STO ' + r(BK),
            'LBL 03', 'RCL ' + r(BC), 'X≤0?', 'GTO 04', '44', 'X>Y?', 'X<>Y', 'STO ' + r(BN), 'CLA',
            'LBL 05', 'RCL ' + r(BB), 'XTOA', 'DSE ' + r(BN), 'GTO 05',
            'RCL ' + r(BT), 'RCL ' + r(BK), 'AGRAPH', '44', 'STO+ ' + r(BK), '-44', 'STO+ ' + r(BC), 'GTO 03',
            'LBL 04', '8', 'STO+ ' + r(BT), '-8', 'STO+ ' + r(BR), 'GTO 01',
            'LBL 02', '2', 'RCL ' + r(BR), 'Y↑X', '1', '-', 'STO ' + r(BB), 'RTN']


def fbx(x, y, w, h, mode):
    return GRMOD[mode] + [str(y), 'STO %d' % BY, str(x), 'STO %d' % BX, str(w), 'STO %d' % BW, str(h), 'STO %d' % BH,
                          'XEQ "E47B"']


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


# Free42 GETKEY code (1-37) -> the C47 KEY? code, + 40 so that every character is printable (32 + 40: a
# key ELEM47 ignores). 20 8, 30 2, 24 4, 26 6, 25 5, 34 0; 1-3 the keys under F1-F3 (Sigma+ 1/x sqrt).
C47KEY = {20: 53, 30: 73, 24: 62, 26: 64, 25: 63, 34: 82, 1: 11, 2: 12, 3: 13}
KEYTAB = ''.join(chr(C47KEY.get(k, 32) + 40) for k in range(1, 38))


def lower(steps):
    """The numbered STRUCT steps (IF 01 ...) as named labels and GTO (Free42 has no STRUCT): a test before
    IF / WHILE / UNTIL inverted where it can be, else test + GTO + GTO + LBL; WHILE just before its ENDDO:
    test + GTO back to the DO (DSE n WHILE ENDDO = DSE n GTO). The names (:I03E: ...) get local numbers
    in B.resolve with the other named labels."""
    inv = {'X=0?': 'X≠0?', 'X<0?': 'X≥0?', 'X>0?': 'X≤0?', 'X=Y?': 'X≠Y?', 'X<Y?': 'X≥Y?', 'X>Y?': 'X≤Y?'}
    inv.update({v: k for k, v in list(inv.items())})
    has_else = {s.split()[1] for s in steps if s.startswith('ELSE ')}
    out, i = [], 0
    while i < len(steps):
        s = steps[i]
        op, _, k = s.partition(' ')
        lab = lambda kind, end='': ':%s%s%s:' % (kind, int(k), end)
        if op in ('IF', 'WHILE', 'UNTIL'):
            test = out.pop()
            if op == 'IF':
                go = lab('I', 'F' if k in has_else else 'E')
            elif op == 'WHILE':
                go = lab('D', 'E')
                if steps[i + 1] == 'ENDDO ' + k:
                    out += [test, 'GTO ' + lab('D'), 'LBL ' + lab('D', 'E')]
                    i += 2
                    continue
            else:
                go = lab('R')
            if test in inv:
                out += [inv[test], 'GTO ' + go]
            else:
                out += [test, 'GTO ' + lab(op[0], 'T'), 'GTO ' + go, 'LBL ' + lab(op[0], 'T')]
        elif op == 'ELSE':
            out += ['GTO ' + lab('I', 'E'), 'LBL ' + lab('I', 'F')]
        elif op == 'ENDIF':
            out.append('LBL ' + lab('I', 'E'))
        elif op in ('DO', 'REPEAT'):
            out.append('LBL ' + lab(op[0]))
        elif op == 'ENDDO':
            out += ['GTO ' + lab('D'), 'LBL ' + lab('D', 'E')]
        else:
            out.append(s)
        i += 1
    return out


def main_program(steps):
    """steps: the source steps of programs_rem/pixel/ELEM47.txt (named labels, STRUCT numbered)."""
    S = B.structures(list(steps))                    # the partner numbers first (DO 02 ...)
    # the start, after the source has saved the user's stack and LASTx (STO R.08): ALPHA saved too (Free42's
    # text steps use it), SIZE 76 at least, the 400 x 240 screen, no LCD refresh while drawing, GRMOD 0, flag 81 clear
    i = S.index('STO R.08', S.index('LBL "ELEM47"'))
    S[i + 1:i + 1] = (['LXASTO "LA"', 'RCL "REGS"', 'LSTO "LR"', 'DIM?', 'R↓', str(SIZE), 'X>Y?', 'SIZE %d' % SIZE, '3', 'STO "GrMod"']
                      + ['0', 'STO "RefLCD"'] + GRMOD[0] + ['CF 81'])
    # the key wait: GETKEY, its code made a C47 code (KEYTAB), so the source's key arithmetic is unchanged
    wait = ['DO %s', 'PAUSE 50', 'KEY? 33', 'WHILE %s', 'ENDDO %s']
    k = next(j for j in range(len(S)) if S[j].startswith('DO ') and S[j + 1:j + 3] == ['PAUSE 50', 'KEY? 33'])
    n = S[k].split()[1]
    assert S[k:k + 5] == [w % n if '%' in w else w for w in wait]
    # (Z the table, Y k - 1, X k: SUBSTR gives character k - 1 from 0; RCL ST X keeps the stack lift on)
    S[k:k + 5] = ['-1', 'STO "RefLCD"', 'GETKEY', 'XSTR "%s"' % KEYTAB, 'X<>Y', '1', '-', 'RCL ST X', '1', '+',
                  'SUBSTR', 'C→N', '40', '-', 'STO 33']
    # the end: GRMOD 0, PT deleted, the screen as Free42 shows it again
    S = replace(S, ['0', 'GRMOD', '20', 'GRFNT', 'DELITM "PT"', 'CLLCD'],
                GRMOD[0] + ['CLV "PT"', 'CLLCD', '0', 'STO "GrMod"', '7', 'STO "RefLCD"', 'CLD', 'CLA',
                                'ARCL "LA"'])
    # R-CLR (X = 20.37: R20-R56): the user's registers back first (the copy LR of the start: E47T, E47S, E47B
    # work in R60-R75, and SIZE goes back to the user's), then R20-R56 cleared as far as SIZE goes (:RCLR:)
    S = replace(S, ['20.37', 'R-CLR'], ['RCL "LR"', 'STO "REGS"', 'XEQ :RCLR:'])
    # the patterns of the C47 columns: not needed (the cells, the cursor and the box are Free42 bands)
    for k in range(len(S) - 1, -1, -1):
        if S[k].endswith('#2') and S[k + 1] in ('STO 20', 'STO 21', 'STO 23'):
            del S[k:k + 2]
    S = [s for s in S if s != 'WSIZE 64']
    # the table's horizontal lines: on Free42 each cell is drawn whole (:FCELL:, 4 AGRAPH of 23 columns: as many
    # AGRAPH as its left edge alone), so the PIXEL rows of :GRID: / :ROWS: and their clearing are left out
    S.remove('XEQ :GRID:')
    S.remove('XEQ :ROWS:')
    for name in (':GRID:', ':ROWS:'):
        a = S.index('LBL ' + name)
        b = S.index('RTN', a)
        del S[a:b + 1]
    a = S.index('LBL :SEGMENT:')
    S[a:] = replace(S[a:], ['RCL 40', 'RCL 39', 'AGRAPH 20'], ['XEQ :FCELL:'])
    S[a:] = replace(S[a:], ['RCL 40', 'RCL 39', 'AGRAPH 20', 'RTN'], ['RTN'])
    # the cursor
    S = replace(S, ['3', 'GRMOD', 'RCL 53', 'RCL 39', '1', '+'] + ['AGRAPH 23'] * 21 + ['0', 'GRMOD'],
                ['XEQ :FCURS:'])
    # the detail box: the sides x 50 and 349 (rows 56-179), the bottom line (row 56) and the line over F1-F3
    # (row 75), x 51-348; the header bar XOR rows 158-179
    a = S.index('XEQ :BOXCLR:', S.index('LBL :DETREC:'))
    b = S.index('XEQ :HLINE:', a)
    assert S[a + 1:a + 3] == ['0', 'GRMOD']
    S[a + 1:b + 1] = (fbx(50, 56, 1, 124, 0) + fbx(349, 56, 1, 124, 0) + fbx(51, 56, 298, 1, 0)
                      + fbx(51, 75, 298, 1, 0))
    b = S.index('XEQ :HLINE:', a)
    assert S[b - 4:b - 2] == ['3', 'GRMOD'] and S[b + 1:b + 3] == ['0', 'GRMOD'], S[b - 5:b + 3]
    S[b - 4:b + 3] = fbx(51, 158, 298, 22, 3) + GRMOD[0]
    a = S.index('LBL :HLINE:')
    del S[a:S.index('RTN', a) + 1]
    # the structures as labels and GTO
    S = lower(S)
    # step by step: the local registers and flag, fonts, GRMOD, texts, the text functions
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
        m = re.fullmatch(r'(STO|RCL) R\.(\d\d)', s)
        if m:                                           # the C47's local registers: local variables of ELEM47
            out.append(('LSTO "L%s"' if m.group(1) == 'STO' else 'RCL "L%s"') % m.group(2)); continue
        if s == 'LocR 10':
            continue
        if s == 'SF F.00':
            out.append('SF 81'); continue
        if s == 'FS? F.00':
            out.append('FS?C 81'); continue
        if s == 'STO L':
            out.append('STO ST L'); continue
        if s == 'LASTx':
            out.append('LASTX'); continue
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
        elif op == 'αLENG':
            out += ['RCL ' + arg, 'LENGTH']
        elif op == 'α→𝑥':
            out += ['HEAD ' + arg, 'C→N']
        elif s == 'STOSEQ':
            out += ['STOEL', 'J+']
        elif s == 'CHS':
            out.append('+/-')
        else:
            out.append(s)
    k = next(i for i, s in enumerate(out) if s == 'LBL %02d' % B.SYM0)
    out = out[:k] + cell_routine() + cursor_routine() + rclr_routine() + out[k:]
    bad = [s for s in out if s.endswith('#2') or s.split(' ')[0] in (
        'GRMOD', 'GRFNT', 'ATEXT', 'KEY?', 'PAUSE', 'LocR', 'WSIZE', 'x→α', 'αIP', 'αSL', 'αLEFT', 'αPOS', 'αLENG',
        'α→𝑥', 'DELITM', 'CLSTK', 'CLREGS', 'R-CLR', 'CHS', 'STOSEQ', 'LASTx') + B.STRUCT
        or s.startswith('AGRAPH ') or re.search(r'\b[RF]\.\d', s) or s == 'PIXEL']
    if bad:
        raise SystemExit('free42: C47 steps left: %s' % bad[:5])
    return out


def rclr_routine():
    """:RCLR: R20-R56 cleared (the C47's 20.37 R-CLR) as far as the user's SIZE goes, a local variable the index."""
    return ['LBL :RCLR:', 'RCL "REGS"', 'DIM?', 'R↓', '1', '-', '56', 'X>Y?', 'X<>Y', '1000', '÷', '20', '+',
            'LSTO "I"', 'LBL :RCLRL:', 'RCL "I"', 'IP', 'RCL "REGS"', 'DIM?', 'R↓', 'X≤Y?', 'RTN', 'R↓', 'R↓',
            '0', 'STO IND "I"', 'DROP', 'ISG "I"', 'GTO :RCLRL:', 'RTN']


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
    tiny = set('0123456789 ') | set('5: BACK') | set('   8↵5 4 6↵   2↵   0      ↑↵INFO ← →↵      ↓↵     END') - {'↵'}
    return big, tiny


def build():
    """The Free42 build of the release, the PIXEL variant's source (programs_rem/pixel/ELEM47.txt)."""
    lines = [ln.rstrip() for ln in open(os.path.join(ROOT, 'programs_rem', 'pixel', 'ELEM47.txt'), encoding='utf-8')]
    steps = B.source_steps(lines)
    main, num = B.resolve(main_program(steps))
    big, tiny = chars_used(steps)
    T = textprog('E47T', 21, big) + box_routine() + ['END']
    S = textprog('E47S', 10, tiny) + ['END']
    for p in B.programs(main) + [T, S]:
        labs = [x for x in p if re.fullmatch(r'LBL \d\d', x)]
        if len(labs) != len(set(labs)):
            raise SystemExit('free42: a local label twice in %s' % p[0])
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LST, exist_ok=True)
    allp = main + T + S
    with open(os.path.join(OUT, 'ELEM47.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(allp) + '\n')
    with open(os.path.join(LST, 'ELEM47_doc.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join('%4d  %s' % (i + 1, x) for i, x in enumerate(allp)) + '\n')
    return main, T, S


def raw():
    """build/free42/ELEM47.raw with f42run: paste the listing, export (Almanac 47's way)."""
    import subprocess
    f42 = os.environ.get('F42RUN', os.path.expanduser('~/opt/almanac47/tools/f42/f42run'))
    if not os.path.exists(f42):
        print('no f42run (%s; set F42RUN): ELEM47.raw not written' % f42)
        return
    txt = os.path.join(OUT, 'ELEM47.txt')
    r = subprocess.run([f42], input='paste %s\nexport %s\n' % (txt, txt[:-4] + '.raw'), text=True,
                       capture_output=True, cwd=OUT)
    if r.returncode or not os.path.exists(txt[:-4] + '.raw'):
        raise SystemExit('f42run export failed: %s' % (r.stdout + r.stderr)[-300:])
    print('build/free42/ELEM47.raw (%d bytes)' % os.path.getsize(txt[:-4] + '.raw'))


if __name__ == '__main__':
    m, t, s = build()
    for p in B.programs(m) + [t, s]:
        n = p[0][5:-1]
        print('%-7s %5d steps  about %5d bytes' % (n, len(p), B.estimate(p)))
    print('build/free42/ELEM47.txt')
    raw()
