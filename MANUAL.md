# Elements 47 v1.1.0: user's manual

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

## Free42 / DM42

ELEM47 v1.1.0 is for the C47 / R47 only (Free42 has no structured programming). On a DM42 / DM42n with the
stock firmware, or in Free42, use the release v1.0.0 (`Free42_DM42/ELEM47.raw`): the same table and keys,
without going around the edges.
