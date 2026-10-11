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
| Programs | `ELEM47` (the code, 868 steps), `ELD1` and `ELD2` (the element records, one per label: Z 1–60 and 61–118) |
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

### Which calculators (STRUCT, ATEXT and GRFNT in the firmware)

ELEM47 v1.1.0 needs three things from the C47 firmware: the STRUCT commands (IF / DO / REPEAT, app note AN0007),
ATEXT and GRFNT. Whether a calculator has them depends on the hardware and the firmware version:

| Calculator | Firmware | STRUCT | ATEXT, GRFNT | ELEM47 v1.1.0 |
|---|---|---|---|---|
| R47, DM42n (DM32 board, `C47.pg5` / `R47.pg5`) | 00.109.05.00a0.ALPHA (5 Oct 2026) or later | in | in | **runs** (tested in the firmware and on a C47) |
| original DM42 (not n), `C47.pgm` **packages 1, 2, 3** | 00.109.05.00a0.ALPHA or later | in, at most 10 IF, 10 DO and 10 REPEAT per program, 10 levels | in | **should run** (ELEM47: 10 IF, 5 DO, 1 REPEAT); not tried on a real DM42 |
| original DM42, `C47.pgm` **package 4** | any | out | in | no |
| original DM42 | master of 8 Oct 2026 (a snapshot, not a release) | out | out | no |
| any | 00.109.04.00b0 and earlier | out | out | no |
| DM42 / DM42n, stock firmware (Free42) | Free42 3.3 | — | — | use v1.0.0 |

- **The original DM42: packages 1-3 only, not tried yet.** Its flash is small, so its firmware packages leave features
  out (c43 `src/c47/defines.h`, `TWO_FILE_PGM`, `res/PACKAGES.md`). Where STRUCT is in, the DM42 has room for only 10
  numbers of each kind per program and 10 levels of nesting (`src/c47/programming/structured.h`, `OLD_HW`; the R47
  and the DM42n: 255 and 63). ELEM47 keeps within that: 10 IF (the build stops past the DM42 limits). Which features
  the DM42 packages carry changes from one firmware build to the next to save space (the master of 8 Oct 2026 had
  STRUCT, ATEXT and GRFNT out, the master of 10 Oct has them back): a later release may leave them out again.
- **Slow on the original DM42.** It is older, slower hardware than the DM42n and the R47, where the table already
  takes a few seconds: expect the table, the moves and the detail box to take longer (not measured).
- **Not tried on a real original DM42.** There is no simulator for it; the above is from the firmware sources and
  the files. A report from someone with an original DM42 is welcome.

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
