#!/usr/bin/env python3
"""test_f42.py - ELEM47 for Free42 (build/free42/, tools/build_free42.py) against the C47 screens.
f42run (Almanac 47's headless Free42 3.3 core: ~/opt/almanac47/tools/f42/f42run, or F42RUN) runs it
with the keys; a screen at every key wait (GETKEY), compared with python/c47sim.py pixel by pixel:
  - build/free42/ is up to date with programs_rem/ELEM47.txt
  - every command survives Free42 Paste (it leaves out the steps it does not know)
  - the whole table, every row both ways, the detail box opened and closed at each cell
  - the end: the registers and the stack cleared (CLRG, CLST); SIZE 30 becomes 76 (R20-R51, R60-R75 for
    E47T, E47S and E47B); five programs: ELEM47, ELD1, ELD2, E47T (with E47B), E47S
  python3 tests/test_f42.py"""
import os, re, subprocess, sys, tempfile, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python')]
import elem47sim as E                                                  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import build_free42 as BF                                              # noqa: E402

F42 = os.environ.get('F42RUN', os.path.expanduser('~/opt/almanac47/tools/f42/f42run'))
PROG = os.path.join(ROOT, 'build', 'free42', 'ELEM47.txt')
KM = {E.UP: 20, E.DOWN: 30, E.LEFT: 24, E.RIGHT: 26, E.INFO: 25, E.END: 34, 72: 29}    # C47 -> GETKEY
ANY = 72
fails = []


def check(ok, msg):
    print('%-5s %s' % ('ok' if ok else 'FAIL', msg))
    if not ok:
        fails.append(msg)


def pbm(fn):
    t = open(fn).read().split()
    w, px = int(t[1]), ''.join(t[3:])
    return {(i % w, i // w) for i, c in enumerate(px) if c == '1'}


def f42(cmds, d):
    r = subprocess.run([F42], input='\n'.join(cmds) + '\n', capture_output=True, text=True, timeout=1800, cwd=d)
    return r.stdout + r.stderr


def screens(keys, d, pre=()):
    cmds = ['paste %s' % PROG] + list(pre) + ['xeq ELEM47', 'shot s000.pbm']
    for i, k in enumerate(keys):
        cmds.append('key %d' % KM[k])
        if k != E.END:
            cmds.append('shot s%03d.pbm' % (i + 1))
    out = f42(cmds, d)
    return [pbm(os.path.join(d, 's%03d.pbm' % i)) for i in range(len(keys))], out


def pasted(d):
    """Every distinct command of the file, pasted in one program and listed back."""
    ops = []
    for s in open(PROG, encoding='utf-8').read().split('\n'):
        if not s or s == 'END' or s.startswith(('"', '├"', 'XSTR "', 'LBL "')) or re.fullmatch(r'-?[\d.]+', s) \
                or re.fullmatch(r'(LBL|GTO|XEQ) \d\d', s) or s in ops:
            continue
        ops.append(s)
    open(os.path.join(d, 'O.txt'), 'w', encoding='utf-8').write('\n'.join(['LBL "OO"'] + ops + ['END']) + '\n')
    out = f42(['paste O.txt', 'list 0'], d)
    got = {re.sub(r'\s+', '', re.sub(r'^\s*\d+[ ▸]', '', l)) for l in out.split('\n') if re.match(r'\s*\d+[ ▸]', l)}
    return [o for o in ops if re.sub(r'\s+', '', o) not in got], len(ops)


def main():
    if not os.path.exists(F42):
        print('no f42run (%s): set F42RUN' % F42)
        return 0
    before = open(PROG, encoding='utf-8').read()
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build_free42.py')], check=True, capture_output=True)
    check(open(PROG, encoding='utf-8').read() == before, 'build/free42/ELEM47.txt up to date with programs_rem/ELEM47.txt')
    d = tempfile.mkdtemp(prefix='elem47f42_')
    try:
        prog = open(PROG, encoding='utf-8').read().split('\n')
        check([x for x in prog if x.startswith('LBL "')] == ['LBL "ELEM47"', 'LBL "ELD1"', 'LBL "ELD2"', 'LBL "E47T"',
                                                               'LBL "E47B"', 'LBL "E47S"']
              and prog.count('END') == 5, 'five programs: ELEM47, ELD1, ELD2, E47T (with E47B), E47S')
        miss, n = pasted(d)
        check(not miss, 'Free42 Paste keeps all %d different commands %s' % (n, miss[:4]))
        rows = [[E.INFO, E.INFO, E.RIGHT if r % 2 == 0 else E.LEFT] * 18 + [E.INFO, E.INFO, E.DOWN] for r in range(10)]
        keys = sum(rows, []) + [E.END]
        fs, out = screens(keys, d)
        py, _ = E.frames(keys)
        same = sum(a == b for a, b in zip(fs, py))
        check(len(fs) == len(py) and same == len(py), 'the whole table both ways: %d of %d screens the same as the C47' % (same, len(py)))
        back = sum(fs[i] == fs[i + 2] != fs[i + 1] for i in range(0, len(fs) - 2, 3))
        check(back == 190, 'the detail box opened and closed 190 times: the table back each time (%d)' % back)
        # inside the box: the arrows (the box of each element on the way), 5 closes it
        bk = [E.INFO] + [E.RIGHT] * 17 + [E.DOWN] * 8 + [E.LEFT] * 17 + [E.UP] * 8 + [E.INFO, E.END]
        fs, out = screens(bk, d)
        py, _ = E.frames(bk)
        check(fs == py, 'moves inside the detail box (every cell), 5: %d screens the same as the C47' % len(py))
        # your registers: SIZE 100, R00-R99 marked; then SIZE 30
        for size in (100, 30):
            setp = os.path.join(d, 'S.txt')
            open(setp, 'w').write('\n'.join(['LBL "ESET"', 'SIZE %d' % size] + sum(
                (['%d' % (1000 + r), 'STO %02d' % r] for r in range(size)), []) + ['END']) + '\n')
            dimp = os.path.join(d, 'D.txt')
            open(dimp, 'w').write('LBL "EDIM"\nRCL "REGS"\nDIM?\nEND\n')
            n = max(size, BF.SIZE)
            out = f42(['paste %s' % PROG, 'paste S.txt', 'paste D.txt', 'xeq ESET', 'xeq ELEM47', 'key 26', 'key 25',
                       'key 25', 'key 34', 'stack', 'regs 0 %d' % (n - 1), 'xeq EDIM', 'stack'], d)
            regs = {m.group(1): m.group(2) for m in re.finditer(r'R(\d\d) (\S+)', out)}
            st = re.findall(r'([XYZT]): (\S+)', out)[:4]
            y = re.findall(r'Y: (\S+)', out)[-1]
            clear = all(regs.get('%02d' % r) == '0' for r in range(n)) and all(float(v) == 0 for _, v in st)
            check(clear and float(y) == n, 'SIZE %d: the end: R00-R%02d and the stack cleared, SIZE %d' % (size, n - 1, n))
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print('\n%s' % ('ALL OK' if not fails else '%d FAILED' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
