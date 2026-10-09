#!/usr/bin/env python3
"""The local-register dev build against the release, pixel for pixel.

build/dev/locr/ is rebuilt (tools/build_locr.py). The release build/ELEM47.txt is not.
The screens of the two programs are compared for the same keys. The dev build must give
R00-R99 back at key 0. Step counts are printed; a slower dev build is not a failure.

  python3 tests/test_locr.py
  python3 tests/test_locr.py --fw     the same screens in T47 (one short tour and the registers)
"""
import os, re, sys
from decimal import Decimal as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'tests')]
import elem47sim as E                                                  # noqa: E402
import build_locr                                                      # noqa: E402
import test_opt as opt                                                 # noqa: E402

REL = os.path.join(ROOT, 'build', 'ELEM47.txt')
DEV = os.path.join(ROOT, 'build', 'dev', 'locr', 'ELEM47.txt')
SRC = os.path.join(ROOT, 'programs_rem', 'ELEM47.txt')
REGOP = re.compile(
    r'^(?:RCL|STO|STO\+|STO-|STO×|STO÷|KEY\?|αIP|αPOS|αSL|αLEFT|x→α|α→𝑥|AGRAPH|ATEXT)'
    r'(?: IND)? (\d+)$')
fails = []


def check(ok, msg):
    print('%-5s %s' % ('ok' if ok else 'FAIL', msg))
    if not ok:
        fails.append(msg)


def code_lines(path):
    return [ln.strip() for ln in open(path, encoding='utf-8')
            if ln.strip() and not ln.startswith('REM')]


def end_ok(c):
    return (c.keys == [] and getattr(c, 'grfnt', 20) == 20 and getattr(c, 'grmod', 0) == 0
            and 'PT' not in c.mats and all(v == 0 for v in c.s))


def main():
    rel_src = code_lines(SRC)
    check('CLREGS' in rel_src and not any(ln.startswith('LocR') for ln in rel_src),
          'release source: CLREGS at the end, no LocR, globals not saved')
    before = open(REL, encoding='utf-8').read()
    build_locr.build()
    check(open(REL, encoding='utf-8').read() == before, 'build/ELEM47.txt unchanged by the dev build')
    dev = code_lines(DEV)
    check('LocR 48' in dev and 'CLREGS' not in dev, 'dev program: LocR 48, no CLREGS')
    used = sorted({int(m.group(1)) for ln in dev if (m := REGOP.match(ln))})
    check(used == [0] + list(range(90, 98)),
          'dev program writes only R00 and R90-R97 %s' % used)

    runs = dict(opt.RUNS)
    runs['close'] = [E.DOWN, E.RIGHT, E.INFO, E.RIGHT, E.INFO, E.END]
    runs['inbox'] = [E.DOWN, E.RIGHT, E.RIGHT, E.INFO, E.RIGHT, E.DOWN, E.LEFT, E.INFO, E.END]
    counts = {}
    for name, keys in runs.items():
        a, ca = E.frames(keys, REL)
        b, cb = E.frames(keys, DEV)
        bad = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), None)
        same = len(a) == len(b) and bad is None
        check(same, '%-12s %2d screens the same as the release%s' % (
            name, len(b), '' if same else ' (first difference: screen %d)' % bad))
        check(end_ok(cb), '%-12s the end: GRFNT 20, GRMOD 0, PT deleted, stack cleared' % name)
        counts[name] = (ca.at_steps, cb.at_steps)

    mine = {str(i): D(1000 + i) for i in range(100)}
    _, c = E.frames(runs['close'], DEV, regs=dict(mine))
    bad = [i for i in range(100) if c.reg.get(str(i), D(0)) != mine[str(i)]]
    check(not bad and end_ok(c), 'key 0 gives R00-R99 back %s' % bad[:8])

    print('\nsteps at each key (release -> dev):')
    for name, (rs, ds) in counts.items():
        print('  %-12s %7d -> %7d  (%+d)' % (name, rs[-1], ds[-1], ds[-1] - rs[-1]))
    rs, ds = counts['close']
    names = ('table', 'down', 'right', 'detail', 'box move', 'close')
    print('  close, each key:')
    prev = (0, 0)
    for name, r, d in zip(names, rs, ds):
        print('    %-8s %6d -> %6d  (%+d)' % (name, r - prev[0], d - prev[1], (d - prev[1]) - (r - prev[0])))
        prev = (r, d)

    if '--fw' in sys.argv[1:]:
        import test_fw as F                                           # noqa: E402
        if not os.path.exists(F.SIM):
            check(False, 'no T47 at %s' % F.SIM)
        else:
            for name in ('close', 'inbox'):
                fw, _, err = F.run(DEV, runs[name])
                py, _ = E.frames(runs[name], DEV)
                bad = next((i for i, (x, y) in enumerate(zip(fw, py)) if x != y), None)
                same = not err and len(fw) == len(py) and bad is None
                check(same, 'T47 %-8s %d screens the same as c47sim%s %s' % (
                    name, len(py), '' if bad is None else ' (screen %d)' % bad, err[:2]))
            regs = [(r, 1000 + r) for r in range(100)]
            _, got, err = F.run(DEV, runs['close'], regs)
            def num(s):
                return (s or '').replace(',', '').replace(' ', '')
            bad = [r for r, _ in regs if num(got.get('R%02d' % r)) not in ('%d' % (1000 + r), '%d.' % (1000 + r))]
            stack = [k for k in 'XYZT' if num(got.get('S' + k)) not in ('0', '0.')]
            check(not bad and not stack and not err,
                  'T47 key 0: R00-R99 back, stack cleared %s %s %s' % (bad[:8], stack, err[:2]))
    print('\n%s' % ('ALL OK' if not fails else '%d FAILED' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
