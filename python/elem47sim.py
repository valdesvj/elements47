"""elem47sim.py - run build/ELEM47.txt in the C47 simulator (c47sim.py, from Almanac 47) and turn its
screens into pictures.
  frames(keys)  the screens shown while ELEM47 waits for a key, as sets of (x, row), row 0 = top
  png(fn, pix)  a PNG of one screen (LCD colours, 3 pixels per C47 pixel)
  python3 python/elem47sim.py   writes the screens in docs/ and prints the step counts"""
import os, struct, sys, zlib
from decimal import Decimal as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import c47sim

PROG = os.environ.get('ELEM47_PROG') or os.path.join(ROOT, 'build', 'ELEM47.txt')   # ELEM47_PROG: a variant (build/loops)
W, H = 400, 240
LCD_BG, LCD_ON = (199, 205, 186), (34, 38, 30)


UP, DOWN, LEFT, RIGHT, INFO, END = 53, 73, 62, 64, 63, 82     # the keys 8 2 4 6 5 0
# ELEM47's registers: cursor Z, row, column; name; the detail box's left and right value texts
REG = dict(Z='30', ROW='31', COL='32', NAME='37', LEFT='38', RIGHT='48')
REG_V1 = dict(Z='36', ROW='37', COL='38', NAME='43', LEFT='44', RIGHT='54')     # before the optimize branch


INVERSE = {'X=0?': 'X≠0?', 'X<0?': 'X≥0?', 'X>0?': 'X≤0?', 'X=Y?': 'X≠Y?', 'X<Y?': 'X≥Y?', 'X>Y?': 'X≤Y?'}
INVERSE.update({v: k for k, v in list(INVERSE.items())})


def lower(steps, tag):
    """The C47 STRUCT commands (IF / ELSE / ENDIF, DO / WHILE / ENDDO, REPEAT / UNTIL, numbered as in
    build/ELEM47.txt) written with labels and GTO for c47sim, which has no STRUCT yet (Almanac 47): the
    same jumps as the firmware (structured.c). A test before IF, WHILE or UNTIL is inverted where it can be
    (test + IF -> inverted test + GTO, as many steps); KEY? and DSE are not: test, GTO, GTO, LBL. WHILE just
    before its ENDDO: test + GTO back to the DO. The label names carry tag (the program), so they stay local.
    The step counts are close to the firmware's, not the same: ENDIF and the labels count as steps here."""
    has_else = {s.split()[1] for s in steps if s.startswith('ELSE ')}
    out, i = [], 0
    while i < len(steps):
        s = steps[i]
        op, _, k = s.partition(' ')
        lab = lambda kind, end='': '%s%s%s%s' % (tag, kind, k, end)
        if op in ('IF', 'WHILE', 'UNTIL'):
            test = out.pop()
            if op == 'IF':
                go = lab('I', 'F' if k in has_else else 'E')     # false: the ELSE, else the ENDIF
            elif op == 'WHILE':
                go = lab('D', 'E')                                # false: past the ENDDO
                if steps[i + 1] == 'ENDDO ' + k:                  # WHILE just before ENDDO: true goes back to the DO
                    out += [test, 'GTO ' + lab('D'), 'LBL ' + lab('D', 'E')]
                    i += 2
                    continue
            else:
                go = lab('R')                                     # UNTIL false: back to the REPEAT
            if test in INVERSE:
                out += [INVERSE[test], 'GTO ' + go]
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


def split(prog):
    """The programs of a file (each ends with END) as separate files, so their numeric labels stay local
    (c47sim.load: one program per file, as on the C47), the STRUCT commands lowered (lower). Returns the
    file names."""
    import tempfile
    d = tempfile.mkdtemp(prefix='elem47_'); files, cur = [], []
    for ln in open(prog, encoding='utf-8').read().splitlines():
        if ln.strip() == 'CLREGS':           # c47sim has no CLREGS yet (Almanac 47): R00-R99 set to 0 here
            cur += ['0'] + ['STO %02d' % r for r in range(100)]
            continue
        cur.append(ln)
        if ln.strip() == 'END':
            files.append(os.path.join(d, 'p%d.txt' % len(files)))
            cur = lower(cur, 'S%d' % len(files))
            open(files[-1], 'w', encoding='utf-8').write('\n'.join(cur) + '\n'); cur = []
    return files


class _Frames(list):
    """The screens, and the steps run before each one (c.at_steps)."""
    def __init__(self, c): super().__init__(); self.c = c; c.at_steps = []
    def append(self, f): self.c.at_steps.append(self.c.steps); super().append(f)


def frames(keys=(RIGHT, INFO, INFO, END), prog=PROG, regs=None, label='ELEM47'):
    """The screens of ELEM47 (or of the program label in prog) for the keys pressed. The run ends when the keys run out (or at the end).
    c.at_steps: the steps run before each screen (the work of each key = the difference)."""
    c = c47sim.load(split(prog))
    c.s = [D(0)] * 4; c.pix = []; c.keys = list(keys); c.steps = 0; c.frames = _Frames(c)
    if regs:
        c.reg.update(regs)                     # the user's registers before ELEM47 runs
    try:
        c.run(label, maxsteps=10 ** 6)
    except StopIteration:
        pass
    shots = [{(x, H - 1 - y) for y, x in f if 0 <= y < H and 0 <= x < W} for f in c.frames]
    return shots, c


def png(fn, pix, scale=3, border=12):
    w, h = W * scale + 2 * border, H * scale + 2 * border
    buf = bytearray(bytes(LCD_BG) * (w * h))
    dot = bytes(LCD_ON) * scale
    for x, r in pix:
        for dy in range(scale):
            o = ((border + r * scale + dy) * w + border + x * scale) * 3
            buf[o:o + len(dot)] = dot
    raw = b''.join(b'\x00' + bytes(buf[y * w * 3:(y + 1) * w * 3]) for y in range(h))

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(fn, 'wb') as fh:
        fh.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                 + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


SHOTS = [('ELEM47_table.png', 'the table, cursor on H'), ('ELEM47_fe.png', 'cursor on Fe (2 2 2 6 x7)'),
         ('ELEM47_detail_fe.png', 'detail box of Fe (5)'), ('ELEM47_sm.png', 'cursor on Sm (2 x4: Ru Os Hs Sm)'),
         ('ELEM47_detail_sm.png', 'detail box of Sm (5)')]
KEYS = [DOWN] * 3 + [RIGHT] * 7 + [INFO, INFO] + [DOWN] * 4 + [INFO, INFO, END]


if __name__ == '__main__':
    shots, c = frames(KEYS)
    st = c.at_steps
    idx = [0, 10, 11, 16, 17]          # the screens kept: start, Fe, Fe detail, Sm, Sm detail
    for (fn, what), i in zip(SHOTS, idx):
        png(os.path.join(ROOT, 'docs', fn), shots[i])
        print('docs/%-22s %s' % (fn, what))
    moves = [st[i] - st[i - 1] for i in list(range(1, 11)) + list(range(13, 17))]
    print('steps: table %d, move %d-%d (mean %d), detail box %d, table again %d' % (
        st[0], min(moves), max(moves), sum(moves) // len(moves), st[11] - st[10], st[12] - st[11]))
