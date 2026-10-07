#!/usr/bin/env python3
"""test_dev.py - the development programs (build/dev/, tools/build_dev.py), apart from the release.
  - build/dev/ is up to date with programs_rem/dev/
  - ELEM47P: the table, the cursor (6 and 4, 118 goes to 1), the info box and the cells under it drawn
    again when it closes, 0 the end; in python/c47sim.py and, when T47 is there (tests/test_fw.py), the
    same screens in the C47 firmware pixel for pixel
  - build/dev/dev_test/ELEM47_H.txt (prototype 1, kept for reference): runs, the same in T47
  python3 tests/test_dev.py"""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'python'), os.path.join(ROOT, 'tests')]
import elem47sim as E                                                  # noqa: E402
import test_fw as F                                                    # noqa: E402

PROG = os.path.join(ROOT, 'build', 'dev', 'ELEM47P.txt')
fails = []


def check(ok, msg):
    print('%-5s %s' % ('ok' if ok else 'FAIL', msg))
    if not ok:
        fails.append(msg)


def main():
    before = open(PROG, encoding='utf-8').read()
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build_dev.py')], check=True, capture_output=True)
    check(open(PROG, encoding='utf-8').read() == before, 'build/dev/ELEM47P.txt up to date with programs_rem/dev/')
    keys = [E.INFO, F.ANY, E.RIGHT, E.RIGHT, E.INFO, F.ANY, E.LEFT, E.LEFT, E.LEFT, E.INFO, F.ANY, E.END]
    py, c = E.frames(keys, PROG, label='ELEM47P')
    check(len(py) == len(keys), 'ELEM47P in c47sim: %d screens for %d keys' % (len(py), len(keys)))
    # 5 then a key: the screen before the box comes back (H, Li, Og after 4 from H)
    back = [py[i] == py[i + 2] and py[i] != py[i + 1] for i in (0, 4, 9)]
    check(all(back), 'the info box closed: the table back as it was, each time %s' % back)
    check(py[0] != py[9], 'the cursor moved (4 from H goes round to Og)')
    check(getattr(c, 'grfnt', 20) == 20 and getattr(c, 'grmod', 0) == 0, '0: GRFNT 20 and GRMOD 0 restored')
    h = os.path.join(ROOT, 'build', 'dev', 'dev_test', 'ELEM47_H.txt')
    hk = [85, F.ANY, E.END]
    hp, _ = E.frames(hk, h)
    check(len(hp) == 3 and hp[0] == hp[2] != hp[1], 'dev_test/ELEM47_H (prototype 1): H, + the box, a key back')
    if os.path.exists(F.SIM):
        hf, _, err = F.run(h, hk)
        check(hf == hp and not err, 'dev_test/ELEM47_H in the C47 firmware (T47): the same 3 screens')
        fw, _, err = F.run(PROG, keys, label='ELEM47P')
        same = len(fw) == len(py) and all(a == b for a, b in zip(fw, py))
        check(same and not err, 'ELEM47P in the C47 firmware (T47): the same %d screens, no error %s' % (len(fw), err[:2]))
    else:
        print('--    no T47 (%s): firmware run skipped' % F.SIM)
    print('\n%s' % ('ALL OK' if not fails else '%d FAILED' % len(fails)))
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
