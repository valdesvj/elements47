# Elements 47 🧪

An interactive, memory-optimized Periodic Table of Elements built for the **C47** and **Free42** RPN calculator firmware (fully compatible with SwissMicros DM42 hardware and mobile/desktop emulators).

---

## Elements 47 v1.0.0

`ELEM47` draws all 118 elements in an 18 × 9 grid. **8 4 6 2** move the cursor (gaps skipped),
**5** opens the detail box (symbol, mass, state, boiling point, group number and name, electron
configuration); with the box open **8 4 6 2** move to the next element and show its box, **5** closes
it, **0** ends.
The empty space of periods 1–3 holds the title, the selected element's name, Z and mass, and the keys
(the digit cross 8 4 6 2 with 5 and 0, beside the same places in arrows and words).
Masses: the abridged standard atomic weights of the IUPAC periodic table (CIAAW 2024); "-" for the 34
elements without a standard atomic weight. State, boiling point and configuration: the PubChem periodic table
("-" where PubChem has none, or only an expected state).

| | C47 / R47 | Free42 (DM42 / DM42n stock firmware) |
|---|---|---|
| File (release zip) | `C47_R47/ELEM47.p47` (from `build/ELEM47.txt`, rejig) | `Free42_DM42/ELEM47.raw` (from `build/free42/ELEM47.txt`) |
| Programs | `ELEM47` (the code, 810 steps, numeric local labels 00–50), `A` and `B` (the element records, Z 1–60 and 61–118, 49 steps each, 4 elements per text) | `ELEM47` (1 016 steps), `A`, `B` as on the C47, `E47T` (with `E47B`) and `E47S`: the C47 fonts, one local label per character |
| Needs | ATEXT and GRFNT: firmware 00.109.05.00a0.ALPHA (5 Oct 2026) or later, as Almanac 47 v2.2.0 | Free42 3.3 (strings: XSTR, SUBSTR, POS, HEAD) |
| Memory | R20–R55 and the matrix `PT` (9 × 18) | R20–R75 (SIZE 76 if smaller) and `PT` |
| Screen | shown when ELEM47 waits for a key (the C47 draws off screen) | the same with `RefLCD` (DM42 / DM42n): 0 while drawing, -1 before each key wait, 7 at the end |
| At the end (0) | `PT` deleted, **the registers and the stack cleared** (CLREGS, CLSTK) | `PT` deleted, CLRG, CLST |

Same screens on both, pixel for pixel. Tested in the C47 firmware itself (T47, built from the firmware
sources, `tests/test_fw.py`), in the Python C47 simulator (`tests/test_elem47.py`, `tests/test_opt.py`) and in
Free42 (`tests/test_f42.py`): the whole table both ways with the detail box opened and closed at every cell.
Screens: `docs/ELEM47_*.png`. Start with `QUICKSTART.txt`; the layout of the repository is in `PROGRAM_MAP.txt`.

Work (C47 simulator steps): the table 7 900, a cursor move about 245, the detail box 1 040, closing it 4 070
(only the cells under the box are drawn again). The routines of a move are at the start of `ELEM47`: the firmware
finds the step after an XEQ again by counting the steps from the start of the program, at every RTN.

---

## Author

By Victor Valdes (valdes.vj@gmail.com),

Thank you to the C43/C47 firmware developers and SwissMicros, and to @tangent for rejig, which makes converting the .txt programs to .p47 easy. Written with the help of AI. See `AI_ASSISTANCE.md` for the responsible-use statement.

## License

Published under the [GNU General Public License v3.0](LICENSE). Free to use, modify, and share for the calculator community. See `NOTICE` for the sources of the element data.
