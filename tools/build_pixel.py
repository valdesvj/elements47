#!/usr/bin/env python3
"""Build the variant of branch struct-pixel: programs_rem/pixel/ELEM47.txt (the release with the horizontal
lines of the table drawn by PIXEL, full rows, and the parts without cells cleared again) -> build/pixel/ELEM47.txt, listings/pixel/. The release files
(programs/, build/ELEM47.txt, listings/) are not touched. Same global labels as the release (ELEM47,
ELD1, ELD2): load one of the two on the calculator.
  python3 tools/build_pixel.py
  ELEM47_PROG=build/pixel/ELEM47.txt python3 tests/test_opt.py     (the screens of the variant)"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_elem47 as B

if __name__ == '__main__':
    st, num = B.build('pixel')
    for p in B.programs(st):
        print('%-8s %5d steps, %2d local labels  about %5d bytes (.p47, estimated)' % (
            p[0][5:-1], len(p), sum(1 for s in p if re.match(r'LBL (\d\d|:)', s)), B.estimate(p)))
    print('build/pixel/ELEM47.txt')
