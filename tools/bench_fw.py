#!/usr/bin/env python3
"""bench_fw.py - the speed of ELEM47 in the C47 firmware: the CPU instructions (perf stat, user space) of T47
running it, minus those of a run of an empty program (T47's start). Deterministic to about 0.1 %.
  table  the table drawn, then 0
  moves  46 cursor moves (the whole of row 1 to 18 and back, 6 down, 6 up)
  boxes  the detail box opened and closed 6 times (rows 1-7)
  inbox  the moves of 'moves' with the detail box open (5 first, 5 at the end)
The key waits (PAUSE / KEY? / GTO, or DO / PAUSE / KEY? / WHILE / ENDDO) are replaced by the next key from the text TKS (as tests/test_fw.py, without PAUSE and SNAP).
Needs T47 (tests/test_fw.py, DEVELOPMENT_NOTES) and perf.
  python3 tools/bench_fw.py [build/ELEM47.txt]"""
import os, re, subprocess, sys, tempfile, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tests')]
import elem47sim as E
import test_fw as F
SIM = F.SIM

def copy(src, dst):
    L = [l for l in open(src, encoding='utf-8').read().split('\n') if l]
    out, i = [], 0
    while i < len(L):
        if re.fullmatch(r'PAUSE \d+', L[i]) and L[i + 1].startswith('KEY? ') and L[i + 2].startswith('GTO '):
            out += ['α→x "TKS"', '→REAL', 'STO ' + L[i + 1][5:], 'DROP']; i += 3; continue
        # branch struct: DO n / PAUSE / KEY? r / WHILE n / ENDDO n
        m = re.fullmatch(r'DO (\d+)', L[i])
        if m and i + 4 < len(L) and re.fullmatch(r'PAUSE \d+', L[i + 1]) and L[i + 2].startswith('KEY? ') \
                and L[i + 3:i + 5] == ['WHILE ' + m.group(1), 'ENDDO ' + m.group(1)]:
            out += ['α→x "TKS"', '→REAL', 'STO ' + L[i + 2][5:], 'DROP']; i += 5; continue
        out.append(L[i]); i += 1
    open(dst, 'w', encoding='utf-8').write('\n'.join(out) + '\n')

def count(prog, keys, label='ELEM47'):
    d = tempfile.mkdtemp(prefix='e47b_')
    try:
        copy(prog, d + '/E.txt')
        t = ''.join(map(chr, keys)); parts = [t[i:i + 150] for i in range(0, len(t), 150)]
        body = ['"%s"' % parts[0]] + sum((['"%s"' % q, '+'] for q in parts[1:]), [])
        open(d + '/TSET.txt', 'w').write('\n'.join(['LBL "TSET"'] + body + ['STO "TKS"', 'CLSTK', 'RTN', 'LBL "NOP"', 'RTN', 'END']) + '\n')
        for f in ('E', 'TSET'):
            F.p47(d + '/%s.txt' % f, d + '/%s.p47' % f)
        open(d + '/t.tcl', 'w').write('readp %s/E.p47\nreadp %s/TSET.p47\nxeq TSET\nxeq %s\nputs "X=[reg X]"\n' % (d, d, label))
        r = subprocess.run(['perf', 'stat', '-x,', '-e', 'instructions:u', SIM, '--headless', '--reset', '--script', d + '/t.tcl'],
                           cwd=d, capture_output=True, text=True, timeout=1800)
        err = [l for l in (r.stdout).split('\n') if any(w in l for w in F.ERRORS)]
        n = int(next(l for l in r.stderr.split('\n') if 'instructions' in l).split(',')[0])
        return n, err
    finally:
        shutil.rmtree(d, ignore_errors=True)

R, L, U, D, I, A, Q = E.RIGHT, E.LEFT, E.UP, E.DOWN, E.INFO, F.ANY, E.END
SCRIPTS = {
    'table': [Q],
    'moves': [R] * 17 + [D] * 6 + [L] * 17 + [U] * 6 + [Q],
    'boxes': sum(([I, I] + [R] * 3 + [D] for _ in range(6)), []) + [Q],
    'inbox': [I] + [R] * 17 + [D] * 6 + [L] * 17 + [U] * 6 + [I, Q],
}
if __name__ == '__main__':
    prog = sys.argv[1] if len(sys.argv) > 1 else ROOT + '/build/ELEM47.txt'
    base = min(count(prog, [Q], 'NOP')[0] for _ in range(2))
    res = {}
    for k, ks in SCRIPTS.items():
        n, err = count(prog, ks)
        res[k] = n - base
        print('%-6s %8.1f M  %s' % (k, res[k] / 1e6, err[:1]))
    print('moves-table %.1f M, boxes-table %.1f M' % ((res['moves'] - res['table']) / 1e6, (res['boxes'] - res['table']) / 1e6))
