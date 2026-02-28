# Advanced Materials, Components, and Salvage Database
# Import this in bot.py: from advanced_materials_database import ADVANCED_MATERIALS, COMPONENT_DATABASE, SALVAGE_DATABASE, REACTION_MATERIALS

# Advanced Materials - Raw resources from moon mining, reactions, etc.
ADVANCED_MATERIALS = {
    # Raw Moon Materials (R4)
    'Bitumens': {'type_id': 45492, 'base_price': 500},
    'Brimful Bitumens': {'type_id': 45493, 'base_price': 600},
    'Glistening Bitumens': {'type_id': 45494, 'base_price': 750},
    'Coesite': {'type_id': 45495, 'base_price': 500},
    'Brimful Coesite': {'type_id': 45496, 'base_price': 600},
    'Glistening Coesite': {'type_id': 45497, 'base_price': 750},
    'Sylvite': {'type_id': 45498, 'base_price': 500},
    'Brimful Sylvite': {'type_id': 45499, 'base_price': 600},
    'Glistening Sylvite': {'type_id': 45500, 'base_price': 750},
    'Zeolites': {'type_id': 45501, 'base_price': 500},
    'Brimful Zeolites': {'type_id': 45502, 'base_price': 600},
    'Glistening Zeolites': {'type_id': 45503, 'base_price': 750},
    
    # Raw Moon Materials (R8)
    'Cobaltite': {'type_id': 45504, 'base_price': 1000},
    'Copious Cobaltite': {'type_id': 45505, 'base_price': 1200},
    'Twinkling Cobaltite': {'type_id': 45506, 'base_price': 1500},
    'Euxenite': {'type_id': 45507, 'base_price': 1000},
    'Copious Euxenite': {'type_id': 45508, 'base_price': 1200},
    'Twinkling Euxenite': {'type_id': 45509, 'base_price': 1500},
    'Titanite': {'type_id': 45510, 'base_price': 1000},
    'Copious Titanite': {'type_id': 45511, 'base_price': 1200},
    'Twinkling Titanite': {'type_id': 45512, 'base_price': 1500},
    'Scheelite': {'type_id': 45513, 'base_price': 1000},
    'Copious Scheelite': {'type_id': 45514, 'base_price': 1200},
    'Twinkling Scheelite': {'type_id': 45515, 'base_price': 1500},
    
    # Raw Moon Materials (R16)
    'Lepidolite': {'type_id': 45516, 'base_price': 2000},
    'Bountiful Lepidolite': {'type_id': 45517, 'base_price': 2400},
    'Shining Lepidolite': {'type_id': 45518, 'base_price': 3000},
    'Petzlite': {'type_id': 45519, 'base_price': 2000},
    'Bountiful Petzlite': {'type_id': 45520, 'base_price': 2400},
    'Shining Petzlite': {'type_id': 45521, 'base_price': 3000},
    'Pollucite': {'type_id': 45522, 'base_price': 2000},
    'Bountiful Pollucite': {'type_id': 45523, 'base_price': 2400},
    'Shining Pollucite': {'type_id': 45524, 'base_price': 3000},
    
    # Raw Moon Materials (R32)
    'Carnotite': {'type_id': 45525, 'base_price': 4000},
    'Replete Carnotite': {'type_id': 45526, 'base_price': 4800},
    'Glowing Carnotite': {'type_id': 45527, 'base_price': 6000},
    'Cinnabar': {'type_id': 45528, 'base_price': 4000},
    'Replete Cinnabar': {'type_id': 45529, 'base_price': 4800},
    'Glowing Cinnabar': {'type_id': 45530, 'base_price': 6000},
    'Zircon': {'type_id': 45531, 'base_price': 4000},
    'Replete Zircon': {'type_id': 45532, 'base_price': 4800},
    'Glowing Zircon': {'type_id': 45533, 'base_price': 6000},
    
    # Raw Moon Materials (R64)
    'Monazite': {'type_id': 45534, 'base_price': 8000},
    'Rich Monazite': {'type_id': 45535, 'base_price': 9600},
    'Sparkling Monazite': {'type_id': 45536, 'base_price': 12000},
    'Loparite': {'type_id': 45537, 'base_price': 8000},
    'Rich Loparite': {'type_id': 45538, 'base_price': 9600},
    'Sparkling Loparite': {'type_id': 45539, 'base_price': 12000},
    'Xenotime': {'type_id': 45540, 'base_price': 8000},
    'Rich Xenotime': {'type_id': 45541, 'base_price': 9600},
    'Sparkling Xenotime': {'type_id': 45542, 'base_price': 12000},
    'Ytterbite': {'type_id': 45543, 'base_price': 8000},
    'Rich Ytterbite': {'type_id': 45544, 'base_price': 9600},
    'Sparkling Ytterbite': {'type_id': 45545, 'base_price': 12000},
    
    # Processed Moon Goo (Simple Reactions)
    'Hydrocarbons': {'type_id': 16633, 'base_price': 350},
    'Silicates': {'type_id': 16636, 'base_price': 350},
    'Evaporite Deposits': {'type_id': 16635, 'base_price': 350},
    'Atmospheric Gases': {'type_id': 16634, 'base_price': 350},
    'Cobalt': {'type_id': 16640, 'base_price': 700},
    'Scandium': {'type_id': 16639, 'base_price': 700},
    'Titanium': {'type_id': 16638, 'base_price': 700},
    'Tungsten': {'type_id': 16637, 'base_price': 700},
    'Chromium': {'type_id': 16641, 'base_price': 1400},
    'Cadmium': {'type_id': 16643, 'base_price': 1400},
    'Vanadium': {'type_id': 16642, 'base_price': 1400},
    'Platinum': {'type_id': 16644, 'base_price': 1400},
    'Caesium': {'type_id': 16647, 'base_price': 2800},
    'Mercury': {'type_id': 16646, 'base_price': 2800},
    'Hafnium': {'type_id': 16649, 'base_price': 2800},
    'Technetium': {'type_id': 16648, 'base_price': 2800},
    'Promethium': {'type_id': 16652, 'base_price': 5600},
    'Dysprosium': {'type_id': 16651, 'base_price': 5600},
    'Neodymium': {'type_id': 16650, 'base_price': 5600},
    'Thulium': {'type_id': 16653, 'base_price': 5600},
}

# Reaction Materials (Complex Reactions)
REACTION_MATERIALS = {
    'Crystalline Carbonide': {'type_id': 16670, 'base_price': 12000},
    'Titanium Carbide': {'type_id': 16671, 'base_price': 12000},
    'Tungsten Carbide': {'type_id': 16672, 'base_price': 12000},
    'Fernite Carbide': {'type_id': 16673, 'base_price': 12000},
    'Sylramic Fibers': {'type_id': 16679, 'base_price': 12000},
    'Fullerides': {'type_id': 16678, 'base_price': 15000},
    'Phenolic Composites': {'type_id': 16677, 'base_price': 15000},
    'Nanotransistors': {'type_id': 16680, 'base_price': 20000},
    'Hypersynaptic Fibers': {'type_id': 16681, 'base_price': 20000},
    'Ferrogel': {'type_id': 16682, 'base_price': 50000},
    'Fermionic Condensates': {'type_id': 16683, 'base_price': 75000},
    'Nonlinear Metamaterials': {'type_id': 57478, 'base_price': 80000},
    'Photonic Metamaterials': {'type_id': 57479, 'base_price': 80000},
    'Plasmonic Metamaterials': {'type_id': 57480, 'base_price': 80000},
    'Terahertz Metamaterials': {'type_id': 57481, 'base_price': 80000},
}

# Capital Components as Buildable Blueprints
CAPITAL_COMPONENT_BLUEPRINTS = [
    # Armor Components
    {'id': 1000, 'name': 'Capital Armor Plates Blueprint', 'category': 'capital_components', 'group': 'Armor', 
     'volume': 10000, 'base_cost': 8500000, 'build_time': 43200, 'materials': [
        {'name': 'Tritanium', 'quantity': 2800000}, {'name': 'Pyerite', 'quantity': 650000},
        {'name': 'Mexallon', 'quantity': 152000}, {'name': 'Isogen', 'quantity': 35600},
        {'name': 'Nocxium', 'quantity': 7120}, {'name': 'Zydrine', 'quantity': 1780}
    ]},
    {'id': 1001, 'name': 'Capital Capacitor Battery Blueprint', 'category': 'capital_components', 'group': 'Capacitor',
     'volume': 10000, 'base_cost': 7200000, 'build_time': 38400, 'materials': [
        {'name': 'Tritanium', 'quantity': 2400000}, {'name': 'Pyerite', 'quantity': 560000},
        {'name': 'Mexallon', 'quantity': 131000}, {'name': 'Isogen', 'quantity': 30700},
        {'name': 'Nocxium', 'quantity': 6140}
    ]},
    {'id': 1002, 'name': 'Capital Cargo Bay Blueprint', 'category': 'capital_components', 'group': 'Structure',
     'volume': 10000, 'base_cost': 6500000, 'build_time': 36000, 'materials': [
        {'name': 'Tritanium', 'quantity': 2150000}, {'name': 'Pyerite', 'quantity': 502000},
        {'name': 'Mexallon', 'quantity': 117000}, {'name': 'Isogen', 'quantity': 27400}
    ]},
    {'id': 1003, 'name': 'Capital Computer System Blueprint', 'category': 'capital_components', 'group': 'Electronics',
     'volume': 10000, 'base_cost': 9200000, 'build_time': 48000, 'materials': [
        {'name': 'Tritanium', 'quantity': 3050000}, {'name': 'Pyerite', 'quantity': 711000},
        {'name': 'Mexallon', 'quantity': 166000}, {'name': 'Isogen', 'quantity': 38900},
        {'name': 'Nocxium', 'quantity': 7780}, {'name': 'Megacyte', 'quantity': 1950}
    ]},
    {'id': 1004, 'name': 'Capital Construction Parts Blueprint', 'category': 'capital_components', 'group': 'Structure',
     'volume': 10000, 'base_cost': 7800000, 'build_time': 40800, 'materials': [
        {'name': 'Tritanium', 'quantity': 2580000}, {'name': 'Pyerite', 'quantity': 602000},
        {'name': 'Mexallon', 'quantity': 140000}, {'name': 'Isogen', 'quantity': 32900},
        {'name': 'Nocxium', 'quantity': 6580}
    ]},
    {'id': 1005, 'name': 'Capital Corporate Hangar Bay Blueprint', 'category': 'capital_components', 'group': 'Structure',
     'volume': 10000, 'base_cost': 8800000, 'build_time': 45600, 'materials': [
        {'name': 'Tritanium', 'quantity': 2920000}, {'name': 'Pyerite', 'quantity': 680000},
        {'name': 'Mexallon', 'quantity': 158000}, {'name': 'Isogen', 'quantity': 37100},
        {'name': 'Nocxium', 'quantity': 7420}, {'name': 'Zydrine', 'quantity': 1850}
    ]},
    {'id': 1006, 'name': 'Capital Doomsday Weapon Mount Blueprint', 'category': 'capital_components', 'group': 'Weapons',
     'volume': 10000, 'base_cost': 25000000, 'build_time': 86400, 'materials': [
        {'name': 'Tritanium', 'quantity': 8250000}, {'name': 'Pyerite', 'quantity': 1925000},
        {'name': 'Mexallon', 'quantity': 448500}, {'name': 'Isogen', 'quantity': 105100},
        {'name': 'Nocxium', 'quantity': 21020}, {'name': 'Zydrine', 'quantity': 5255},
        {'name': 'Megacyte', 'quantity': 1314}, {'name': 'Morphite', 'quantity': 263}
    ]},
    {'id': 1007, 'name': 'Capital Drone Bay Blueprint', 'category': 'capital_components', 'group': 'Structure',
     'volume': 10000, 'base_cost': 6200000, 'build_time': 34800, 'materials': [
        {'name': 'Tritanium', 'quantity': 2050000}, {'name': 'Pyerite', 'quantity': 478000},
        {'name': 'Mexallon', 'quantity': 111000}, {'name': 'Isogen', 'quantity': 26100}
    ]},
    {'id': 1008, 'name': 'Capital Jump Bridge Array Blueprint', 'category': 'capital_components', 'group': 'Navigation',
     'volume': 10000, 'base_cost': 18000000, 'build_time': 72000, 'materials': [
        {'name': 'Tritanium', 'quantity': 5950000}, {'name': 'Pyerite', 'quantity': 1388000},
        {'name': 'Mexallon', 'quantity': 323500}, {'name': 'Isogen', 'quantity': 75800},
        {'name': 'Nocxium', 'quantity': 15160}, {'name': 'Zydrine', 'quantity': 3790},
        {'name': 'Megacyte', 'quantity': 948}
    ]},
    {'id': 1009, 'name': 'Capital Propulsion Engine Blueprint', 'category': 'capital_components', 'group': 'Propulsion',
     'volume': 10000, 'base_cost': 8500000, 'build_time': 43200, 'materials': [
        {'name': 'Tritanium', 'quantity': 2800000}, {'name': 'Pyerite', 'quantity': 653000},
        {'name': 'Mexallon', 'quantity': 152000}, {'name': 'Isogen', 'quantity': 35700},
        {'name': 'Nocxium', 'quantity': 7140}
    ]},
    {'id': 1010, 'name': 'Capital Sensor Cluster Blueprint', 'category': 'capital_components', 'group': 'Electronics',
     'volume': 10000, 'base_cost': 9500000, 'build_time': 46800, 'materials': [
        {'name': 'Tritanium', 'quantity': 3150000}, {'name': 'Pyerite', 'quantity': 734000},
        {'name': 'Mexallon', 'quantity': 171000}, {'name': 'Isogen', 'quantity': 40100},
        {'name': 'Megacyte', 'quantity': 2000}
    ]},
    {'id': 1011, 'name': 'Capital Shield Emitter Blueprint', 'category': 'capital_components', 'group': 'Shields',
     'volume': 10000, 'base_cost': 8200000, 'build_time': 42000, 'materials': [
        {'name': 'Tritanium', 'quantity': 2720000}, {'name': 'Pyerite', 'quantity': 634000},
        {'name': 'Mexallon', 'quantity': 148000}, {'name': 'Isogen', 'quantity': 34700},
        {'name': 'Nocxium', 'quantity': 6940}, {'name': 'Zydrine', 'quantity': 1740}
    ]},
    {'id': 1012, 'name': 'Capital Ship Maintenance Bay Blueprint', 'category': 'capital_components', 'group': 'Structure',
     'volume': 10000, 'base_cost': 9000000, 'build_time': 44400, 'materials': [
        {'name': 'Tritanium', 'quantity': 2980000}, {'name': 'Pyerite', 'quantity': 695000},
        {'name': 'Mexallon', 'quantity': 162000}, {'name': 'Isogen', 'quantity': 38000},
        {'name': 'Nocxium', 'quantity': 7600}, {'name': 'Zydrine', 'quantity': 1900}
    ]},
    {'id': 1013, 'name': 'Capital Siege Array Blueprint', 'category': 'capital_components', 'group': 'Weapons',
     'volume': 10000, 'base_cost': 22000000, 'build_time': 79200, 'materials': [
        {'name': 'Tritanium', 'quantity': 7260000}, {'name': 'Pyerite', 'quantity': 1694000},
        {'name': 'Mexallon', 'quantity': 394600}, {'name': 'Isogen', 'quantity': 92500},
        {'name': 'Nocxium', 'quantity': 18500}, {'name': 'Zydrine', 'quantity': 4625},
        {'name': 'Megacyte', 'quantity': 1156}
    ]},
    {'id': 1014, 'name': 'Capital Turret Hardpoint Blueprint', 'category': 'capital_components', 'group': 'Weapons',
     'volume': 10000, 'base_cost': 16000000, 'build_time': 64800, 'materials': [
        {'name': 'Tritanium', 'quantity': 5280000}, {'name': 'Pyerite', 'quantity': 1232000},
        {'name': 'Mexallon', 'quantity': 287000}, {'name': 'Isogen', 'quantity': 67300},
        {'name': 'Nocxium', 'quantity': 13460}, {'name': 'Megacyte', 'quantity': 3370}
    ]},
    
    # Tech 2 Capital Components
    {'id': 1100, 'name': 'Capital Antimatter Reactor Unit Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 35000000, 'build_time': 129600, 'materials': [
        {'name': 'Tritanium', 'quantity': 11550000}, {'name': 'Pyerite', 'quantity': 2695000},
        {'name': 'Mexallon', 'quantity': 628500}, {'name': 'Isogen', 'quantity': 147200},
        {'name': 'Nocxium', 'quantity': 29440}, {'name': 'Zydrine', 'quantity': 7360},
        {'name': 'Megacyte', 'quantity': 1840}, {'name': 'Morphite', 'quantity': 368}
    ]},
    {'id': 1101, 'name': 'Capital Crystalline Carbonide Armor Plate Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 28000000, 'build_time': 108000, 'materials': [
        {'name': 'Tritanium', 'quantity': 9240000}, {'name': 'Pyerite', 'quantity': 2156000},
        {'name': 'Mexallon', 'quantity': 502800}, {'name': 'Isogen', 'quantity': 117800},
        {'name': 'Nocxium', 'quantity': 23560}, {'name': 'Zydrine', 'quantity': 5890},
        {'name': 'Megacyte', 'quantity': 1470}, {'name': 'Morphite', 'quantity': 294}
    ]},
    {'id': 1102, 'name': 'Capital Fusion Reactor Unit Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 32000000, 'build_time': 115200, 'materials': [
        {'name': 'Tritanium', 'quantity': 10560000}, {'name': 'Pyerite', 'quantity': 2464000},
        {'name': 'Mexallon', 'quantity': 574600}, {'name': 'Isogen', 'quantity': 134700},
        {'name': 'Nocxium', 'quantity': 26940}, {'name': 'Zydrine', 'quantity': 6735},
        {'name': 'Megacyte', 'quantity': 1680}, {'name': 'Morphite', 'quantity': 336}
    ]},
    {'id': 1103, 'name': 'Capital Graviton Reactor Unit Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 33000000, 'build_time': 118800, 'materials': [
        {'name': 'Tritanium', 'quantity': 10890000}, {'name': 'Pyerite', 'quantity': 2541000},
        {'name': 'Mexallon', 'quantity': 592600}, {'name': 'Isogen', 'quantity': 138900},
        {'name': 'Nocxium', 'quantity': 27780}, {'name': 'Zydrine', 'quantity': 6945},
        {'name': 'Megacyte', 'quantity': 1740}, {'name': 'Morphite', 'quantity': 348}
    ]},
    {'id': 1104, 'name': 'Capital Ion Thruster Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 31000000, 'build_time': 111600, 'materials': [
        {'name': 'Tritanium', 'quantity': 10230000}, {'name': 'Pyerite', 'quantity': 2387000},
        {'name': 'Mexallon', 'quantity': 556800}, {'name': 'Isogen', 'quantity': 130500},
        {'name': 'Nocxium', 'quantity': 26100}, {'name': 'Zydrine', 'quantity': 6525},
        {'name': 'Megacyte', 'quantity': 1630}, {'name': 'Morphite', 'quantity': 326}
    ]},
    {'id': 1105, 'name': 'Capital Magnetometric Sensor Cluster Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 29000000, 'build_time': 104400, 'materials': [
        {'name': 'Tritanium', 'quantity': 9570000}, {'name': 'Pyerite', 'quantity': 2233000},
        {'name': 'Mexallon', 'quantity': 520800}, {'name': 'Isogen', 'quantity': 122100},
        {'name': 'Nocxium', 'quantity': 24420}, {'name': 'Zydrine', 'quantity': 6105},
        {'name': 'Megacyte', 'quantity': 1530}, {'name': 'Morphite', 'quantity': 306}
    ]},
    {'id': 1106, 'name': 'Capital Oscillator Capacitor Unit Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 34000000, 'build_time': 122400, 'materials': [
        {'name': 'Tritanium', 'quantity': 11220000}, {'name': 'Pyerite', 'quantity': 2618000},
        {'name': 'Mexallon', 'quantity': 610600}, {'name': 'Isogen', 'quantity': 143100},
        {'name': 'Nocxium', 'quantity': 28620}, {'name': 'Zydrine', 'quantity': 7155},
        {'name': 'Megacyte', 'quantity': 1790}, {'name': 'Morphite', 'quantity': 358}
    ]},
    {'id': 1107, 'name': 'Capital Plasma Thruster Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 30000000, 'build_time': 108000, 'materials': [
        {'name': 'Tritanium', 'quantity': 9900000}, {'name': 'Pyerite', 'quantity': 2310000},
        {'name': 'Mexallon', 'quantity': 538500}, {'name': 'Isogen', 'quantity': 126200},
        {'name': 'Nocxium', 'quantity': 25240}, {'name': 'Zydrine', 'quantity': 6310},
        {'name': 'Megacyte', 'quantity': 1580}, {'name': 'Morphite', 'quantity': 316}
    ]},
    {'id': 1108, 'name': 'Capital Pulse Shield Emitter Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 27000000, 'build_time': 97200, 'materials': [
        {'name': 'Tritanium', 'quantity': 8910000}, {'name': 'Pyerite', 'quantity': 2079000},
        {'name': 'Mexallon', 'quantity': 484800}, {'name': 'Isogen', 'quantity': 113600},
        {'name': 'Nocxium', 'quantity': 22720}, {'name': 'Zydrine', 'quantity': 5680},
        {'name': 'Megacyte', 'quantity': 1420}, {'name': 'Morphite', 'quantity': 284}
    ]},
    {'id': 1109, 'name': 'Capital Quantum Microprocessor Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 38000000, 'build_time': 136800, 'materials': [
        {'name': 'Tritanium', 'quantity': 12540000}, {'name': 'Pyerite', 'quantity': 2926000},
        {'name': 'Mexallon', 'quantity': 682600}, {'name': 'Isogen', 'quantity': 159900},
        {'name': 'Nocxium', 'quantity': 31980}, {'name': 'Zydrine', 'quantity': 7995},
        {'name': 'Megacyte', 'quantity': 2000}, {'name': 'Morphite', 'quantity': 400}
    ]},
    {'id': 1110, 'name': 'Capital Radar Sensor Cluster Blueprint', 'category': 'capital_components', 'group': 'Tech2',
     'volume': 10000, 'base_cost': 29500000, 'build_time': 106200, 'materials': [
        {'name': 'Tritanium', 'quantity': 9735000}, {'name': 'Pyerite', 'quantity': 2271500},
        {'name': 'Mexallon', 'quantity': 530200}, {'name': 'Isogen', 'quantity': 124250},
        {'name': 'Nocxium', 'quantity': 24850}, {'name': 'Zydrine', 'quantity': 6210},
        {'name': 'Megacyte', 'quantity': 1550}, {'name': 'Morphite', 'quantity': 310}
    ]},
]

# Tech 3 Materials and Components
T3_MATERIALS = {
    'Fullerite-C28': {'type_id': 30375, 'base_price': 15000},
    'Fullerite-C32': {'type_id': 30376, 'base_price': 15000},
    'Fullerite-C50': {'type_id': 30370, 'base_price': 12000},
    'Fullerite-C60': {'type_id': 30371, 'base_price': 12000},
    'Fullerite-C70': {'type_id': 30372, 'base_price': 12000},
    'Fullerite-C72': {'type_id': 30373, 'base_price': 12000},
    'Fullerite-C84': {'type_id': 30374, 'base_price': 12000},
    'Fullerite-C320': {'type_id': 30377, 'base_price': 18000},
    'Fullerite-C540': {'type_id': 30378, 'base_price': 18000},
    
    # Hybrid Polymers
    'C3-FTM Acid': {'type_id': 30382, 'base_price': 25000},
    'Carbon-86 Epoxy Resin': {'type_id': 30381, 'base_price': 25000},
    'Fullerene Intercalated Graphite': {'type_id': 30383, 'base_price': 25000},
    'Fulleroferrocene': {'type_id': 30384, 'base_price': 25000},
    'Graphene Nanoribbons': {'type_id': 30385, 'base_price': 25000},
    'Lanthanum Metallofullerene': {'type_id': 30386, 'base_price': 25000},
    'Methanofullerene': {'type_id': 30387, 'base_price': 25000},
    'PPD Fullerene Fibers': {'type_id': 30388, 'base_price': 25000},
    'Scandium Metallofullerene': {'type_id': 30389, 'base_price': 25000},
    
    # Hybrid Components
    'Complex Fullerene Ball': {'type_id': 30390, 'base_price': 50000},
    'Complex Reaction Intermediates': {'type_id': 30391, 'base_price': 50000},
    'Defective Current Pump': {'type_id': 30392, 'base_price': 50000},
    'Drifter Advanced Trigger Unit': {'type_id': 57466, 'base_price': 100000},
    'Drifter Advanced Thruster': {'type_id': 57467, 'base_price': 100000},
    'Drifter Advanced Sensor': {'type_id': 57468, 'base_price': 100000},
    'Drifter Advanced Powercore': {'type_id': 57469, 'base_price': 100000},
    'Drifter Advanced Processor': {'type_id': 57470, 'base_price': 100000},
    'Drifter Advanced Capacitor': {'type_id': 57471, 'base_price': 100000},
    'Drifter Advanced Hull': {'type_id': 57472, 'base_price': 100000},
    'Drifter Advanced Firewall': {'type_id': 57473, 'base_price': 100000},
    'Drifter Advanced Focusing': {'type_id': 57474, 'base_price': 100000},
    'Drifter Advanced Interface': {'type_price': 57475, 'base_price': 100000},
    'Drifter Advanced Lenses': {'type_id': 57476, 'base_price': 100000},
    'Drifter Advanced Multiplexer': {'type_id': 57477, 'base_price': 100000},
}

# Salvage Materials
SALVAGE_MATERIALS = {
    'Alloyed Tritanium Bar': {'type_id': 30420, 'base_price': 2000},
    'Armor Plates': {'type_id': 25625, 'base_price': 5000},
    'Artificial Neural Network': {'type_id': 25627, 'base_price': 10000},
    'Broken Drone Transceiver': {'type_id': 25629, 'base_price': 3000},
    'Burned Logic Circuit': {'type_id': 25631, 'base_price': 15000},
    'Capacitor Console': {'type_id': 25633, 'base_price': 25000},
    'Charred Micro Circuit': {'type_id': 25635, 'base_price': 800},
    'Conductive Polymer': {'type_id': 25637, 'base_price': 2500},
    'Conductive Thermoplastic': {'type_id': 25639, 'base_price': 3000},
    'Contaminated Lorentz Fluid': {'type_id': 25641, 'base_price': 12000},
    'Contaminated Nanite Polymer': {'type_id': 25643, 'base_price': 8000},
    'Damaged Artificial Neural Network': {'type_id': 25645, 'base_price': 4000},
    'Defective Current Pump': {'type_id': 25647, 'base_price': 2500},
    'Drone Transceiver': {'type_id': 25649, 'base_price': 8000},
    'Electromagnetic Metaprismatic Sheeting': {'type_id': 25651, 'base_price': 18000},
    'Enhanced Ward Console': {'type_id': 25653, 'base_price': 35000},
    'Fried Interface Circuit': {'type_id': 25655, 'base_price': 5000},
    'Impetus Console': {'type_id': 25657, 'base_price': 20000},
    'Intact Armor Plates': {'type_id': 25659, 'base_price': 80000},
    'Intact Shield Emitter': {'type_id': 25661, 'base_price': 75000},
    'Interface Circuit': {'type_id': 25663, 'base_price': 12000},
    'Logic Circuit': {'type_id': 25665, 'base_price': 35000},
    'Lorentz Fluid': {'type_id': 25667, 'base_price': 50000},
    'Malfunctioning Shield Emitter': {'type_id': 25669, 'base_price': 3000},
    'Melted Capacitor Console': {'type_id': 25671, 'base_price': 15000},
    'Micro Circuit': {'type_id': 25673, 'base_price': 15000},
    'Nanite Compound': {'type_id': 25675, 'base_price': 55000},
    'Power Circuit': {'type_id': 25677, 'base_price': 65000},
    'Power Conduit': {'type_id': 25679, 'base_price': 28000},
    'Scorched Telemetry Processor': {'type_id': 25681, 'base_price': 1800},
    'Single-crystal Superalloy I-beam': {'type_id': 25683, 'base_price': 25000},
    'Smashed Trigger Unit': {'type_id': 25685, 'base_price': 2000},
    'Tangled Power Conduit': {'type_id': 25687, 'base_price': 4500},
    'Telemetry Processor': {'type_id': 25689, 'base_price': 22000},
    'Thruster Console': {'type_id': 25691, 'base_price': 20000},
    'Tripped Power Circuit': {'type_id': 25693, 'base_price': 10000},
    'Ward Console': {'type_id': 25695, 'base_price': 50000},
}

# Ancient Salvage (for T3)
ANCIENT_SALVAGE = {
    'Ancient Armor Plates': {'type_id': 30634, 'base_price': 150000},
    'Ancient Casing': {'type_id': 30632, 'base_price': 120000},
    'Ancient Circuitry': {'type_id': 30636, 'base_price': 180000},
    'Ancient Compressor': {'type_id': 30638, 'base_price': 200000},
    'Ancient Control Unit': {'type_id': 30640, 'base_price': 220000},
    'Ancient Co-processor': {'type_id': 30642, 'base_price': 250000},
    'Ancient Crystal Cylinder': {'type_id': 30644, 'base_price': 160000},
    'Ancient Defensive Layering': {'type_id': 30646, 'base_price': 280000},
    'Ancient Friction Sheet': {'type_id': 30648, 'base_price': 140000},
    'Ancient Hull Section': {'type_id': 30650, 'base_price': 300000},
    'Ancient Integrated Analyzer': {'type_id': 30652, 'base_price': 350000},
    'Ancient Interface Circuits': {'type_id': 30654, 'base_price': 320000},
    'Ancient Kinetic Deflection Field': {'type_id': 30656, 'base_price': 400000},
    'Ancient Lateral Thrusters': {'type_id': 30658, 'base_price': 180000},
    'Ancient Nanostructures': {'type_id': 30660, 'base_price': 500000},
    'Ancient Neural Networks': {'type_id': 30662, 'base_price': 450000},
    'Ancient Particle Accelerator': {'type_id': 30664, 'base_price': 550000},
    'Ancient Plasma Membranes': {'type_id': 30666, 'base_price': 380000},
    'Ancient Power Cores': {'type_id': 30668, 'base_price': 600000},
    'Ancient Shield Emitters': {'type_id': 30670, 'base_price': 480000},
    'Ancient Thruster Devices': {'type_id': 30672, 'base_price': 220000},
    'Ancient Weapon Modules': {'type_id': 30674, 'base_price': 650000},
}

# Combine all databases
ALL_COMPONENT_DATABASE = CAPITAL_COMPONENT_BLUEPRINTS

print(f"Advanced materials database loaded:")
print(f"  - {len(ADVANCED_MATERIALS)} moon materials")
print(f"  - {len(REACTION_MATERIALS)} reaction materials")
print(f"  - {len(T3_MATERIALS)} T3 materials")
print(f"  - {len(SALVAGE_MATERIALS)} salvage materials")
print(f"  - {len(ANCIENT_SALVAGE)} ancient salvage")
print(f"  - {len(CAPITAL_COMPONENT_BLUEPRINTS)} capital component blueprints")
print(f"Total: {len(ADVANCED_MATERIALS) + len(REACTION_MATERIALS) + len(T3_MATERIALS) + len(SALVAGE_MATERIALS) + len(ANCIENT_SALVAGE) + len(CAPITAL_COMPONENT_BLUEPRINTS)} entries")
