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

PROG = os.path.join(ROOT, 'build', 'ELEM47.txt')
W, H = 400, 240
LCD_BG, LCD_ON = (199, 205, 186), (34, 38, 30)


UP, DOWN, LEFT, RIGHT, INFO, END = 53, 73, 62, 64, 63, 82     # the keys 8 2 4 6 5 0


class _Frames(list):
    """The screens, and the steps run before each one (c.at_steps)."""
    def __init__(self, c): super().__init__(); self.c = c; c.at_steps = []
    def append(self, f): self.c.at_steps.append(self.c.steps); super().append(f)


def frames(keys=(RIGHT, INFO, 1, END), prog=PROG):
    """The screens of ELEM47 for the keys pressed. The run ends when the keys run out (or at the end).
    c.at_steps: the steps run before each screen (the work of each key = the difference)."""
    c = c47sim.load([prog])
    c.s = [D(0)] * 4; c.pix = []; c.keys = list(keys); c.steps = 0; c.frames = _Frames(c)
    try:
        c.run('ELEM47', maxsteps=10 ** 6)
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
KEYS = [DOWN] * 3 + [RIGHT] * 7 + [INFO, 1] + [DOWN] * 4 + [INFO, 1, END]


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
