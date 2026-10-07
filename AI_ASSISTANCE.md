# AI Assistance Policy

## How this project uses AI

This project was **developed with the help of AI** — Claude (Anthropic) and Gemini (Google) — as a cooperation. AI assisted with brainstorming, code generation, and documentation, but I reviewed all output, validated results against reference data and the C47 simulator, and take full responsibility for the work and any mistakes.

## Responsible use

- ✅ **I checked the results** — Every screen is run in the C47 simulator and checked pixel for pixel (`tests/test_elem47.py`): the 118 cells, the cursor moves, the detail box
- ✅ **I checked the data** — Atomic weights from the IUPAC periodic table (CIAAW abridged standard atomic weights 2024); state, boiling point and electron configuration from the PubChem periodic table; every element's data is tested against `python/elements.py`
- ✅ **I maintained domain expertise** — I guide the AI with the design decisions: the layout, the keys, the data shown
- ✅ **I take full responsibility** — The work is mine; any errors are mine to fix
- ✅ **I'm transparent** — This file documents how AI was used

## Testing & Validation

- Simulator tests: the C47 programs run in `python/c47sim.py` (from Almanac 47), every screen and every element checked
- Data cross-checked against IUPAC / CIAAW and PubChem
- To be tested on real C47 hardware before each release

## License

This does not affect the GNU GPL-3.0 license. All code remains open-source and fully accessible.

---

*For more details, see `NOTICE` and the development documentation.*
