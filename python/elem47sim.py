"""elem47sim.py - run build/ELEM47.txt in the C47 simulator (c47sim.py, from Almanac 47) and turn its
screens into pictures.
  frames(keys)  the screens shown while ELEM47 waits for a key, as sets of (x, row), row 0 = top
  png(fn, pix)  a PNG of one screen (LCD colours, 3 pixels per C47 pixel)
  python3 python/elem47sim.py   writes docs/ELEM47_table.png and docs/ELEM47_detail.png"""
import os, struct, sys, zlib
from decimal import Decimal as D

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import c47sim

PROG = os.path.join(ROOT, 'build', 'ELEM47.txt')
W, H = 400, 240
LCD_BG, LCD_ON = (199, 205, 186), (34, 38, 30)


def frames(keys=(85, 85, 82), prog=PROG):
    """The screens of ELEM47 for the keys pressed (85 = +). The run ends when the keys run out."""
    c = c47sim.load([prog])
    c.s = [D(0)] * 4; c.frames = []; c.pix = []; c.keys = list(keys)
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


if __name__ == '__main__':
    shots, _ = frames()
    png(os.path.join(ROOT, 'docs', 'ELEM47_table.png'), shots[0])
    png(os.path.join(ROOT, 'docs', 'ELEM47_detail.png'), shots[1])
    print('docs/ELEM47_table.png, docs/ELEM47_detail.png (%d screens)' % len(shots))
