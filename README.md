# Elements 47 🧪

An interactive, memory-optimized Periodic Table of Elements built for the **C47 / R47** RPN calculator firmware (release v1.0.0 also runs in **Free42**: SwissMicros DM42 / DM42n stock firmware and the emulators).

---

## Elements 47 v1.1.0 (C47 / R47)

`ELEM47` draws all 118 elements in an 18 × 9 grid. **8 4 6 2** move the cursor (gaps skipped; at an edge it goes
around to the other side), **5** opens the detail box (symbol, mass, state, boiling point, group number and name,
electron configuration); with the box open **8 4 6 2** move to the next element and show its box, **5** closes
it, **0** ends.
The empty space of periods 1–3 holds the title, the selected element's name, Z and mass, and the keys
(the digit cross 8 4 6 2 with 5 and 0, beside the same places in arrows and words).
Masses: the abridged standard atomic weights of the IUPAC periodic table (CIAAW 2024); "-" for the 34
elements without a standard atomic weight. State, boiling point and configuration: the PubChem periodic table
("-" where PubChem has none, or only an expected state).

How to use it, with the screens: **[MANUAL.md](MANUAL.md)** (`MANUAL.html` in the release zip). In short: `QUICKSTART.txt`.

| | C47 / R47 |
|---|---|
| File (release zip) | `C47_R47/ELEM47.p47` (rejig, from `build/pixel/ELEM47.txt`), the listing `C47_R47/ELEM47.txt` |
| Programs | `ELEM47` (the code, 867 steps), `ELD1` and `ELD2` (the element records, one per label: Z 1–60 and 61–118) |
| Needs | firmware 00.109.05.00a0.ALPHA (5 Oct 2026) or later, as Almanac 47 v2.2.0: ATEXT, GRFNT, PIXEL and the STRUCT commands (IF / DO / REPEAT, app note AN0007) |
| Memory | R20–R56 and the matrix `PT` (9 × 18) |
| At the end (0) | `PT` deleted, **the registers and the stack cleared** (CLREGS, CLSTK), GRFNT 20 and GRMOD 0 restored |

What is new since v1.0.0:
- The arrows go around the edges (H up → Fr, H left → He, Ac down → Sc, ...).
- C47 / R47 only: the control flow in the C47 STRUCT commands (no GTO), one element record per data label,
  the table's horizontal lines by PIXEL (one full screen row in one step). C47 simulator steps, v1.0.0 → v1.1.0:
  the table 7 900 → 5 254 (-33 %), the detail box 1 040 → 991, closing it 4 070 → 2 737 (-33 %), a move 245 → 235.
- The user's manual with the screens.

**Free42 / DM42 (stock firmware):** Free42 has no STRUCT commands, so v1.1.0 is not converted for it. Use
release [v1.0.0](https://github.com/valdesvj/elements47/releases/tag/v1.0.0) (`Free42_DM42/ELEM47.raw`): the
same table and keys, without going around the edges.

Tested in the C47 firmware itself (T47, built from the firmware sources, `tests/test_fw.py`: 955 screens pixel
for pixel), in the Python C47 simulator (`tests/test_elem47.py`, `tests/test_opt.py`: every screen of the table
and the detail box) and on a C47 by the author. Screens: `docs/ELEM47_*.png`; the layout of the repository is in
`PROGRAM_MAP.txt`.

The `.p47u` for the PROGRAMS folder of the C47 firmware release: `build/p47u/ELEM47.p47u` (the same programs with
the comments).

---

## Author

By Victor Valdes (valdes.vj@gmail.com),

Thank you to the C43/C47 firmware developers and SwissMicros, and to @tangent for rejig, which makes converting the .txt programs to .p47 easy. Written with the help of AI. See `AI_ASSISTANCE.md` for the responsible-use statement.

## License

Published under the [GNU General Public License v3.0](LICENSE). Free to use, modify, and share for the calculator community. See `NOTICE` for the sources of the element data.
