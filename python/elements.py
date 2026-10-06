"""elements.py - the 118 elements: (symbol, name, standard atomic weight as shown), and EXTRA (state,
boiling point, electron configuration).
Weights: the abridged standard atomic weights of the IUPAC periodic table (CIAAW, Abridged Standard
Atomic Weights 2024: www.ciaaw.org/abridged-atomic-weights.htm); "-" = no standard atomic weight.
Index 0 = Z 1. Used by tools/build_elem47.py to write the data labels of ELEM47."""

ELEMENTS = [
    ('H', 'Hydrogen', '1.0080'), ('He', 'Helium', '4.0026'), ('Li', 'Lithium', '6.94'),
    ('Be', 'Beryllium', '9.0122'), ('B', 'Boron', '10.81'), ('C', 'Carbon', '12.011'),
    ('N', 'Nitrogen', '14.007'), ('O', 'Oxygen', '15.999'), ('F', 'Fluorine', '18.998'),
    ('Ne', 'Neon', '20.180'), ('Na', 'Sodium', '22.990'), ('Mg', 'Magnesium', '24.305'),
    ('Al', 'Aluminium', '26.982'), ('Si', 'Silicon', '28.085'), ('P', 'Phosphorus', '30.974'),
    ('S', 'Sulfur', '32.06'), ('Cl', 'Chlorine', '35.45'), ('Ar', 'Argon', '39.95'),
    ('K', 'Potassium', '39.098'), ('Ca', 'Calcium', '40.078'), ('Sc', 'Scandium', '44.956'),
    ('Ti', 'Titanium', '47.867'), ('V', 'Vanadium', '50.942'), ('Cr', 'Chromium', '51.996'),
    ('Mn', 'Manganese', '54.938'), ('Fe', 'Iron', '55.845'), ('Co', 'Cobalt', '58.933'),
    ('Ni', 'Nickel', '58.693'), ('Cu', 'Copper', '63.546'), ('Zn', 'Zinc', '65.38'),
    ('Ga', 'Gallium', '69.723'), ('Ge', 'Germanium', '72.630'), ('As', 'Arsenic', '74.922'),
    ('Se', 'Selenium', '78.971'), ('Br', 'Bromine', '79.904'), ('Kr', 'Krypton', '83.798'),
    ('Rb', 'Rubidium', '85.468'), ('Sr', 'Strontium', '87.62'), ('Y', 'Yttrium', '88.906'),
    ('Zr', 'Zirconium', '91.222'), ('Nb', 'Niobium', '92.906'), ('Mo', 'Molybdenum', '95.95'),
    ('Tc', 'Technetium', '-'), ('Ru', 'Ruthenium', '101.07'), ('Rh', 'Rhodium', '102.91'),
    ('Pd', 'Palladium', '106.42'), ('Ag', 'Silver', '107.87'), ('Cd', 'Cadmium', '112.41'),
    ('In', 'Indium', '114.82'), ('Sn', 'Tin', '118.71'), ('Sb', 'Antimony', '121.76'),
    ('Te', 'Tellurium', '127.60'), ('I', 'Iodine', '126.90'), ('Xe', 'Xenon', '131.29'),
    ('Cs', 'Caesium', '132.91'), ('Ba', 'Barium', '137.33'), ('La', 'Lanthanum', '138.91'),
    ('Ce', 'Cerium', '140.12'), ('Pr', 'Praseodymium', '140.91'), ('Nd', 'Neodymium', '144.24'),
    ('Pm', 'Promethium', '-'), ('Sm', 'Samarium', '150.36'), ('Eu', 'Europium', '151.96'),
    ('Gd', 'Gadolinium', '157.25'), ('Tb', 'Terbium', '158.93'), ('Dy', 'Dysprosium', '162.50'),
    ('Ho', 'Holmium', '164.93'), ('Er', 'Erbium', '167.26'), ('Tm', 'Thulium', '168.93'),
    ('Yb', 'Ytterbium', '173.05'), ('Lu', 'Lutetium', '174.97'), ('Hf', 'Hafnium', '178.49'),
    ('Ta', 'Tantalum', '180.95'), ('W', 'Tungsten', '183.84'), ('Re', 'Rhenium', '186.21'),
    ('Os', 'Osmium', '190.23'), ('Ir', 'Iridium', '192.22'), ('Pt', 'Platinum', '195.08'),
    ('Au', 'Gold', '196.97'), ('Hg', 'Mercury', '200.59'), ('Tl', 'Thallium', '204.38'),
    ('Pb', 'Lead', '207.2'), ('Bi', 'Bismuth', '208.98'), ('Po', 'Polonium', '-'),
    ('At', 'Astatine', '-'), ('Rn', 'Radon', '-'), ('Fr', 'Francium', '-'),
    ('Ra', 'Radium', '-'), ('Ac', 'Actinium', '-'), ('Th', 'Thorium', '232.04'),
    ('Pa', 'Protactinium', '231.04'), ('U', 'Uranium', '238.03'), ('Np', 'Neptunium', '-'),
    ('Pu', 'Plutonium', '-'), ('Am', 'Americium', '-'), ('Cm', 'Curium', '-'),
    ('Bk', 'Berkelium', '-'), ('Cf', 'Californium', '-'), ('Es', 'Einsteinium', '-'),
    ('Fm', 'Fermium', '-'), ('Md', 'Mendelevium', '-'), ('No', 'Nobelium', '-'),
    ('Lr', 'Lawrencium', '-'), ('Rf', 'Rutherfordium', '-'), ('Db', 'Dubnium', '-'),
    ('Sg', 'Seaborgium', '-'), ('Bh', 'Bohrium', '-'), ('Hs', 'Hassium', '-'),
    ('Mt', 'Meitnerium', '-'), ('Ds', 'Darmstadtium', '-'), ('Rg', 'Roentgenium', '-'),
    ('Cn', 'Copernicium', '-'), ('Nh', 'Nihonium', '-'), ('Fl', 'Flerovium', '-'),
    ('Mc', 'Moscovium', '-'), ('Lv', 'Livermorium', '-'), ('Ts', 'Tennessine', '-'),
    ('Og', 'Oganesson', '-'),
]

# state, boiling point, electron configuration (noble-gas core, subshells in shell order); index 0 = Z 1.
# From the PubChem periodic table (pubchem.ncbi.nlm.nih.gov/periodic-table, CSV of Oct 2026, from Victor):
# StandardState ("Expected to be ..." shown as "-"), BoilingPoint in K (one decimal below 100 K, "-" when
# none), ElectronConfiguration ("(predicted)" dropped). Boiling points of C and As are sublimation points.
EXTRA = [
    ('Gas', '20.3 K', '1s1'), ('Gas', '4.2 K', '1s2'),
    ('Solid', '1615 K', '[He] 2s1'), ('Solid', '2744 K', '[He] 2s2'),
    ('Solid', '4273 K', '[He] 2s2 2p1'), ('Solid', '4098 K', '[He] 2s2 2p2'),
    ('Gas', '77.4 K', '[He] 2s2 2p3'), ('Gas', '90.2 K', '[He] 2s2 2p4'),
    ('Gas', '85.0 K', '[He] 2s2 2p5'), ('Gas', '27.1 K', '[He] 2s2 2p6'),
    ('Solid', '1156 K', '[Ne] 3s1'), ('Solid', '1363 K', '[Ne] 3s2'),
    ('Solid', '2792 K', '[Ne] 3s2 3p1'), ('Solid', '3538 K', '[Ne] 3s2 3p2'),
    ('Solid', '554 K', '[Ne] 3s2 3p3'), ('Solid', '718 K', '[Ne] 3s2 3p4'),
    ('Gas', '239 K', '[Ne] 3s2 3p5'), ('Gas', '87.3 K', '[Ne] 3s2 3p6'),
    ('Solid', '1032 K', '[Ar] 4s1'), ('Solid', '1757 K', '[Ar] 4s2'),
    ('Solid', '3109 K', '[Ar] 3d1 4s2'), ('Solid', '3560 K', '[Ar] 3d2 4s2'),
    ('Solid', '3680 K', '[Ar] 3d3 4s2'), ('Solid', '2944 K', '[Ar] 3d5 4s1'),
    ('Solid', '2334 K', '[Ar] 3d5 4s2'), ('Solid', '3134 K', '[Ar] 3d6 4s2'),
    ('Solid', '3200 K', '[Ar] 3d7 4s2'), ('Solid', '3186 K', '[Ar] 3d8 4s2'),
    ('Solid', '2835 K', '[Ar] 3d10 4s1'), ('Solid', '1180 K', '[Ar] 3d10 4s2'),
    ('Solid', '2477 K', '[Ar] 3d10 4s2 4p1'), ('Solid', '3106 K', '[Ar] 3d10 4s2 4p2'),
    ('Solid', '887 K', '[Ar] 3d10 4s2 4p3'), ('Solid', '958 K', '[Ar] 3d10 4s2 4p4'),
    ('Liquid', '332 K', '[Ar] 3d10 4s2 4p5'), ('Gas', '120 K', '[Ar] 3d10 4s2 4p6'),
    ('Solid', '961 K', '[Kr] 5s1'), ('Solid', '1655 K', '[Kr] 5s2'),
    ('Solid', '3618 K', '[Kr] 4d1 5s2'), ('Solid', '4682 K', '[Kr] 4d2 5s2'),
    ('Solid', '5017 K', '[Kr] 4d4 5s1'), ('Solid', '4912 K', '[Kr] 4d5 5s1'),
    ('Solid', '4538 K', '[Kr] 4d5 5s2'), ('Solid', '4423 K', '[Kr] 4d7 5s1'),
    ('Solid', '3968 K', '[Kr] 4d8 5s1'), ('Solid', '3236 K', '[Kr] 4d10'),
    ('Solid', '2435 K', '[Kr] 4d10 5s1'), ('Solid', '1040 K', '[Kr] 4d10 5s2'),
    ('Solid', '2345 K', '[Kr] 4d10 5s2 5p1'), ('Solid', '2875 K', '[Kr] 4d10 5s2 5p2'),
    ('Solid', '1860 K', '[Kr] 4d10 5s2 5p3'), ('Solid', '1261 K', '[Kr] 4d10 5s2 5p4'),
    ('Solid', '458 K', '[Kr] 4d10 5s2 5p5'), ('Gas', '165 K', '[Kr] 4d10 5s2 5p6'),
    ('Solid', '944 K', '[Xe] 6s1'), ('Solid', '2170 K', '[Xe] 6s2'),
    ('Solid', '3737 K', '[Xe] 5d1 6s2'), ('Solid', '3697 K', '[Xe] 4f1 5d1 6s2'),
    ('Solid', '3793 K', '[Xe] 4f3 6s2'), ('Solid', '3347 K', '[Xe] 4f4 6s2'),
    ('Solid', '3273 K', '[Xe] 4f5 6s2'), ('Solid', '2067 K', '[Xe] 4f6 6s2'),
    ('Solid', '1802 K', '[Xe] 4f7 6s2'), ('Solid', '3546 K', '[Xe] 4f7 5d1 6s2'),
    ('Solid', '3503 K', '[Xe] 4f9 6s2'), ('Solid', '2840 K', '[Xe] 4f10 6s2'),
    ('Solid', '2973 K', '[Xe] 4f11 6s2'), ('Solid', '3141 K', '[Xe] 4f12 6s2'),
    ('Solid', '2223 K', '[Xe] 4f13 6s2'), ('Solid', '1469 K', '[Xe] 4f14 6s2'),
    ('Solid', '3675 K', '[Xe] 4f14 5d1 6s2'), ('Solid', '4876 K', '[Xe] 4f14 5d2 6s2'),
    ('Solid', '5731 K', '[Xe] 4f14 5d3 6s2'), ('Solid', '5828 K', '[Xe] 4f14 5d4 6s2'),
    ('Solid', '5869 K', '[Xe] 4f14 5d5 6s2'), ('Solid', '5285 K', '[Xe] 4f14 5d6 6s2'),
    ('Solid', '4701 K', '[Xe] 4f14 5d7 6s2'), ('Solid', '4098 K', '[Xe] 4f14 5d9 6s1'),
    ('Solid', '3129 K', '[Xe] 4f14 5d10 6s1'), ('Liquid', '630 K', '[Xe] 4f14 5d10 6s2'),
    ('Solid', '1746 K', '[Xe] 4f14 5d10 6s2 6p1'), ('Solid', '2022 K', '[Xe] 4f14 5d10 6s2 6p2'),
    ('Solid', '1837 K', '[Xe] 4f14 5d10 6s2 6p3'), ('Solid', '1235 K', '[Xe] 4f14 5d10 6s2 6p4'),
    ('Solid', '-', '[Xe] 4f14 5d10 6s2 6p5'), ('Gas', '211 K', '[Xe] 4f14 5d10 6s2 6p6'),
    ('Solid', '-', '[Rn] 7s1'), ('Solid', '1413 K', '[Rn] 7s2'),
    ('Solid', '3471 K', '[Rn] 6d1 7s2'), ('Solid', '5061 K', '[Rn] 6d2 7s2'),
    ('Solid', '-', '[Rn] 5f2 6d1 7s2'), ('Solid', '4404 K', '[Rn] 5f3 6d1 7s2'),
    ('Solid', '4175 K', '[Rn] 5f4 6d1 7s2'), ('Solid', '3501 K', '[Rn] 5f6 7s2'),
    ('Solid', '2284 K', '[Rn] 5f7 7s2'), ('Solid', '3400 K', '[Rn] 5f7 6d1 7s2'),
    ('Solid', '-', '[Rn] 5f9 7s2'), ('Solid', '-', '[Rn] 5f10 7s2'),
    ('Solid', '-', '[Rn] 5f11 7s2'), ('Solid', '-', '[Rn] 5f12 7s2'),
    ('Solid', '-', '[Rn] 5f13 7s2'), ('Solid', '-', '[Rn] 5f14 7s2'),
    ('Solid', '-', '[Rn] 5f14 6d1 7s2'), ('Solid', '-', '[Rn] 5f14 6d2 7s2'),
    ('Solid', '-', '[Rn] 5f14 6d3 7s2'), ('Solid', '-', '[Rn] 5f14 6d4 7s2'),
    ('Solid', '-', '[Rn] 5f14 6d5 7s2'), ('Solid', '-', '[Rn] 5f14 6d6 7s2'),
    ('Solid', '-', '[Rn] 5f14 6d7 7s2'), ('-', '-', '[Rn] 5f14 6d8 7s2'),
    ('-', '-', '[Rn] 5f14 6d9 7s2'), ('-', '-', '[Rn] 5f14 6d10 7s2'),
    ('-', '-', '[Rn] 5f14 6d10 7s2 7p1'), ('-', '-', '[Rn] 5f14 6d10 7s2 7p2'),
    ('-', '-', '[Rn] 5f14 6d10 7s2 7p3'), ('-', '-', '[Rn] 5f14 6d10 7s2 7p4'),
    ('-', '-', '[Rn] 5f14 6d10 7s2 7p5'), ('-', '-', '[Rn] 5f14 6d10 7s2 7p6'),
]

# the table: (first Z, count, row, column); rows 1-7 = periods, 8 = lanthanides, 9 = actinides
SEGMENTS = [(1, 1, 1, 1), (2, 1, 1, 18), (3, 2, 2, 1), (5, 6, 2, 13), (11, 2, 3, 1), (13, 6, 3, 13),
            (19, 18, 4, 1), (37, 18, 5, 1), (55, 2, 6, 1), (57, 15, 8, 3), (72, 15, 6, 4),
            (87, 2, 7, 1), (89, 15, 9, 3), (104, 15, 7, 4)]


def position(z):
    """(row, column) of element z."""
    for z0, n, r, c in SEGMENTS:
        if z0 <= z < z0 + n:
            return r, c + z - z0
    raise ValueError(z)


assert len(ELEMENTS) == len(EXTRA) == 118 and sum(n for _, n, _, _ in SEGMENTS) == 118
