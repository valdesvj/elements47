#!/usr/bin/env python3
"""build_p47.py - the calculator files (.p47) of Elements 47, made with rejig on your own computer.

  python3 tools/build_p47.py            every program below -> build/p47/NAME.p47 (not in git: *.p47 is ignored)
  python3 tools/build_p47.py NAME ...   only those

For each program rejig converts the commented forum file (build/p47u/NAME.p47u: its '@' lines and the comments
after ';' are not compiled) with --validate=r47 (C47 / R47), and, when there is one, the plain listing too
(build/NAME.txt, the steps only); the two .p47 must be the same bytes: the comments take no memory and no REM
step slipped in. Copy build/p47/*.p47 to the calculator's PROGRAMS folder and load them (or load the .p47u in a
C47 that reads them). Run the build first (python3 tools/build_pixel.py && python3 tools/build_p47u.py) so build/ is up to date.
Needs rejig on the PATH (or REJIG=/path/to/rejig)."""
import filecmp, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'build', 'p47')
# NAME: (the commented forum file, the plain listing or None), paths from the repository's root
PROGRAMS = {
    'ELEM47': ('build/p47u/ELEM47.p47u', 'build/pixel/ELEM47.txt'),
}


def rejig(src, dst):
    exe = os.environ.get('REJIG') or shutil.which('rejig')
    if not exe:
        raise SystemExit('rejig not found: put it on the PATH or set REJIG=/path/to/rejig')
    r = subprocess.run([exe, '--validate=r47', '-o', dst, src], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('rejig %s:\n%s%s' % (os.path.relpath(src, ROOT), r.stdout, r.stderr))
    return r.stdout.strip()


def main(names):
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    for name in names or list(PROGRAMS):
        forum, plain = PROGRAMS[name]
        src = os.path.join(ROOT, forum)
        if not os.path.exists(src):
            print('%-8s  no %s: run %s first' % (name, forum, 'python3 tools/build_pixel.py && python3 tools/build_p47u.py')); bad += 1; continue
        dst = os.path.join(OUT, name + '.p47')
        msg = rejig(src, dst)
        same = ''
        if plain and os.path.exists(os.path.join(ROOT, plain)):
            with tempfile.TemporaryDirectory() as d:
                tmp = os.path.join(d, name + '.p47')
                rejig(os.path.join(ROOT, plain), tmp)
                ok = filecmp.cmp(dst, tmp, shallow=False)
                same = '  = %s' % plain if ok else '  DIFFERS from %s (a comment became a step?)' % plain
                bad += not ok
        print('%-8s  build/p47/%s.p47  %6d bytes%s%s' % (name, name, os.path.getsize(dst), same,
                                                     ('  (' + msg + ')') if msg else ''))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
