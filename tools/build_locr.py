#!/usr/bin/env python3
"""Dev build: ELEM47 works in local registers and gives the user's globals back.

The release (programs_rem/ELEM47.txt) does not save the globals. It writes R20-R55, keeps the key
in R33, and CLREGS at the end, so R00-R99 are gone. This build does not replace that file. It writes
build/dev/locr/ so the two versions sit side by side.

Why the working set can be local registers: on the C47 every XEQ starts a level with no local
registers (lblGtoXeq.c fnExecute), and KEY? refuses a local register. So the code of ELEM47 runs at
one level (LocR 48 at LBL "ELEM47"). An internal XEQ becomes a same-level call: ISG pushes a return
label, GTO enters the routine, and the routine's RTN is GTO to one return sequence that DSE-pops it.
XEQ "ELD1" / "ELD2" and XEQ IND of the symbol texts stay real XEQ (they only put a text in X).

The return label is a number, so it has to sit in X for a moment. On the 4-level stack the Python
simulator models, that push drops T. LBL :CLSEG: reads T (the first Z of the segment), so the call
saves T in R.47 and puts it back before the routine runs, and the return does the same. An 8-level
stack keeps X, Y, Z and T as well; only the bottom level is disturbed, and this program does not
read it.

R00 and R90-R97 are the only globals written: R00 is the key (KEY?) and the label ELD1/ELD2 execute,
R90-R97 are the return stack (eight deep; the call depth of this program is less). Both are copied
into local registers at the start and written back at key 0. There is no CLREGS. WSIZE 64 is still
left as the release leaves it. EXIT or R/S skips the copy back, same as any program that restores
on the way out.

A single-call routine whose body is one block (one RTN, no label inside, no GTO out) is inlined, so
it costs no call and no local label. LBL :FIELDK: counts down with DSE instead of 1 / STO- / GTO.

  python3 tools/build_locr.py
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from build_elem47 import programs, resolve          # noqa: E402

OUT = os.path.join(ROOT, 'build', 'dev', 'locr')
LIST = os.path.join(ROOT, 'listings', 'dev', 'locr')

# R20-R55 -> R.00-R.35. R33 is the key: KEY? has no local register, so the key lives in R00.
LOC = 48          # R.00-R.35 work, R.36 saved R00, R.37 pointer, R.38-R.45 saved R90-R97,
                  # R.46 the return label, R.47 the T that the call and the return put aside
PTR = 'R.37'
RETMP = 'R.46'    # the label number the return sequence jumps to
STMP = 'R.47'     # T, held while the return label is in X
STACK0 = 90       # return stack in R90-R97; the pointer starts at 89 and ISG moves it onto R90
INV = {
    'X=0?': 'X≠0?', 'X≠0?': 'X=0?', 'X<0?': 'X≥0?', 'X≥0?': 'X<0?',
    'X>0?': 'X≤0?', 'X≤0?': 'X>0?', 'X=Y?': 'X≠Y?', 'X≠Y?': 'X=Y?',
    'X<Y?': 'X≥Y?', 'X≥Y?': 'X<Y?', 'X>Y?': 'X≤Y?', 'X≤Y?': 'X>Y?',
}
NONREG = {'LBL', 'GTO', 'XEQ', 'PAUSE', 'WSIZE'}


def source_steps():
    path = os.path.join(ROOT, 'programs_rem', 'ELEM47.txt')
    lines = [ln.rstrip() for ln in open(path, encoding='utf-8')]
    steps = [ln for ln in lines if ln.strip() and not ln.startswith('REM')]
    return resolve(steps)


def lbls(steps):
    out = {}
    for i, s in enumerate(steps):
        m = re.fullmatch(r'LBL (\d+)', s)
        if m:
            out[int(m.group(1))] = i
    return out


def closed_span(steps, i):
    """LBL at i through its single RTN, when that RTN is the step before the next label and the
    body has no second RTN. None when the routine falls into another label or returns in two places."""
    rtn = None
    j = i + 1
    while j < len(steps):
        s = steps[j]
        if s.startswith('LBL ') or s == 'END':
            break
        if s == 'RTN':
            if rtn is not None:
                return None
            rtn = j
        j += 1
    if rtn is None or rtn != j - 1:
        return None
    return rtn


def falls_in(steps, i):
    """True when the step before this LBL can reach it without a jump."""
    if i == 0:
        return True
    prev = steps[i - 1]
    if prev in ('RTN', 'END'):
        return False
    if re.fullmatch(r'GTO \d+', prev):
        return i >= 2 and steps[i - 2].endswith('?')
    return True


def xeq_sites(steps, n):
    return [i for i, s in enumerate(steps) if s == 'XEQ %02d' % n]


def inline_pass(steps, names):
    """Inline one closed single-call routine. Returns (steps, note) or (steps, None)."""
    where = lbls(steps)
    for n, i in sorted(where.items(), key=lambda kv: closed_span(steps, kv[1]) or 10**9):
        if n < 2:
            continue
        rtn = closed_span(steps, i)
        if rtn is None or falls_in(steps, i):
            continue
        body = steps[i + 1:rtn]
        if any(re.fullmatch(r'GTO \d+', s) for s in body):
            continue
        if any(re.fullmatch(r'GTO %02d' % n, s) for s in steps):
            continue
        sites = xeq_sites(steps, n)
        if len(sites) != 1:
            continue
        call = sites[0]
        if i <= call <= rtn:
            continue
        cond = call > 0 and steps[call - 1].endswith('?')
        if cond and steps[call - 1] not in INV:
            raise SystemExit('no inverse for %s before XEQ %02d' % (steps[call - 1], n))
        if cond:
            repl = [INV[steps[call - 1]], 'GTO %02d' % n] + body + ['LBL %02d' % n]
        else:
            repl = list(body)
        skip = set(range(i, rtn + 1))
        out = []
        for k, s in enumerate(steps):
            if k in skip:
                continue
            if cond and k == call - 1:
                continue
            if k == call:
                out.extend(repl)
                continue
            out.append(s)
        note = ':%s: (%02d, %d steps%s)' % (names.get(n, '?'), n, len(body), ', conditional' if cond else '')
        return out, note
    return steps, None


def inline_all(steps, num):
    names = {v: k for k, v in num.items()}
    done = []
    while True:
        steps, note = inline_pass(steps, names)
        if note is None:
            return steps, done
        done.append(note)


def dse_fieldk(steps):
    """LBL :FIELDK: counted down with 1 / STO- / GTO. DSE is that countdown in one step."""
    out, i, n = [], 0, 0
    while i < len(steps):
        if (i + 2 < len(steps) and steps[i] == '1' and re.fullmatch(r'STO- \d+', steps[i + 1])
                and steps[i + 2].startswith('GTO ')):
            out.append('DSE ' + steps[i + 1].split()[1])
            out.append(steps[i + 2])
            i += 3
            n += 1
            continue
        out.append(steps[i])
        i += 1
    if n != 1:
        raise SystemExit('expected one FIELDK countdown, found %d' % n)
    return out


def map_reg(op, n):
    if n == 33:
        if op not in ('KEY?', 'RCL'):
            raise SystemExit('R33 is the key register, used by %s' % op)
        return '00'
    if 20 <= n <= 55:
        return 'R.%02d' % (n - 20)
    raise SystemExit('%s %02d is outside R20-R55' % (op, n))


def rename_regs(steps):
    out = []
    for s in steps:
        m = re.fullmatch(r'(\S+) (\d+)', s)
        ind = re.fullmatch(r'(XEQ|GTO|RCL|STO) IND (\d+)', s)
        if ind:
            op, n = ind.group(1), int(ind.group(2))
            if 20 <= n <= 55 or n == 33:
                out.append('%s IND %s' % (op, map_reg(op, n)))
            else:
                out.append(s)
            continue
        if m and m.group(1) not in NONREG and m.group(1) != 'IND':
            op, n = m.group(1), int(m.group(2))
            if 20 <= n <= 55 or n == 33:
                out.append('%s %s' % (op, map_reg(op, n)))
                continue
        out.append(s)
    return out


def prologue():
    """LocR, then the globals this level borrows. Each RCL is dropped: the stack at :INIT: stays
    the stack the user had, as the release leaves it."""
    p = ['LocR %d' % LOC]
    saved = [(0, 'R.36')] + [(90 + i, 'R.%02d' % (38 + i)) for i in range(8)]
    for g, loc in saved:
        p += ['RCL %02d' % g, 'STO ' + loc, 'DROP']
    p += ['%d' % (STACK0 - 1), 'STO ' + PTR, 'DROP']
    return p


def epilogue():
    p = []
    saved = [(0, 'R.36')] + [(90 + i, 'R.%02d' % (38 + i)) for i in range(8)]
    for g, loc in saved:
        p += ['RCL ' + loc, 'STO %02d' % g]
    return p


def insert_frame(steps):
    out = []
    for s in steps:
        out.append(s)
        if s == 'LBL "ELEM47"':
            out.extend(prologue())
        if s == 'CLREGS':
            out.pop()
            out.extend(epilogue())
        if s in ('XEQ "ELD1"', 'XEQ "ELD2"'):
            out.insert(-1, 'RCL R.23')   # the three steps sit in front of the XEQ just appended
            out.insert(-1, 'STO 00')
            out.insert(-1, 'DROP')
    if 'CLREGS' in out:
        raise SystemExit('CLREGS still in the dev program')
    if out.count('LocR %d' % LOC) != 1:
        raise SystemExit('LocR was not inserted once')
    return out


def call_depth(steps):
    """The deepest internal XEQ. A GTO keeps the depth (LBL :CLSEG: joins :SEGMENT: that way)."""
    lab = lbls(steps)
    n = len(steps)
    seen = set()
    best = 0
    stack = [(steps.index('LBL "ELEM47"'), 0, ())]
    while stack:
        i, depth, calls = stack.pop()
        if i >= n or (i, depth) in seen or depth > 12:
            best = max(best, min(depth, 12))
            continue
        seen.add((i, depth))
        best = max(best, depth)
        s = steps[i]
        if s in ('RTN', 'END'):
            continue
        if s.endswith('?') and not s.startswith('LBL'):
            stack.append((i + 1, depth, calls))
            stack.append((i + 2, depth, calls))
            continue
        m = re.fullmatch(r'XEQ (\d+)', s)
        if m:
            t = lab[int(m.group(1))]
            if t not in calls:
                stack.append((t, depth + 1, calls + (t,)))
            stack.append((i + 1, depth, calls))
            continue
        m = re.fullmatch(r'GTO (\d+)', s)
        if m:
            stack.append((lab[int(m.group(1))], depth, calls))
            continue
        stack.append((i + 1, depth, calls))
    return best


def convert_calls(steps):
    """Internal XEQ / RTN become ISG / DSE calls on the one LocR level. XEQ IND and XEQ "name" stay."""
    used = set(lbls(steps))
    free = [n for n in range(99, 1, -1) if n not in used]
    if not free:
        raise SystemExit('no free local label for the return sequence')
    ret = free.pop(0)

    def alloc():
        if not free:
            raise SystemExit('out of local labels (00-99)')
        return free.pop(0)

    protect = set()
    for i, s in enumerate(steps):
        if re.fullmatch(r'LBL 0[01]', s) and steps[i + 1].startswith('"') and steps[i + 2] == 'RTN':
            protect.add(i + 2)
        if s == 'CLSTK' and steps[i + 1] == 'RTN':
            protect.add(i + 1)
    if len(protect) != 3:
        raise SystemExit('expected the two symbol RTNs and the final RTN, found %d' % len(protect))

    # RCL T / STO / DROP parks T. The label is then stored and dropped, and RCL / R↓ puts T back
    # under X, Y, Z. DSE does not skip STO: the pointer stays above 0 (it starts at 89).
    block = ['LBL %02d' % ret, 'RCL T', 'STO ' + STMP, 'DROP',
             'RCL IND ' + PTR, 'DSE ' + PTR, 'STO ' + RETMP, 'DROP',
             'RCL ' + STMP, 'R↓', 'GTO IND ' + RETMP]
    out, calls = [], 0
    placed = False
    i = 0
    while i < len(steps):
        s = steps[i]
        if s == 'LBL 00' and not placed:
            out.extend(block)
            placed = True
        m = re.fullmatch(r'XEQ (\d+)', s)
        if m:
            target = int(m.group(1))
            back = alloc()
            seq = ['RCL T', 'STO ' + STMP, 'DROP',
                   'ISG ' + PTR, 'NOP', '%02d' % back, 'STO IND ' + PTR, 'DROP',
                   'RCL ' + STMP, 'R↓', 'GTO %02d' % target, 'LBL %02d' % back]
            if i > 0 and steps[i - 1].endswith('?'):
                if steps[i - 1] not in INV:
                    raise SystemExit('no inverse for %s' % steps[i - 1])
                out[-1] = INV[steps[i - 1]]
                skip = alloc()
                out.append('GTO %02d' % skip)
                out.extend(seq)
                out.append('LBL %02d' % skip)
            else:
                out.extend(seq)
            calls += 1
            i += 1
            continue
        if s == 'RTN' and i not in protect:
            out.append('GTO %02d' % ret)
            i += 1
            continue
        out.append(s)
        i += 1
    if not placed:
        raise SystemExit('the symbol LBL 00 was not found')
    if len(lbls(out)) != len(set(lbls(out))):
        raise SystemExit('a local label is defined twice')
    return out, ret, calls, len(free)


def build():
    steps, num = source_steps()
    prog = programs(steps)
    if len(prog) != 3:
        raise SystemExit('expected ELEM47, ELD1, ELD2')
    code, inlined = inline_all(prog[0], num)
    code = dse_fieldk(code)
    code = rename_regs(code)
    code = insert_frame(code)
    depth = call_depth(code)
    if depth > 8:
        raise SystemExit('call depth %d does not fit in R90-R97' % depth)
    code, ret, calls, left = convert_calls(code)
    eld = []
    for p in prog[1:]:
        eld.extend('XEQ IND 00' if s == 'XEQ IND 43' else s for s in p)
    if eld.count('XEQ IND 00') != 2:
        raise SystemExit('ELD1 and ELD2 should each execute XEQ IND 00')
    allsteps = code + eld
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(LIST, exist_ok=True)
    open(os.path.join(OUT, 'ELEM47.txt'), 'w', encoding='utf-8').write('\n'.join(allsteps) + '\n')
    listing = ['%4d  %s' % (i + 1, s) for i, s in enumerate(allsteps)]
    open(os.path.join(LIST, 'ELEM47_doc.txt'), 'w', encoding='utf-8').write('\n'.join(listing) + '\n')
    version = [
        'Elements 47 dev build: local registers (branch local-registers)',
        '',
        'Release build/ELEM47.txt is unchanged. This file is the same table with the working',
        'registers in R.00-R.35 (LocR %d at LBL "ELEM47").' % LOC,
        '',
        'Globals touched, and given back at key 0: R00 (the key, and the label ELD1/ELD2 run),',
        'R90-R97 (the return stack). No CLREGS. The other registers are not written.',
        'EXIT or R/S does not run the copy back.',
        'Each internal call parks T in R.47 while the return label is in X, then puts T back.',
        '',
        'Inlined (one call, one block): ' + (', '.join(inlined) if inlined else 'none'),
        'Internal calls still done with ISG / DSE: %d. Return sequence: LBL %02d.' % (calls, ret),
        'Deepest internal call: %d (the return stack holds 8). Local labels left free: %d.' % (depth, left),
        'LBL :FIELDK: counts down with DSE.',
        '',
        'R20-R55 of the release are R.00-R.35 here, in the same order. R33 (the key) is R00.',
        'Steps: ELEM47 %d, ELD1 %d, ELD2 %d.' % (len(code), len(prog[1]), len(prog[2])),
    ]
    open(os.path.join(OUT, 'VERSION.txt'), 'w', encoding='utf-8').write('\n'.join(version) + '\n')
    p47 = os.path.join(OUT, 'ELEM47.p47')
    r = subprocess.run(['rejig', '-o', p47, os.path.join(OUT, 'ELEM47.txt')], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit('rejig failed (%d)' % r.returncode)
    print('\n'.join(version))
    print('rejig -> %s (%d bytes)' % (p47, os.path.getsize(p47)))
    return allsteps


if __name__ == '__main__':
    build()
