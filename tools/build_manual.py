#!/usr/bin/env python3
"""build_manual.py - the user's manual: MANUAL.md (GitHub) and MANUAL.html (the release zip, offline), the same
text, with the screens of docs/ (python/elem47sim.py writes the first ones, this tool the two below).
  docs/ELEM47_wrap_fr.png     H, 8: around the top edge to Fr
  docs/ELEM47_detail_co.png   the box of Fe open, 6: the box of Co
  python3 tools/build_manual.py"""
import html, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'python'))
import elem47sim as E

VERSION = '1.1.0'
TEXT = '''# Elements 47 v%s: user's manual

The periodic table of the 118 elements on the C47 / R47: the table on one screen, a cursor you move with the
digit keys, and a detail box for each element.

## Install

- You need a C47 or R47 with the firmware 00.109.05.00a0.ALPHA (5 Oct 2026) or later: it has the
  structured programming commands (IF, DO, REPEAT: app note AN0007), ATEXT, GRFNT and PIXEL.
- From the release zip, copy `C47_R47/ELEM47.p47` to the calculator (USB disk) and load it as any other
  program. It holds three programs: `ELEM47` (the one you run), `ELD1` and `ELD2` (the element data).
- **Before you run it:** at the end ELEM47 clears the registers R00-R99 and the stack. Keep anything you need
  somewhere else first.

## Start

`XEQ "ELEM47"`. After a few seconds the table is on the screen, the cursor on H (hydrogen).

![The table at the start, the cursor on H](docs/ELEM47_table.png)

- Rows 1-7 are the periods, the two rows below them the lanthanides and the actinides.
- Each cell shows the atomic number (small) and the symbol.
- The empty part of periods 1-3 shows the title, the selected element (name, atomic number, standard atomic
  weight) and the keys: the digit keys on the left, what they do on the right.

## Move the cursor

| Key | |
|---|---|
| **8** | up |
| **2** | down |
| **4** | left |
| **6** | right |

The cursor jumps over empty cells, and the panel shows the new element. Three times **2** and seven times
**6** from H:

![The cursor on Fe (iron)](docs/ELEM47_fe.png)

At an edge the cursor goes around to the other side: **8** on H goes to the bottom of column 1, Fr; **4** on
H goes to He; **2** on Ac goes up to Sc.

![H, then 8: around the top edge to Fr](docs/ELEM47_wrap_fr.png)

## The detail box

**5** opens the box of the element under the cursor: symbol, standard atomic weight, state at room
temperature, boiling point, group with its name, and the electron configuration.

![The detail box of Fe](docs/ELEM47_detail_fe.png)

With the box open, **8 4 6 2** move the cursor as before and the box shows the new element at once
(here **6**: from Fe to Co). **5** closes the box, **0** ends; other keys are ignored.

![The box of Fe, then 6: the box of Co](docs/ELEM47_detail_co.png)

The longest configuration, Og (oganesson):

![The detail box of Og](docs/ELEM47_detail_og.png)

"-" in a field: no value (the 34 elements without a standard atomic weight, or no data in PubChem).

## End

**0** ends ELEM47: the normal calculator screen comes back, with R00-R99 and the stack cleared and the
matrix PT (the table's map) deleted.

## Keys

| Key | Table | Detail box open |
|---|---|---|
| **8 4 6 2** | move the cursor | move, the box of the new element |
| **5** | open the box | close the box |
| **0** | end | end |

## Where the data come from

Standard atomic weights: IUPAC / CIAAW 2024 (abridged, as on the IUPAC periodic table). State, boiling point,
electron configuration: the PubChem periodic table. See `NOTICE`.

## Which calculators

ELEM47 needs three commands of the C47 firmware: the structured programming commands (IF, DO, REPEAT),
ATEXT and GRFNT.

- **R47 and DM42n** with the C47 firmware 00.109.05.00a0.ALPHA (5 Oct 2026) or later: yes.
- **Older C47 firmware** (00.109.04.00b0 and earlier): no, it has none of the three.
- **Original DM42 (not n) with the C47 firmware: not supported.** Its firmware is cut down to fit its flash. In
  00.109.05.00a0.ALPHA, packages 1-3 have the structured commands but only 10 IF, 10 DO and 10 REPEAT per
  program (ELEM47 has 11 IF), and package 4 has none. Later builds have switched them, ATEXT and GRFNT out and in
  again, so this can change with each release. Nobody has tried ELEM47 on an original DM42 yet.
- **DM42 / DM42n with the stock firmware, or Free42:** use the release v1.0.0 (`Free42_DM42/ELEM47.raw`):
  the same table and keys, without going around the edges.
''' % VERSION


def screens():
    """The two screens of the manual that docs/ does not have yet (the other ones: elem47sim, test_elem47)."""
    s, _ = E.frames([E.UP, E.END])
    E.png(os.path.join(ROOT, 'docs', 'ELEM47_wrap_fr.png'), s[1])
    s, _ = E.frames([E.DOWN] * 3 + [E.RIGHT] * 7 + [E.INFO, E.RIGHT, E.END])
    E.png(os.path.join(ROOT, 'docs', 'ELEM47_detail_co.png'), s[12])


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    return re.sub(r'`(.+?)`', r'<code>\1</code>', t)


def to_html(md):
    """The little Markdown of TEXT: headings, paragraphs, lists, images on their own line, tables."""
    out, para, items, rows = [], [], [], []

    def flush():
        if para:
            out.append('<p>%s</p>' % inline(' '.join(para))); para.clear()
        if items:
            out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % inline(i) for i in items)); items.clear()
        if rows:
            head, body = rows[0], [r for r in rows[2:]]
            out.append('<table><tr>%s</tr>%s</table>' % (''.join('<th>%s</th>' % inline(c) for c in head),
                       ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r) for r in body)))
            rows.clear()
    for ln in md.split('\n'):
        m = re.fullmatch(r'(#+) (.*)', ln)
        img = re.fullmatch(r'!\[(.*)\]\((.*)\)', ln)
        if m:
            flush(); n = len(m.group(1)); out.append('<h%d>%s</h%d>' % (n, inline(m.group(2)), n))
        elif img:
            flush(); out.append('<figure><img src="%s" alt="%s"><figcaption>%s</figcaption></figure>'
                                % (img.group(2), html.escape(img.group(1)), html.escape(img.group(1))))
        elif ln.startswith('|'):
            if para or items:
                flush()
            rows.append([c.strip() for c in ln.strip('|').split('|')])
        elif ln.startswith('- '):
            if para or rows:
                flush()
            items.append(ln[2:])
        elif ln.startswith('  ') and items:
            items[-1] += ' ' + ln.strip()
        elif not ln.strip():
            flush()
        else:
            if items or rows:
                flush()
            para.append(ln)
    flush()
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Elements 47 manual</title>
<style>
:root { --bg: #fff; --fg: #1d1d1b; --muted: #5c5c57; --line: #d6d6cf; --code: #f1f1ec; }
@media (prefers-color-scheme: dark) { :root { --bg: #181816; --fg: #e8e8e2; --muted: #a5a59c; --line: #3a3a35; --code: #26261f; } }
body { background: var(--bg); color: var(--fg); font: 16px/1.55 system-ui, sans-serif; margin: 0 auto;
       max-width: 46rem; padding: 1.5rem 16px 3rem; }
h1 { font-size: 1.7rem; line-height: 1.25; } h2 { margin-top: 2.2rem; border-bottom: 1px solid var(--line); }
img { max-width: 100%%; height: auto; border: 1px solid var(--line); border-radius: 4px; }
figure { margin: 1rem 0 1.4rem; } figcaption { color: var(--muted); font-size: .9rem; margin-top: .3rem; }
code { background: var(--code); padding: 0 .25em; border-radius: 3px; }
table { border-collapse: collapse; margin: .8rem 0; } th, td { border: 1px solid var(--line); padding: .3rem .7rem; text-align: left; }
</style></head><body>
%s
</body></html>
''' % '\n'.join(out)


if __name__ == '__main__':
    screens()
    open(os.path.join(ROOT, 'MANUAL.md'), 'w', encoding='utf-8').write(TEXT)
    open(os.path.join(ROOT, 'MANUAL.html'), 'w', encoding='utf-8').write(to_html(TEXT))
    print('MANUAL.md, MANUAL.html, docs/ELEM47_wrap_fr.png, docs/ELEM47_detail_co.png')
