#!/usr/bin/env python3
"""Build the ELEM47 files from the commented source programs_rem/ELEM47.txt:
  programs/ELEM47.txt        the program without REM lines (to convert with rejig)
  build/ELEM47.txt           the calculator file (the same steps for now)
  listings/ELEM47_doc.txt    numbered steps with the comments, for reading and debugging
                             (step numbers = line numbers of the plain program)
  python3 tools/build_elem47.py"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = 'ELEM47'


def build():
    src = os.path.join(ROOT, 'programs_rem', NAME + '.txt')
    lines = [ln.rstrip() for ln in open(src, encoding='utf-8')]
    steps, listing = [], []
    for ln in lines:
        if not ln.strip():
            continue
        if ln.startswith('REM'):
            listing.append('      ; ' + ln[3:].strip())
        else:
            steps.append(ln)
            listing.append('%4d  %s' % (len(steps), ln))
    plain = '\n'.join(steps) + '\n'
    for d in ('programs', 'build'):
        with open(os.path.join(ROOT, d, NAME + '.txt'), 'w', encoding='utf-8') as fh:
            fh.write(plain)
    with open(os.path.join(ROOT, 'listings', NAME + '_doc.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(listing) + '\n')
    return len(steps)


if __name__ == '__main__':
    print('%s: %d steps' % (NAME, build()))
