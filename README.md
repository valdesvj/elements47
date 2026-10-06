# Elements 47 🧪

An interactive, memory-optimized Periodic Table of Elements built for the **C47** and **Free42** RPN calculator firmware (fully compatible with SwissMicros DM42 hardware and mobile/desktop emulators).

---

## Status: the full table (simulator-tested, not yet run on the C47)

`build/ELEM47.txt` draws all 118 elements in an 18 × 9 grid. **8 4 6 2** move the cursor (gaps skipped),
**5** opens the detail box (symbol, mass, state, boiling point, group number and name, electron
configuration), any key closes it, **0** ends.
The empty space of periods 1–3 holds the title, the selected element's name, Z and mass, and the keys
(the digit cross 8 4 6 2 with 5 and 0, beside the same places in arrows and words).
Masses: the abridged standard atomic weights of the IUPAC periodic table (CIAAW 2024); "-" for the 34
elements without a standard atomic weight. State, boiling point and configuration: the PubChem periodic table
("-" where PubChem has none, or only an expected state).
Screens from the C47 simulator: `docs/ELEM47_*.png`. Start with `QUICKSTART.txt`; the layout of the
repository is in `PROGRAM_MAP.txt`. Test: `python3 tests/test_elem47.py`.

| | |
|---|---|
| Programs | one file, three programs: ELEM47 830 steps (47 local labels), the data ELD1 186 and ELD2 182 steps (one label per element, 4 092 characters); about 8 KB (.p47, estimated) |
| Memory while running | R20–R51 (your values saved and given back at the end) and the matrix `PT` (9 × 18, deleted at the end) |
| Screen | cells 23 × 26 px with shared edges, the table uses x 1–397, rows 1–235 of 400 × 240 |
| Work (simulator steps) | table 9 300, a cursor move about 230, the detail box 2 100, closing it = the table again (`docs/OPTIMIZATIONS.md`) |

The features below are the plan; the differences so far: 5 instead of + for the details, the 8 4 6 2 keys
instead of the arrows, ATEXT (not "ATXT") for the text and AGRAPH (not PIXEL) for the lines.

---

## Features

* **Full 118-Element Support:** Comprehensive coverage from Hydrogen (H) to Oganesson (Og).
* **Memory-Optimized Architecture:** Utilizes a custom 236-byte packed string layout ($118 \times 2$ character padding) to ensure lightning-fast lookups without bloating RAM on hardware-constrained builds (ideal for `D42lite` environments).
* **Interactive Grid Navigation:** Seamless arrow-key traversal with built-in boundary and gap-skipping logic for transition metals and lanthanide/actinide rows.
* **XOR Cursor Highlighting:** High-performance real-time screen inversion (`XOR` mode) for tracking your active cell without redrawing the entire table grid.
* **Detail Inspector Modal:** Pressing the **`+`** key instantly pops up a detailed information window displaying extended characteristics for the selected element.
* **Native Primitives:** Built exclusively using standard C47 graphics commands (`PIXEL` line rendering and `ATXT`).

---

## Screen Layout

* **Main Grid:** $18 \text{ columns} \times 9 \text{ rows}$ mapped to the 400×240 monochrome display.
* **Cell Format:** Compact 22×26 pixel grid featuring atomic numbers and 1- or 2-letter chemical symbols.

---

## Installation & Usage

1. Load the `.p47` program source or text file into your C47 / Free42 environment (using tools like `rejig` if converting from text source).
2. Execute the main entry routine to render the periodic table grid.
3. Use the **Arrow Keys** to navigate across elements and press **`+`** for detailed element specs.

---

## Author

By Victor Valdes (valdes.vj@gmail.com),

Thank you to the C43/C47 firmware developers and SwissMicros, and to @tangent for rejig, which makes converting the .txt programs to .p47 easy. Written with the help of AI. See `AI_ASSISTANCE.md` for the responsible-use statement.

## License

Published under the [GNU General Public License v3.0](LICENSE). Free to use, modify, and share for the calculator community. See `NOTICE` for the sources of the element data.
