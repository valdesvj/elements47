# Elements 47 🧪

An interactive, memory-optimized Periodic Table of Elements built for the **C47** and **Free42** RPN calculator firmware (fully compatible with SwissMicros DM42 hardware and mobile/desktop emulators).

---

## Status: prototype 1

`build/ELEM47.txt` shows the Hydrogen cell; **`+`** opens its detail box in the middle of the screen.
Screens from the C47 simulator: `docs/ELEM47_table.png`, `docs/ELEM47_detail.png`. Start with `QUICKSTART.txt`;
the layout of the repository is in `PROGRAM_MAP.txt`. Test: `python3 tests/test_elem47.py`.

The features below are the plan for the full table.

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

## License

Published under the [GNU General Public License v3.0](LICENSE). Free to use, modify, and share for the calculator community.
