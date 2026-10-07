#!/usr/bin/env python3
"""test_fw.py - ELEM47 in the C47 firmware itself: T47, the PC simulator built from the firmware sources
(~/opt/c43, built in a copy: see DEVELOPMENT_NOTES), headless with its Tcl script (--script).
  - tests/calc/LTEST.txt: a 196-character text in a program (the longest the data may use)
  - the whole table, every row both ways: at each cell 5 (the detail box), then a key (the table again);
    every screen the same as python/c47sim.py, pixel for pixel, and the table back after each box
  - build/ELEM47_num.txt (the numeric fallback): the same screens
  - the end: R00-R99 and the stack cleared, no error
The key waits (PAUSE n / KEY? r / GTO) are replaced in a test copy by PAUSE 1 (the firmware puts the drawing
on the screen at a PAUSE), SNAP (a .bmp) and the next key from the text in the variable TKS (α→x takes its
first character). rejig writes the .p47 files (in a temporary folder, never committed).

  python3 tests/test_fw.py            (T47 from C47SIM, default ~/.cache/c47fw/t47; about 5 minutes)
  python3 tests/test_fw.py quick      (the first two rows only)"""
import glob, os, re, shutil, struct, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python')]
import elem47sim as E                                                  # noqa: E402

SIM = os.environ.get('C47SIM', os.path.expanduser('~/.cache/c47fw/t47'))
ANY = 72                         # the key 1: not used by ELEM47, so "any key" (closes the box)
ERRORS = ('rror', 'ndefined', 'ut of range', 'nvalid', 'not found')
fails = []


def check(ok, msg):
    print('%-5s %s' % ('ok' if ok else 'FAIL', msg))
    if not ok:
        fails.append(msg)


def p47(src, dst):
    subprocess.run(['rejig', '-o', dst, src], check=True, capture_output=True)


def testcopy(src, dst):
    L = [l for l in open(src, encoding='utf-8').read().split('\n') if l]
    out, i = [], 0
    while i < len(L):
        if re.fullmatch(r'PAUSE \d+', L[i]) and L[i + 1].startswith('KEY? ') and L[i + 2].startswith('GTO '):
            out += ['PAUSE 1', 'SNAP', 'α→x "TKS"', '→REAL', 'STO ' + L[i + 1][5:], 'DROP']
            i += 3
            continue
        out.append(L[i]); i += 1
    open(dst, 'w', encoding='utf-8').write('\n'.join(out) + '\n')


def bmp(fn):
    """The dark pixels of a SNAP (1 bit per pixel, BITMAPV4 header) as (x, row), row 0 = top."""
    b = open(fn, 'rb').read()
    off = struct.unpack_from('<I', b, 10)[0]; hs = 14 + struct.unpack_from('<I', b, 14)[0]
    w, h = struct.unpack_from('<ii', b, 18)
    dark = [sum(b[hs + 4 * i: hs + 4 * i + 3]) < 384 for i in range(2)]
    row = ((w + 31) // 32) * 4
    on = set()
    for y in range(abs(h)):
        r = b[off + row * y: off + row * (y + 1)]; yy = abs(h) - 1 - y if h > 0 else y
        on |= {(x, yy) for x in range(w) if dark[r[x // 8] >> (7 - x % 8) & 1]}
    return on


def run(prog, keys, regs=(), label='ELEM47'):
    """ELEM47 (or label) of prog in T47 with the keys; the screens, the registers asked, the error lines."""
    d = tempfile.mkdtemp(prefix='elem47fw_')
    try:
        testcopy(prog, os.path.join(d, 'E.txt'))
        t = ''.join(map(chr, keys)); parts = [t[i:i + 150] for i in range(0, len(t), 150)]
        body = ['"%s"' % parts[0]] + sum((['"%s"' % q, '+'] for q in parts[1:]), [])
        open(os.path.join(d, 'TSET.txt'), 'w', encoding='utf-8').write(
            '\n'.join(['LBL "TSET"'] + body + ['STO "TKS"', 'CLSTK', 'RTN', 'END']) + '\n')
        for f in ('E', 'TSET'):
            p47(os.path.join(d, f + '.txt'), os.path.join(d, f + '.p47'))
        tcl = ['readp %s/E.p47' % d, 'readp %s/TSET.p47' % d, 'xeq TSET']
        tcl += ['reg %02d %d' % (r, v) for r, v in regs] + ['xeq %s' % label, 'puts "X=[reg X]"']
        tcl += ['puts "R%02d=[reg %02d]"' % (r, r) for r, _ in regs] + ['puts "S%s=[reg %s]"' % (k, k) for k in 'XYZT']
        open(os.path.join(d, 't.tcl'), 'w').write('\n'.join(tcl) + '\n')
        r = subprocess.run([SIM, '--headless', '--reset', '--script', os.path.join(d, 't.tcl')], cwd=d,
                           capture_output=True, text=True, timeout=1800)
        out = (r.stdout + r.stderr).split('\n')
        shots = [bmp(f) for f in sorted(glob.glob(os.path.join(d, '*.bmp')))]
        got = {m.group(1): m.group(2).strip() for l in out for m in [re.match(r'([RS][\dXYZT]+)=(.*)', l)] if m}
        err = [l for l in out if any(w in l for w in ERRORS)]
        return shots, got, err
    finally:
        shutil.rmtree(d, ignore_errors=True)


def ltest():
    d = tempfile.mkdtemp(prefix='elem47fw_')
    try:
        p47(os.path.join(ROOT, 'tests', 'calc', 'LTEST.txt'), os.path.join(d, 'L.p47'))
        open(os.path.join(d, 't.tcl'), 'w').write('readp %s/L.p47\nxeq LTEST\nputs "X=[reg X]"\n' % d)
        r = subprocess.run([SIM, '--headless', '--reset', '--script', os.path.join(d, 't.tcl')], cwd=d,
                           capture_output=True, text=True, timeout=300)
        return next((l[2:].strip() for l in r.stdout.split('\n') if l.startswith('X=')), None)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    if not os.path.exists(SIM):
        print('no T47 (%s): build it (DEVELOPMENT_NOTES) or set C47SIM' % SIM)
        return 0
    quick = 'quick' in sys.argv[1:]
    check(ltest() == '196', 'LTEST: a 196-character text in a program, αLENG 196')
    moves = lambda ks: [k for k in ks if k not in (E.INFO, ANY)]
    rows = [[E.INFO, ANY, E.RIGHT if r % 2 == 0 else E.LEFT] * 18 + [E.INFO, ANY, E.DOWN] for r in range(10)]
    prog = os.path.join(ROOT, 'build', 'ELEM47.txt')
    boxes = back = same = total = 0
    for r0 in range(0, 2 if quick else 10, 2):
        lead = moves(sum(rows[:r0], []))
        keys = lead + rows[r0] + rows[r0 + 1] + [E.END]
        fw, _, err = run(prog, keys)
        py, _ = E.frames(keys, prog)
        total += len(py); same += sum(a == b for a, b in zip(fw, py)) if len(fw) == len(py) else 0
        seg = fw[len(lead):]
        for i in range(0, len(seg) - 2, 3):
            boxes += 1; back += seg[i] == seg[i + 2] and seg[i] != seg[i + 1]
        check(not err and len(fw) == len(py), 'rows %d-%d: %d screens, no error %s' % (r0 + 1, r0 + 2, len(fw), err[:2]))
    check(same == total, 'every screen the same as c47sim, pixel for pixel (%d of %d)' % (same, total))
    check(boxes and back == boxes, 'the detail box opened and closed %d times: the table back every time (%d)' % (boxes, back))
    keys = [E.RIGHT, E.DOWN, E.INFO, ANY, E.LEFT, E.INFO, ANY, E.END]
    a, _, _ = run(os.path.join(ROOT, 'build', 'ELEM47_num.txt'), keys)
    b, _, _ = run(prog, keys)
    check(a == b and len(a) == len(keys), 'build/ELEM47_num.txt: the same %d screens' % len(a))
    regs = [(r, 1000 + r) for r in range(100)]
    _, got, err = run(prog, [E.RIGHT, E.INFO, ANY, E.END], regs)
    clear = all(got.get('R%02d' % r) == '0' for r, _ in regs) and all(got.get('S' + k) == '0' for k in 'XYZT')
    check(clear and not err, 'the end: R00-R99 and the stack cleared (they held numbers before), no error %s' % err[:2])
    print('\n%s' % ('ALL OK' if not fails else '%d FAILED' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
