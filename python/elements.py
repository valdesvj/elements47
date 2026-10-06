"""elements.py - the 118 elements: (symbol, name, standard atomic weight as shown).
Weights: IUPAC abridged values; [n] = mass number of the longest-lived isotope (no stable isotope).
Index 0 = Z 1. Used by tools/build_elem47.py to write the data labels of ELEM47."""

ELEMENTS = [
    ('H', 'Hydrogen', '1.008'), ('He', 'Helium', '4.0026'), ('Li', 'Lithium', '6.94'),
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
    ('Zr', 'Zirconium', '91.224'), ('Nb', 'Niobium', '92.906'), ('Mo', 'Molybdenum', '95.95'),
    ('Tc', 'Technetium', '[97]'), ('Ru', 'Ruthenium', '101.07'), ('Rh', 'Rhodium', '102.91'),
    ('Pd', 'Palladium', '106.42'), ('Ag', 'Silver', '107.87'), ('Cd', 'Cadmium', '112.41'),
    ('In', 'Indium', '114.82'), ('Sn', 'Tin', '118.71'), ('Sb', 'Antimony', '121.76'),
    ('Te', 'Tellurium', '127.60'), ('I', 'Iodine', '126.90'), ('Xe', 'Xenon', '131.29'),
    ('Cs', 'Caesium', '132.91'), ('Ba', 'Barium', '137.33'), ('La', 'Lanthanum', '138.91'),
    ('Ce', 'Cerium', '140.12'), ('Pr', 'Praseodymium', '140.91'), ('Nd', 'Neodymium', '144.24'),
    ('Pm', 'Promethium', '[145]'), ('Sm', 'Samarium', '150.36'), ('Eu', 'Europium', '151.96'),
    ('Gd', 'Gadolinium', '157.25'), ('Tb', 'Terbium', '158.93'), ('Dy', 'Dysprosium', '162.50'),
    ('Ho', 'Holmium', '164.93'), ('Er', 'Erbium', '167.26'), ('Tm', 'Thulium', '168.93'),
    ('Yb', 'Ytterbium', '173.05'), ('Lu', 'Lutetium', '174.97'), ('Hf', 'Hafnium', '178.49'),
    ('Ta', 'Tantalum', '180.95'), ('W', 'Tungsten', '183.84'), ('Re', 'Rhenium', '186.21'),
    ('Os', 'Osmium', '190.23'), ('Ir', 'Iridium', '192.22'), ('Pt', 'Platinum', '195.08'),
    ('Au', 'Gold', '196.97'), ('Hg', 'Mercury', '200.59'), ('Tl', 'Thallium', '204.38'),
    ('Pb', 'Lead', '207.2'), ('Bi', 'Bismuth', '208.98'), ('Po', 'Polonium', '[209]'),
    ('At', 'Astatine', '[210]'), ('Rn', 'Radon', '[222]'), ('Fr', 'Francium', '[223]'),
    ('Ra', 'Radium', '[226]'), ('Ac', 'Actinium', '[227]'), ('Th', 'Thorium', '232.04'),
    ('Pa', 'Protactinium', '231.04'), ('U', 'Uranium', '238.03'), ('Np', 'Neptunium', '[237]'),
    ('Pu', 'Plutonium', '[244]'), ('Am', 'Americium', '[243]'), ('Cm', 'Curium', '[247]'),
    ('Bk', 'Berkelium', '[247]'), ('Cf', 'Californium', '[251]'), ('Es', 'Einsteinium', '[252]'),
    ('Fm', 'Fermium', '[257]'), ('Md', 'Mendelevium', '[258]'), ('No', 'Nobelium', '[259]'),
    ('Lr', 'Lawrencium', '[266]'), ('Rf', 'Rutherfordium', '[267]'), ('Db', 'Dubnium', '[268]'),
    ('Sg', 'Seaborgium', '[269]'), ('Bh', 'Bohrium', '[270]'), ('Hs', 'Hassium', '[269]'),
    ('Mt', 'Meitnerium', '[278]'), ('Ds', 'Darmstadtium', '[281]'), ('Rg', 'Roentgenium', '[282]'),
    ('Cn', 'Copernicium', '[285]'), ('Nh', 'Nihonium', '[286]'), ('Fl', 'Flerovium', '[289]'),
    ('Mc', 'Moscovium', '[290]'), ('Lv', 'Livermorium', '[293]'), ('Ts', 'Tennessine', '[294]'),
    ('Og', 'Oganesson', '[294]'),
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


assert len(ELEMENTS) == 118 and sum(n for _, n, _, _ in SEGMENTS) == 118
