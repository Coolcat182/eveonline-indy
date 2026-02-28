# Capital Ships, Structures, and Advanced Modules Database
# Import this file in bot.py: from capital_database import CAPITAL_DATABASE, CAPITAL_COMPONENTS, STRUCTURE_DATABASE

CAPITAL_DATABASE = [
    # ========== CARRIERS ==========
    {
        'id': 600, 'name': 'Thanatos Blueprint', 'category': 'capital_ships', 'group': 'Carriers', 
        'volume': 15000000, 'base_cost': 1850000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 95000000}, {'name': 'Pyerite', 'quantity': 32000000},
            {'name': 'Mexallon', 'quantity': 8500000}, {'name': 'Isogen', 'quantity': 2100000},
            {'name': 'Nocxium', 'quantity': 450000}, {'name': 'Zydrine', 'quantity': 125000},
            {'name': 'Megacyte', 'quantity': 32000}
        ]
    },
    {
        'id': 601, 'name': 'Archon Blueprint', 'category': 'capital_ships', 'group': 'Carriers',
        'volume': 15000000, 'base_cost': 1900000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 98000000}, {'name': 'Pyerite', 'quantity': 33000000},
            {'name': 'Mexallon', 'quantity': 8800000}, {'name': 'Isogen', 'quantity': 2180000},
            {'name': 'Nocxium', 'quantity': 465000}, {'name': 'Zydrine', 'quantity': 130000},
            {'name': 'Megacyte', 'quantity': 33500}
        ]
    },
    {
        'id': 602, 'name': 'Chimera Blueprint', 'category': 'capital_ships', 'group': 'Carriers',
        'volume': 15000000, 'base_cost': 1880000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 97000000}, {'name': 'Pyerite', 'quantity': 32500000},
            {'name': 'Mexallon', 'quantity': 8650000}, {'name': 'Isogen', 'quantity': 2140000},
            {'name': 'Nocxium', 'quantity': 458000}, {'name': 'Zydrine', 'quantity': 128000},
            {'name': 'Megacyte', 'quantity': 32800}
        ]
    },
    {
        'id': 603, 'name': 'Nidhoggur Blueprint', 'category': 'capital_ships', 'group': 'Carriers',
        'volume': 15000000, 'base_cost': 1860000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 95500000}, {'name': 'Pyerite', 'quantity': 32200000},
            {'name': 'Mexallon', 'quantity': 8550000}, {'name': 'Isogen', 'quantity': 2120000},
            {'name': 'Nocxium', 'quantity': 452000}, {'name': 'Zydrine', 'quantity': 126000},
            {'name': 'Megacyte', 'quantity': 32400}
        ]
    },
    
    # ========== DREADNOUGHTS ==========
    {
        'id': 610, 'name': 'Moros Blueprint', 'category': 'capital_ships', 'group': 'Dreadnoughts',
        'volume': 15000000, 'base_cost': 2100000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 110000000}, {'name': 'Pyerite', 'quantity': 38000000},
            {'name': 'Mexallon', 'quantity': 10000000}, {'name': 'Isogen', 'quantity': 2500000},
            {'name': 'Nocxium', 'quantity': 540000}, {'name': 'Zydrine', 'quantity': 150000},
            {'name': 'Megacyte', 'quantity': 38000}
        ]
    },
    {
        'id': 611, 'name': 'Revelation Blueprint', 'category': 'capital_ships', 'group': 'Dreadnoughts',
        'volume': 15000000, 'base_cost': 2150000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 113000000}, {'name': 'Pyerite', 'quantity': 39000000},
            {'name': 'Mexallon', 'quantity': 10200000}, {'name': 'Isogen', 'quantity': 2580000},
            {'name': 'Nocxium', 'quantity': 558000}, {'name': 'Zydrine', 'quantity': 156000},
            {'name': 'Megacyte', 'quantity': 39500}
        ]
    },
    {
        'id': 612, 'name': 'Phoenix Blueprint', 'category': 'capital_ships', 'group': 'Dreadnoughts',
        'volume': 15000000, 'base_cost': 2120000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 111000000}, {'name': 'Pyerite', 'quantity': 38500000},
            {'name': 'Mexallon', 'quantity': 10100000}, {'name': 'Isogen', 'quantity': 2540000},
            {'name': 'Nocxium', 'quantity': 549000}, {'name': 'Zydrine', 'quantity': 153000},
            {'name': 'Megacyte', 'quantity': 38700}
        ]
    },
    {
        'id': 613, 'name': 'Naglfar Blueprint', 'category': 'capital_ships', 'group': 'Dreadnoughts',
        'volume': 15000000, 'base_cost': 2080000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 108000000}, {'name': 'Pyerite', 'quantity': 37500000},
            {'name': 'Mexallon', 'quantity': 9900000}, {'name': 'Isogen', 'quantity': 2480000},
            {'name': 'Nocxium', 'quantity': 535000}, {'name': 'Zydrine', 'quantity': 148000},
            {'name': 'Megacyte', 'quantity': 37500}
        ]
    },
    
    # ========== FORCE AUXILIARIES ==========
    {
        'id': 620, 'name': 'Apostle Blueprint', 'category': 'capital_ships', 'group': 'Force Auxiliaries',
        'volume': 15000000, 'base_cost': 1950000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 102000000}, {'name': 'Pyerite', 'quantity': 34500000},
            {'name': 'Mexallon', 'quantity': 9200000}, {'name': 'Isogen', 'quantity': 2280000},
            {'name': 'Nocxium', 'quantity': 485000}, {'name': 'Zydrine', 'quantity': 135000},
            {'name': 'Megacyte', 'quantity': 34200}
        ]
    },
    {
        'id': 621, 'name': 'Minokawa Blueprint', 'category': 'capital_ships', 'group': 'Force Auxiliaries',
        'volume': 15000000, 'base_cost': 1920000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 100000000}, {'name': 'Pyerite', 'quantity': 33800000},
            {'name': 'Mexallon', 'quantity': 9050000}, {'name': 'Isogen', 'quantity': 2240000},
            {'name': 'Nocxium', 'quantity': 476000}, {'name': 'Zydrine', 'quantity': 132000},
            {'name': 'Megacyte', 'quantity': 33500}
        ]
    },
    {
        'id': 622, 'name': 'Lif Blueprint', 'category': 'capital_ships', 'group': 'Force Auxiliaries',
        'volume': 15000000, 'base_cost': 1900000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 98500000}, {'name': 'Pyerite', 'quantity': 33200000},
            {'name': 'Mexallon', 'quantity': 8900000}, {'name': 'Isogen', 'quantity': 2200000},
            {'name': 'Nocxium', 'quantity': 468000}, {'name': 'Zydrine', 'quantity': 130000},
            {'name': 'Megacyte', 'quantity': 32800}
        ]
    },
    {
        'id': 623, 'name': 'Ninazu Blueprint', 'category': 'capital_ships', 'group': 'Force Auxiliaries',
        'volume': 15000000, 'base_cost': 1930000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 101000000}, {'name': 'Pyerite', 'quantity': 34200000},
            {'name': 'Mexallon', 'quantity': 9150000}, {'name': 'Isogen', 'quantity': 2260000},
            {'name': 'Nocxium', 'quantity': 480000}, {'name': 'Zydrine', 'quantity': 133000},
            {'name': 'Megacyte', 'quantity': 33800}
        ]
    },
    
    # ========== SUPERCARRIERS ==========
    {
        'id': 630, 'name': 'Nyx Blueprint', 'category': 'capital_ships', 'group': 'Supercarriers',
        'volume': 50000000, 'base_cost': 25000000000, 'build_time': 864000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 1250000000}, {'name': 'Pyerite', 'quantity': 420000000},
            {'name': 'Mexallon', 'quantity': 112000000}, {'name': 'Isogen', 'quantity': 28000000},
            {'name': 'Nocxium', 'quantity': 6000000}, {'name': 'Zydrine', 'quantity': 1650000},
            {'name': 'Megacyte', 'quantity': 420000}, {'name': 'Morphite', 'quantity': 85000}
        ]
    },
    {
        'id': 631, 'name': 'Aeon Blueprint', 'category': 'capital_ships', 'group': 'Supercarriers',
        'volume': 50000000, 'base_cost': 25500000000, 'build_time': 864000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 1280000000}, {'name': 'Pyerite', 'quantity': 432000000},
            {'name': 'Mexallon', 'quantity': 115000000}, {'name': 'Isogen', 'quantity': 28800000},
            {'name': 'Nocxium', 'quantity': 6180000}, {'name': 'Zydrine', 'quantity': 1700000},
            {'name': 'Megacyte', 'quantity': 432000}, {'name': 'Morphite', 'quantity': 87500}
        ]
    },
    {
        'id': 632, 'name': 'Wyvern Blueprint', 'category': 'capital_ships', 'group': 'Supercarriers',
        'volume': 50000000, 'base_cost': 25200000000, 'build_time': 864000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 1260000000}, {'name': 'Pyerite', 'quantity': 425000000},
            {'name': 'Mexallon', 'quantity': 113000000}, {'name': 'Isogen', 'quantity': 28400000},
            {'name': 'Nocxium', 'quantity': 6080000}, {'name': 'Zydrine', 'quantity': 1670000},
            {'name': 'Megacyte', 'quantity': 425000}, {'name': 'Morphite', 'quantity': 86000}
        ]
    },
    {
        'id': 633, 'name': 'Hel Blueprint', 'category': 'capital_ships', 'group': 'Supercarriers',
        'volume': 50000000, 'base_cost': 24800000000, 'build_time': 864000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 1240000000}, {'name': 'Pyerite', 'quantity': 418000000},
            {'name': 'Mexallon', 'quantity': 111000000}, {'name': 'Isogen', 'quantity': 27800000},
            {'name': 'Nocxium', 'quantity': 5950000}, {'name': 'Zydrine', 'quantity': 1630000},
            {'name': 'Megacyte', 'quantity': 415000}, {'name': 'Morphite', 'quantity': 84000}
        ]
    },
    
    # ========== TITANS ==========
    {
        'id': 640, 'name': 'Erebus Blueprint', 'category': 'capital_ships', 'group': 'Titans',
        'volume': 100000000, 'base_cost': 100000000000, 'build_time': 1728000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 5500000000}, {'name': 'Pyerite', 'quantity': 1850000000},
            {'name': 'Mexallon', 'quantity': 495000000}, {'name': 'Isogen', 'quantity': 123000000},
            {'name': 'Nocxium', 'quantity': 26400000}, {'name': 'Zydrine', 'quantity': 7250000},
            {'name': 'Megacyte', 'quantity': 1850000}, {'name': 'Morphite', 'quantity': 375000}
        ]
    },
    {
        'id': 641, 'name': 'Avatar Blueprint', 'category': 'capital_ships', 'group': 'Titans',
        'volume': 100000000, 'base_cost': 105000000000, 'build_time': 1728000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 5800000000}, {'name': 'Pyerite', 'quantity': 1950000000},
            {'name': 'Mexallon', 'quantity': 520000000}, {'name': 'Isogen', 'quantity': 130000000},
            {'name': 'Nocxium', 'quantity': 27800000}, {'name': 'Zydrine', 'quantity': 7650000},
            {'name': 'Megacyte', 'quantity': 1950000}, {'name': 'Morphite', 'quantity': 395000}
        ]
    },
    {
        'id': 642, 'name': 'Ragnarok Blueprint', 'category': 'capital_ships', 'group': 'Titans',
        'volume': 100000000, 'base_cost': 102000000000, 'build_time': 1728000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 5600000000}, {'name': 'Pyerite', 'quantity': 1880000000},
            {'name': 'Mexallon', 'quantity': 505000000}, {'name': 'Isogen', 'quantity': 125000000},
            {'name': 'Nocxium', 'quantity': 26800000}, {'name': 'Zydrine', 'quantity': 7400000},
            {'name': 'Megacyte', 'quantity': 1880000}, {'name': 'Morphite', 'quantity': 380000}
        ]
    },
    {
        'id': 643, 'name': 'Leviathan Blueprint', 'category': 'capital_ships', 'group': 'Titans',
        'volume': 100000000, 'base_cost': 103000000000, 'build_time': 1728000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 5650000000}, {'name': 'Pyerite', 'quantity': 1900000000},
            {'name': 'Mexallon', 'quantity': 510000000}, {'name': 'Isogen', 'quantity': 126000000},
            {'name': 'Nocxium', 'quantity': 27000000}, {'name': 'Zydrine', 'quantity': 7450000},
            {'name': 'Megacyte', 'quantity': 1900000}, {'name': 'Morphite', 'quantity': 385000}
        ]
    },
    
    # ========== FREIGHTERS & JUMP FREIGHTERS ==========
    {
        'id': 650, 'name': 'Charon Blueprint', 'category': 'capital_ships', 'group': 'Freighters',
        'volume': 20000000, 'base_cost': 8500000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 450000000}, {'name': 'Pyerite', 'quantity': 150000000},
            {'name': 'Mexallon', 'quantity': 37500000}, {'name': 'Isogen', 'quantity': 9200000},
            {'name': 'Nocxium', 'quantity': 1950000}, {'name': 'Zydrine', 'quantity': 540000},
            {'name': 'Megacyte', 'quantity': 138000}
        ]
    },
    {
        'id': 651, 'name': 'Providence Blueprint', 'category': 'capital_ships', 'group': 'Freighters',
        'volume': 20000000, 'base_cost': 8300000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 440000000}, {'name': 'Pyerite', 'quantity': 146000000},
            {'name': 'Mexallon', 'quantity': 36500000}, {'name': 'Isogen', 'quantity': 9000000},
            {'name': 'Nocxium', 'quantity': 1900000}, {'name': 'Zydrine', 'quantity': 525000},
            {'name': 'Megacyte', 'quantity': 134000}
        ]
    },
    {
        'id': 652, 'name': 'Obelisk Blueprint', 'category': 'capital_ships', 'group': 'Freighters',
        'volume': 20000000, 'base_cost': 8400000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 445000000}, {'name': 'Pyerite', 'quantity': 148000000},
            {'name': 'Mexallon', 'quantity': 37000000}, {'name': 'Isogen', 'quantity': 9100000},
            {'name': 'Nocxium', 'quantity': 1925000}, {'name': 'Zydrine', 'quantity': 532500},
            {'name': 'Megacyte', 'quantity': 136000}
        ]
    },
    {
        'id': 653, 'name': 'Fenrir Blueprint', 'category': 'capital_ships', 'group': 'Freighters',
        'volume': 20000000, 'base_cost': 8200000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 435000000}, {'name': 'Pyerite', 'quantity': 144000000},
            {'name': 'Mexallon', 'quantity': 36000000}, {'name': 'Isogen', 'quantity': 8900000},
            {'name': 'Nocxium', 'quantity': 1875000}, {'name': 'Zydrine', 'quantity': 517500},
            {'name': 'Megacyte', 'quantity': 132000}
        ]
    },
    
    # Jump Freighters
    {
        'id': 660, 'name': 'Rhea Blueprint', 'category': 'capital_ships', 'group': 'Jump Freighters',
        'volume': 20000000, 'base_cost': 9500000000, 'build_time': 518400,
        'materials': [
            {'name': 'Tritanium', 'quantity': 520000000}, {'name': 'Pyerite', 'quantity': 172000000},
            {'name': 'Mexallon', 'quantity': 43000000}, {'name': 'Isogen', 'quantity': 10600000},
            {'name': 'Nocxium', 'quantity': 2250000}, {'name': 'Zydrine', 'quantity': 625000},
            {'name': 'Megacyte', 'quantity': 159000}
        ]
    },
    {
        'id': 661, 'name': 'Anshar Blueprint', 'category': 'capital_ships', 'group': 'Jump Freighters',
        'volume': 20000000, 'base_cost': 9300000000, 'build_time': 518400,
        'materials': [
            {'name': 'Tritanium', 'quantity': 510000000}, {'name': 'Pyerite', 'quantity': 168000000},
            {'name': 'Mexallon', 'quantity': 42000000}, {'name': 'Isogen', 'quantity': 10400000},
            {'name': 'Nocxium', 'quantity': 2200000}, {'name': 'Zydrine', 'quantity': 612500},
            {'name': 'Megacyte', 'quantity': 155000}
        ]
    },
    {
        'id': 662, 'name': 'Ark Blueprint', 'category': 'capital_ships', 'group': 'Jump Freighters',
        'volume': 20000000, 'base_cost': 9400000000, 'build_time': 518400,
        'materials': [
            {'name': 'Tritanium', 'quantity': 515000000}, {'name': 'Pyerite', 'quantity': 170000000},
            {'name': 'Mexallon', 'quantity': 42500000}, {'name': 'Isogen', 'quantity': 10500000},
            {'name': 'Nocxium', 'quantity': 2225000}, {'name': 'Zydrine', 'quantity': 618750},
            {'name': 'Megacyte', 'quantity': 157000}
        ]
    },
    {
        'id': 663, 'name': 'Nomad Blueprint', 'category': 'capital_ships', 'group': 'Jump Freighters',
        'volume': 20000000, 'base_cost': 9200000000, 'build_time': 518400,
        'materials': [
            {'name': 'Tritanium', 'quantity': 505000000}, {'name': 'Pyerite', 'quantity': 166000000},
            {'name': 'Mexallon', 'quantity': 41500000}, {'name': 'Isogen', 'quantity': 10300000},
            {'name': 'Nocxium', 'quantity': 2175000}, {'name': 'Zydrine', 'quantity': 606250},
            {'name': 'Megacyte', 'quantity': 153000}
        ]
    },
    
    # ========== ORCAS & RORQUALS ==========
    {
        'id': 670, 'name': 'Orca Blueprint', 'category': 'capital_ships', 'group': 'Industrial Command Ships',
        'volume': 15000000, 'base_cost': 750000000, 'build_time': 345600,
        'materials': [
            {'name': 'Tritanium', 'quantity': 38000000}, {'name': 'Pyerite', 'quantity': 12600000},
            {'name': 'Mexallon', 'quantity': 3150000}, {'name': 'Isogen', 'quantity': 780000},
            {'name': 'Nocxium', 'quantity': 165000}, {'name': 'Zydrine', 'quantity': 45800},
            {'name': 'Megacyte', 'quantity': 11600}
        ]
    },
    {
        'id': 671, 'name': 'Rorqual Blueprint', 'category': 'capital_ships', 'group': 'Capital Industrial Ships',
        'volume': 15000000, 'base_cost': 1200000000, 'build_time': 432000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 62000000}, {'name': 'Pyerite', 'quantity': 20800000},
            {'name': 'Mexallon', 'quantity': 5200000}, {'name': 'Isogen', 'quantity': 1280000},
            {'name': 'Nocxium', 'quantity': 272000}, {'name': 'Zydrine', 'quantity': 75500},
            {'name': 'Megacyte', 'quantity': 19200}
        ]
    },
]

# Capital Components for building
CAPITAL_COMPONENTS = [
    {'name': 'Capital Armor Plates', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Zydrine']},
    {'name': 'Capital Capacitor Battery', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium']},
    {'name': 'Capital Cargo Bay', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen']},
    {'name': 'Capital Computer System', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium', 'Megacyte']},
    {'name': 'Capital Construction Parts', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium']},
    {'name': 'Capital Corporate Hangar Bay', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Zydrine']},
    {'name': 'Capital Doomsday Weapon Mount', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium', 'Zydrine', 'Megacyte', 'Morphite']},
    {'name': 'Capital Drone Bay', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen']},
    {'name': 'Capital Jump Bridge Array', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium', 'Zydrine', 'Megacyte']},
    {'name': 'Capital Propulsion Engine', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium']},
    {'name': 'Capital Sensor Cluster', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Megacyte']},
    {'name': 'Capital Shield Emitter', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Zydrine']},
    {'name': 'Capital Ship Maintenance Bay', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Zydrine']},
    {'name': 'Capital Siege Array', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium', 'Zydrine', 'Megacyte']},
    {'name': 'Capital Turret Hardpoint', 'materials': ['Tritanium', 'Pyerite', 'Mexallon', 'Isogen', 'Nocxium', 'Megacyte']},
]

# Structure modules (Citadel, Engineering Complex)
STRUCTURE_DATABASE = [
    # Astrahus (Medium Citadel)
    {
        'id': 700, 'name': 'Astrahus Blueprint', 'category': 'structures', 'group': 'Citadels',
        'volume': 8000, 'base_cost': 2500000000, 'build_time': 648000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 125000000}, {'name': 'Pyerite', 'quantity': 42000000},
            {'name': 'Mexallon', 'quantity': 10500000}, {'name': 'Isogen', 'quantity': 2600000},
            {'name': 'Nocxium', 'quantity': 550000}, {'name': 'Zydrine', 'quantity': 152000},
            {'name': 'Megacyte', 'quantity': 38500}
        ]
    },
    # Fortizar (Large Citadel)
    {
        'id': 701, 'name': 'Fortizar Blueprint', 'category': 'structures', 'group': 'Citadels',
        'volume': 80000, 'base_cost': 15000000000, 'build_time': 1296000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 650000000}, {'name': 'Pyerite', 'quantity': 218000000},
            {'name': 'Mexallon', 'quantity': 54500000}, {'name': 'Isogen', 'quantity': 13500000},
            {'name': 'Nocxium', 'quantity': 2850000}, {'name': 'Zydrine', 'quantity': 792000},
            {'name': 'Megacyte', 'quantity': 200000}
        ]
    },
    # Keepstar (XL Citadel)
    {
        'id': 702, 'name': 'Keepstar Blueprint', 'category': 'structures', 'group': 'Citadels',
        'volume': 3200000, 'base_cost': 200000000000, 'build_time': 2592000,
        'materials': [
            {'name': 'Tritanium', 'quantity': 8000000000}, {'name': 'Pyerite', 'quantity': 2680000000},
            {'name': 'Mexallon', 'quantity': 670000000}, {'name': 'Isogen', 'quantity': 166000000},
            {'name': 'Nocxium', 'quantity': 35000000}, {'name': 'Zydrine', 'quantity': 9720000},
            {'name': 'Megacyte', 'quantity': 2450000}
        ]
    },
    # Raitaru (Medium Engineering Complex)
    {
        'id': 710, 'name': 'Raitaru Blueprint', 'category': 'structures', 'group': 'Engineering Complexes',
        'volume': 8000, 'base_cost': 1800000000, 'build_time': 518400,
        'materials': [
            {'name': 'Tritanium', 'quantity': 95000000}, {'name': 'Pyerite', 'quantity': 31800000},
            {'name': 'Mexallon', 'quantity': 7950000}, {'name': 'Isogen', 'quantity': 1970000},
            {'name': 'Nocxium', 'quantity': 416000}, {'name': 'Zydrine', 'quantity': 115000},
            {'name': 'Megacyte', 'quantity': 29200}
        ]
    },
    # Azbel (Large Engineering Complex)
    {
        'id': 711, 'name': 'Azbel Blueprint', 'category': 'structures', 'group': 'Engineering Complexes',
        'volume': 80000, 'base_cost': 10000000000, 'build_time': 1036800,
        'materials': [
            {'name': 'Tritanium', 'quantity': 480000000}, {'name': 'Pyerite', 'quantity': 160000000},
            {'name': 'Mexallon', 'quantity': 40000000}, {'name': 'Isogen', 'quantity': 9900000},
            {'name': 'Nocxium', 'quantity': 2090000}, {'name': 'Zydrine', 'quantity': 580000},
            {'name': 'Megacyte', 'quantity': 146000}
        ]
    },
    # Sotiyo (XL Engineering Complex)
    {
        'id': 712, 'name': 'Sotiyo Blueprint', 'category': 'structures', 'group': 'Engineering Complexes',
        'volume': 3200000, 'base_cost': 120000000000, 'build_time': 2073600,
        'materials': [
            {'name': 'Tritanium', 'quantity': 5600000000}, {'name': 'Pyerite', 'quantity': 1860000000},
            {'name': 'Mexallon', 'quantity': 465000000}, {'name': 'Isogen', 'quantity': 115000000},
            {'name': 'Nocxium', 'quantity': 24300000}, {'name': 'Zydrine', 'quantity': 6750000},
            {'name': 'Megacyte', 'quantity': 1700000}
        ]
    },
    # Athanor (Medium Refinery)
    {
        'id': 720, 'name': 'Athanor Blueprint', 'category': 'structures', 'group': 'Refineries',
        'volume': 8000, 'base_cost': 1500000000, 'build_time': 518400,
        'materials': [
            {'name': 'Tritanium', 'quantity': 82000000}, {'name': 'Pyerite', 'quantity': 27400000},
            {'name': 'Mexallon', 'quantity': 6850000}, {'name': 'Isogen', 'quantity': 1690000},
            {'name': 'Nocxium', 'quantity': 357000}, {'name': 'Zydrine', 'quantity': 99000},
            {'name': 'Megacyte', 'quantity': 25000}
        ]
    },
    # Tatara (Large Refinery)
    {
        'id': 721, 'name': 'Tatara Blueprint', 'category': 'structures', 'group': 'Refineries',
        'volume': 80000, 'base_cost': 8000000000, 'build_time': 1036800,
        'materials': [
            {'name': 'Tritanium', 'quantity': 420000000}, {'name': 'Pyerite', 'quantity': 140000000},
            {'name': 'Mexallon', 'quantity': 35000000}, {'name': 'Isogen', 'quantity': 8650000},
            {'name': 'Nocxium', 'quantity': 1825000}, {'name': 'Zydrine', 'quantity': 506000},
            {'name': 'Megacyte', 'quantity': 128000}
        ]
    },
]

# Advanced capital modules
CAPITAL_MODULES = [
    # Shield Modules
    {'id': 800, 'name': 'Capital Shield Booster I Blueprint', 'category': 'capital_modules', 'group': 'Shields',
     'volume': 4000, 'base_cost': 850000, 'build_time': 12000, 'materials': [
         {'name': 'Tritanium', 'quantity': 850000}, {'name': 'Pyerite', 'quantity': 198000},
         {'name': 'Mexallon', 'quantity': 46200}, {'name': 'Isogen', 'quantity': 11000},
         {'name': 'Nocxium', 'quantity': 2200}, {'name': 'Zydrine', 'quantity': 550}
     ]},
    {'id': 801, 'name': 'Capital Shield Extender I Blueprint', 'category': 'capital_modules', 'group': 'Shields',
     'volume': 4000, 'base_cost': 620000, 'build_time': 9500, 'materials': [
         {'name': 'Tritanium', 'quantity': 620000}, {'name': 'Pyerite', 'quantity': 145000},
         {'name': 'Mexallon', 'quantity': 33800}, {'name': 'Isogen', 'quantity': 8000}
     ]},
    {'id': 802, 'name': 'Capital Shield Hardener I Blueprint', 'category': 'capital_modules', 'group': 'Shields',
     'volume': 4000, 'base_cost': 780000, 'build_time': 11000, 'materials': [
         {'name': 'Tritanium', 'quantity': 780000}, {'name': 'Pyerite', 'quantity': 182000},
         {'name': 'Mexallon', 'quantity': 42500}, {'name': 'Isogen', 'quantity': 10000},
         {'name': 'Nocxium', 'quantity': 2000}
     ]},
    
    # Armor Modules
    {'id': 810, 'name': 'Capital Armor Repairer I Blueprint', 'category': 'capital_modules', 'group': 'Armor',
     'volume': 4000, 'base_cost': 820000, 'build_time': 11500, 'materials': [
         {'name': 'Tritanium', 'quantity': 820000}, {'name': 'Pyerite', 'quantity': 191000},
         {'name': 'Mexallon', 'quantity': 44700}, {'name': 'Isogen', 'quantity': 10500},
         {'name': 'Nocxium', 'quantity': 2100}
     ]},
    {'id': 811, 'name': 'Capital Armor Plate I Blueprint', 'category': 'capital_modules', 'group': 'Armor',
     'volume': 4000, 'base_cost': 580000, 'build_time': 8800, 'materials': [
         {'name': 'Tritanium', 'quantity': 580000}, {'name': 'Pyerite', 'quantity': 135000},
         {'name': 'Mexallon', 'quantity': 31500}, {'name': 'Isogen', 'quantity': 7400}
     ]},
    {'id': 812, 'name': 'Capital Armor Hardener I Blueprint', 'category': 'capital_modules', 'group': 'Armor',
     'volume': 4000, 'base_cost': 750000, 'build_time': 10500, 'materials': [
         {'name': 'Tritanium', 'quantity': 750000}, {'name': 'Pyerite', 'quantity': 175000},
         {'name': 'Mexallon', 'quantity': 40800}, {'name': 'Isogen', 'quantity': 9600},
         {'name': 'Nocxium', 'quantity': 1920}
     ]},
    
    # Capacitor Modules
    {'id': 820, 'name': 'Capital Capacitor Booster I Blueprint', 'category': 'capital_modules', 'group': 'Capacitor',
     'volume': 4000, 'base_cost': 720000, 'build_time': 10000, 'materials': [
         {'name': 'Tritanium', 'quantity': 720000}, {'name': 'Pyerite', 'quantity': 168000},
         {'name': 'Mexallon', 'quantity': 39200}, {'name': 'Isogen', 'quantity': 9200}
     ]},
    {'id': 821, 'name': 'Capital Capacitor Battery I Blueprint', 'category': 'capital_modules', 'group': 'Capacitor',
     'volume': 4000, 'base_cost': 680000, 'build_time': 9200, 'materials': [
         {'name': 'Tritanium', 'quantity': 680000}, {'name': 'Pyerite', 'quantity': 159000},
         {'name': 'Mexallon', 'quantity': 37000}, {'name': 'Isogen', 'quantity': 8700}
     ]},
    {'id': 822, 'name': 'Capital Capacitor Emitter I Blueprint', 'category': 'capital_modules', 'group': 'Capacitor',
     'volume': 4000, 'base_cost': 650000, 'build_time': 8800, 'materials': [
         {'name': 'Tritanium', 'quantity': 650000}, {'name': 'Pyerite', 'quantity': 152000},
         {'name': 'Mexallon', 'quantity': 35400}, {'name': 'Isogen', 'quantity': 8300}
     ]},
    
    # Weapons
    {'id': 830, 'name': 'Capital Neutron Blaster Cannon I Blueprint', 'category': 'capital_modules', 'group': 'Weapons',
     'volume': 4000, 'base_cost': 1250000, 'build_time': 18000, 'materials': [
         {'name': 'Tritanium', 'quantity': 1250000}, {'name': 'Pyerite', 'quantity': 292000},
         {'name': 'Mexallon', 'quantity': 68000}, {'name': 'Isogen', 'quantity': 16000},
         {'name': 'Nocxium', 'quantity': 3200}, {'name': 'Zydrine', 'quantity': 800}
     ]},
    {'id': 831, 'name': 'Capital Ion Siege Blaster I Blueprint', 'category': 'capital_modules', 'group': 'Weapons',
     'volume': 4000, 'base_cost': 1350000, 'build_time': 19500, 'materials': [
         {'name': 'Tritanium', 'quantity': 1350000}, {'name': 'Pyerite', 'quantity': 315000},
         {'name': 'Mexallon', 'quantity': 73500}, {'name': 'Isogen', 'quantity': 17200},
         {'name': 'Nocxium', 'quantity': 3440}, {'name': 'Zydrine', 'quantity': 860}
     ]},
    {'id': 832, 'name': 'Capital Quad 3500mm Siege Artillery I Blueprint', 'category': 'capital_modules', 'group': 'Weapons',
     'volume': 4000, 'base_cost': 1380000, 'build_time': 20000, 'materials': [
         {'name': 'Tritanium', 'quantity': 1380000}, {'name': 'Pyerite', 'quantity': 322000},
         {'name': 'Mexallon', 'quantity': 75200}, {'name': 'Isogen', 'quantity': 17600},
         {'name': 'Nocxium', 'quantity': 3520}, {'name': 'Zydrine', 'quantity': 880}
     ]},
    {'id': 833, 'name': 'Capital Dual 425mm AutoCannon I Blueprint', 'category': 'capital_modules', 'group': 'Weapons',
     'volume': 4000, 'base_cost': 1320000, 'build_time': 19200, 'materials': [
         {'name': 'Tritanium', 'quantity': 1320000}, {'name': 'Pyerite', 'quantity': 308000},
         {'name': 'Mexallon', 'quantity': 72000}, {'name': 'Isogen', 'quantity': 16900},
         {'name': 'Nocxium', 'quantity': 3380}, {'name': 'Zydrine', 'quantity': 845}
     ]},
    {'id': 834, 'name': 'Capital Tachyon Beam Laser I Blueprint', 'category': 'capital_modules', 'group': 'Weapons',
     'volume': 4000, 'base_cost': 1400000, 'build_time': 20500, 'materials': [
         {'name': 'Tritanium', 'quantity': 1400000}, {'name': 'Pyerite', 'quantity': 327000},
         {'name': 'Mexallon', 'quantity': 76300}, {'name': 'Isogen', 'quantity': 17900},
         {'name': 'Nocxium', 'quantity': 3580}, {'name': 'Zydrine', 'quantity': 895}
     ]},
    
    # Doomsday Weapons (Titans only)
    {'id': 840, 'name': 'Gjallarhorn Blueprint', 'category': 'capital_modules', 'group': 'Doomsday',
     'volume': 8000, 'base_cost': 8500000, 'build_time': 86400, 'materials': [
         {'name': 'Tritanium', 'quantity': 8500000}, {'name': 'Pyerite', 'quantity': 1985000},
         {'name': 'Mexallon', 'quantity': 463000}, {'name': 'Isogen', 'quantity': 108500},
         {'name': 'Nocxium', 'quantity': 21700}, {'name': 'Zydrine', 'quantity': 5425},
         {'name': 'Megacyte', 'quantity': 1356}, {'name': 'Morphite', 'quantity': 271}
     ]},
    {'id': 841, 'name': 'Oblivion Blueprint', 'category': 'capital_modules', 'group': 'Doomsday',
     'volume': 8000, 'base_cost': 8800000, 'build_time': 90000, 'materials': [
         {'name': 'Tritanium', 'quantity': 8800000}, {'name': 'Pyerite', 'quantity': 2055000},
         {'name': 'Mexallon', 'quantity': 479500}, {'name': 'Isogen', 'quantity': 112300},
         {'name': 'Nocxium', 'quantity': 22460}, {'name': 'Zydrine', 'quantity': 5615},
         {'name': 'Megacyte', 'quantity': 1404}, {'name': 'Morphite', 'quantity': 281}
     ]},
    {'id': 842, 'name': 'Aurora Ominae Blueprint', 'category': 'capital_modules', 'group': 'Doomsday',
     'volume': 8000, 'base_cost': 8600000, 'build_time': 87500, 'materials': [
         {'name': 'Tritanium', 'quantity': 8600000}, {'name': 'Pyerite', 'quantity': 2008000},
         {'name': 'Mexallon', 'quantity': 468500}, {'name': 'Isogen', 'quantity': 109800},
         {'name': 'Nocxium', 'quantity': 21960}, {'name': 'Zydrine', 'quantity': 5490},
         {'name': 'Megacyte', 'quantity': 1373}, {'name': 'Morphite', 'quantity': 275}
     ]},
    
    # Siege/Triage Modules
    {'id': 850, 'name': 'Siege Module I Blueprint', 'category': 'capital_modules', 'group': 'Siege',
     'volume': 4000, 'base_cost': 2100000, 'build_time': 28000, 'materials': [
         {'name': 'Tritanium', 'quantity': 2100000}, {'name': 'Pyerite', 'quantity': 490000},
         {'name': 'Mexallon', 'quantity': 114300}, {'name': 'Isogen', 'quantity': 26800},
         {'name': 'Nocxium', 'quantity': 5360}, {'name': 'Zydrine', 'quantity': 1340},
         {'name': 'Megacyte', 'quantity': 335}
     ]},
    {'id': 851, 'name': 'Triage Module I Blueprint', 'category': 'capital_modules', 'group': 'Siege',
     'volume': 4000, 'base_cost': 1950000, 'build_time': 26000, 'materials': [
         {'name': 'Tritanium', 'quantity': 1950000}, {'name': 'Pyerite', 'quantity': 455000},
         {'name': 'Mexallon', 'quantity': 106100}, {'name': 'Isogen', 'quantity': 24900},
         {'name': 'Nocxium', 'quantity': 4980}, {'name': 'Zydrine', 'quantity': 1245},
         {'name': 'Megacyte', 'quantity': 311}
     ]},
    {'id': 852, 'name': 'Industrial Core I Blueprint', 'category': 'capital_modules', 'group': 'Siege',
     'volume': 4000, 'base_cost': 1800000, 'build_time': 24000, 'materials': [
         {'name': 'Tritanium', 'quantity': 1800000}, {'name': 'Pyerite', 'quantity': 420000},
         {'name': 'Mexallon', 'quantity': 98000}, {'name': 'Isogen', 'quantity': 23000},
         {'name': 'Nocxium', 'quantity': 4600}, {'name': 'Zydrine', 'quantity': 1150},
         {'name': 'Megacyte', 'quantity': 288}
     ]},
    
    # Jump Portal/Bridge
    {'id': 860, 'name': 'Jump Portal Generator I Blueprint', 'category': 'capital_modules', 'group': 'Navigation',
     'volume': 4000, 'base_cost': 3200000, 'build_time': 42000, 'materials': [
         {'name': 'Tritanium', 'quantity': 3200000}, {'name': 'Pyerite', 'quantity': 747000},
         {'name': 'Mexallon', 'quantity': 174200}, {'name': 'Isogen', 'quantity': 40800},
         {'name': 'Nocxium', 'quantity': 8160}, {'name': 'Zydrine', 'quantity': 2040},
         {'name': 'Megacyte', 'quantity': 510}
     ]},
    {'id': 861, 'name': 'Capital Micro Jump Drive Blueprint', 'category': 'capital_modules', 'group': 'Navigation',
     'volume': 4000, 'base_cost': 2800000, 'build_time': 38000, 'materials': [
         {'name': 'Tritanium', 'quantity': 2800000}, {'name': 'Pyerite', 'quantity': 654000},
         {'name': 'Mexallon', 'quantity': 152600}, {'name': 'Isogen', 'quantity': 35700},
         {'name': 'Nocxium', 'quantity': 7140}, {'name': 'Zydrine', 'quantity': 1785},
         {'name': 'Megacyte', 'quantity': 446}
     ]},
    
    # Fighter-related
    {'id': 870, 'name': 'Fighter Support Unit I Blueprint', 'category': 'capital_modules', 'group': 'Fighters',
     'volume': 4000, 'base_cost': 950000, 'build_time': 13500, 'materials': [
         {'name': 'Tritanium', 'quantity': 950000}, {'name': 'Pyerite', 'quantity': 222000},
         {'name': 'Mexallon', 'quantity': 51800}, {'name': 'Isogen', 'quantity': 12100},
         {'name': 'Nocxium', 'quantity': 2420}, {'name': 'Zydrine', 'quantity': 605}
     ]},
    {'id': 871, 'name': 'Capital Drone Bay Blueprint', 'category': 'capital_modules', 'group': 'Fighters',
     'volume': 4000, 'base_cost': 680000, 'build_time': 9200, 'materials': [
         {'name': 'Tritanium', 'quantity': 680000}, {'name': 'Pyerite', 'quantity': 159000},
         {'name': 'Mexallon', 'quantity': 37000}, {'name': 'Isogen', 'quantity': 8700}
     ]},
    
    # Structure Modules
    {'id': 900, 'name': 'Standup Ballistic Control System I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 850000, 'build_time': 12000, 'materials': [
         {'name': 'Tritanium', 'quantity': 850000}, {'name': 'Pyerite', 'quantity': 198000},
         {'name': 'Mexallon', 'quantity': 46200}, {'name': 'Isogen', 'quantity': 10800}
     ]},
    {'id': 901, 'name': 'Standup Missile Guidance Computer I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 780000, 'build_time': 10800, 'materials': [
         {'name': 'Tritanium', 'quantity': 780000}, {'name': 'Pyerite', 'quantity': 182000},
         {'name': 'Mexallon', 'quantity': 42500}, {'name': 'Isogen', 'quantity': 9900}
     ]},
    {'id': 902, 'name': 'Standup Point Defense Battery I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1250000, 'build_time': 18000, 'materials': [
         {'name': 'Tritanium', 'quantity': 1250000}, {'name': 'Pyerite', 'quantity': 292000},
         {'name': 'Mexallon', 'quantity': 68000}, {'name': 'Isogen', 'quantity': 15900},
         {'name': 'Nocxium', 'quantity': 3180}, {'name': 'Zydrine', 'quantity': 795}
     ]},
    {'id': 903, 'name': 'Standup Anticapital Missile Launcher I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1400000, 'build_time': 20000, 'materials': [
         {'name': 'Tritanium', 'quantity': 1400000}, {'name': 'Pyerite', 'quantity': 327000},
         {'name': 'Mexallon', 'quantity': 76300}, {'name': 'Isogen', 'quantity': 17900},
         {'name': 'Nocxium', 'quantity': 3580}, {'name': 'Zydrine', 'quantity': 895}
     ]},
    {'id': 904, 'name': 'Standup Guided Bomb Launcher I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1650000, 'build_time': 23500, 'materials': [
         {'name': 'Tritanium', 'quantity': 1650000}, {'name': 'Pyerite', 'quantity': 385000},
         {'name': 'Mexallon', 'quantity': 89800}, {'name': 'Isogen', 'quantity': 21000},
         {'name': 'Nocxium', 'quantity': 4200}, {'name': 'Zydrine', 'quantity': 1050},
         {'name': 'Megacyte', 'quantity': 263}
     ]},
    {'id': 905, 'name': 'Standup Energy Neutralizer I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 920000, 'build_time': 13200, 'materials': [
         {'name': 'Tritanium', 'quantity': 920000}, {'name': 'Pyerite', 'quantity': 215000},
         {'name': 'Mexallon', 'quantity': 50200}, {'name': 'Isogen', 'quantity': 11700},
         {'name': 'Nocxium', 'quantity': 2340}, {'name': 'Zydrine', 'quantity': 585}
     ]},
    {'id': 906, 'name': 'Standup ECM Jammer I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 880000, 'build_time': 12500, 'materials': [
         {'name': 'Tritanium', 'quantity': 880000}, {'name': 'Pyerite', 'quantity': 205000},
         {'name': 'Mexallon', 'quantity': 47900}, {'name': 'Isogen', 'quantity': 11200},
         {'name': 'Nocxium', 'quantity': 2240}, {'name': 'Zydrine', 'quantity': 560}
     ]},
    {'id': 907, 'name': 'Standup Stasis Webifier I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 750000, 'build_time': 10500, 'materials': [
         {'name': 'Tritanium', 'quantity': 750000}, {'name': 'Pyerite', 'quantity': 175000},
         {'name': 'Mexallon', 'quantity': 40800}, {'name': 'Isogen', 'quantity': 9500}
     ]},
    {'id': 908, 'name': 'Standup Warp Scrambler I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 700000, 'build_time': 9800, 'materials': [
         {'name': 'Tritanium', 'quantity': 700000}, {'name': 'Pyerite', 'quantity': 163000},
         {'name': 'Mexallon', 'quantity': 38100}, {'name': 'Isogen', 'quantity': 8900}
     ]},
    {'id': 909, 'name': 'Standup Target Painter I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 680000, 'build_time': 9500, 'materials': [
         {'name': 'Tritanium', 'quantity': 680000}, {'name': 'Pyerite', 'quantity': 159000},
         {'name': 'Mexallon', 'quantity': 37000}, {'name': 'Isogen', 'quantity': 8600}
     ]},
    {'id': 910, 'name': 'Standup Remote Sensor Dampener I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 720000, 'build_time': 10200, 'materials': [
         {'name': 'Tritanium', 'quantity': 720000}, {'name': 'Pyerite', 'quantity': 168000},
         {'name': 'Mexallon', 'quantity': 39200}, {'name': 'Isogen', 'quantity': 9200}
     ]},
    {'id': 911, 'name': 'Standup Weapon Disruptor I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 760000, 'build_time': 10800, 'materials': [
         {'name': 'Tritanium', 'quantity': 760000}, {'name': 'Pyerite', 'quantity': 177000},
         {'name': 'Mexallon', 'quantity': 41400}, {'name': 'Isogen', 'quantity': 9700}
     ]},
    {'id': 912, 'name': 'Standup Co-Processor Array I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1450000, 'build_time': 20500, 'materials': [
         {'name': 'Tritanium', 'quantity': 1450000}, {'name': 'Pyerite', 'quantity': 338000},
         {'name': 'Mexallon', 'quantity': 78900}, {'name': 'Isogen', 'quantity': 18500},
         {'name': 'Nocxium', 'quantity': 3700}, {'name': 'Zydrine', 'quantity': 925}
     ]},
    {'id': 913, 'name': 'Standup Reprocessing Facility I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1680000, 'build_time': 24000, 'materials': [
         {'name': 'Tritanium', 'quantity': 1680000}, {'name': 'Pyerite', 'quantity': 392000},
         {'name': 'Mexallon', 'quantity': 91500}, {'name': 'Isogen', 'quantity': 21400},
         {'name': 'Nocxium', 'quantity': 4280}, {'name': 'Zydrine', 'quantity': 1070},
         {'name': 'Megacyte', 'quantity': 268}
     ]},
    {'id': 914, 'name': 'Standup Manufacturing Plant I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1850000, 'build_time': 26500, 'materials': [
         {'name': 'Tritanium', 'quantity': 1850000}, {'name': 'Pyerite', 'quantity': 432000},
         {'name': 'Mexallon', 'quantity': 100800}, {'name': 'Isogen', 'quantity': 23600},
         {'name': 'Nocxium', 'quantity': 4720}, {'name': 'Zydrine', 'quantity': 1180},
         {'name': 'Megacyte', 'quantity': 295}
     ]},
    {'id': 915, 'name': 'Standup Research Lab I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1720000, 'build_time': 24500, 'materials': [
         {'name': 'Tritanium', 'quantity': 1720000}, {'name': 'Pyerite', 'quantity': 401000},
         {'name': 'Mexallon', 'quantity': 93600}, {'name': 'Isogen', 'quantity': 21900},
         {'name': 'Nocxium', 'quantity': 4380}, {'name': 'Zydrine', 'quantity': 1095},
         {'name': 'Megacyte', 'quantity': 274}
     ]},
    {'id': 916, 'name': 'Standup Market Hub I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 2400000, 'build_time': 34000, 'materials': [
         {'name': 'Tritanium', 'quantity': 2400000}, {'name': 'Pyerite', 'quantity': 560000},
         {'name': 'Mexallon', 'quantity': 130600}, {'name': 'Isogen', 'quantity': 30600},
         {'name': 'Nocxium', 'quantity': 6120}, {'name': 'Zydrine', 'quantity': 1530},
         {'name': 'Megacyte', 'quantity': 383}
     ]},
    {'id': 917, 'name': 'Standup Cloning Center I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1580000, 'build_time': 22500, 'materials': [
         {'name': 'Tritanium', 'quantity': 1580000}, {'name': 'Pyerite', 'quantity': 368000},
         {'name': 'Mexallon', 'quantity': 85900}, {'name': 'Isogen', 'quantity': 20100},
         {'name': 'Nocxium', 'quantity': 4020}, {'name': 'Zydrine', 'quantity': 1005},
         {'name': 'Megacyte', 'quantity': 251}
     ]},
    {'id': 918, 'name': 'Standup Cynosural System I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 2200000, 'build_time': 31000, 'materials': [
         {'name': 'Tritanium', 'quantity': 2200000}, {'name': 'Pyerite', 'quantity': 513000},
         {'name': 'Mexallon', 'quantity': 119700}, {'name': 'Isogen', 'quantity': 28000},
         {'name': 'Nocxium', 'quantity': 5600}, {'name': 'Zydrine', 'quantity': 1400},
         {'name': 'Megacyte', 'quantity': 350}
     ]},
    {'id': 919, 'name': 'Standup Moon Drill I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 2800000, 'build_time': 39500, 'materials': [
         {'name': 'Tritanium', 'quantity': 2800000}, {'name': 'Pyerite', 'quantity': 654000},
         {'name': 'Mexallon', 'quantity': 152600}, {'name': 'Isogen', 'quantity': 35700},
         {'name': 'Nocxium', 'quantity': 7140}, {'name': 'Zydrine', 'quantity': 1785},
         {'name': 'Megacyte', 'quantity': 446}
     ]},
    {'id': 920, 'name': 'Standup Reactor Array I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1950000, 'build_time': 27500, 'materials': [
         {'name': 'Tritanium', 'quantity': 1950000}, {'name': 'Pyerite', 'quantity': 455000},
         {'name': 'Mexallon', 'quantity': 106100}, {'name': 'Isogen', 'quantity': 24900},
         {'name': 'Nocxium', 'quantity': 4980}, {'name': 'Zydrine', 'quantity': 1245},
         {'name': 'Megacyte', 'quantity': 311}
     ]},
    {'id': 921, 'name': 'Standup Drone Bay I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1350000, 'build_time': 19000, 'materials': [
         {'name': 'Tritanium', 'quantity': 1350000}, {'name': 'Pyerite', 'quantity': 315000},
         {'name': 'Mexallon', 'quantity': 73500}, {'name': 'Isogen', 'quantity': 17200},
         {'name': 'Nocxium', 'quantity': 3440}, {'name': 'Zydrine', 'quantity': 860}
     ]},
    {'id': 922, 'name': 'Standup Fighter Bay I Blueprint', 'category': 'structure_modules', 'group': 'Structure',
     'volume': 5000, 'base_cost': 1680000, 'build_time': 23800, 'materials': [
         {'name': 'Tritanium', 'quantity': 1680000}, {'name': 'Pyerite', 'quantity': 392000},
         {'name': 'Mexallon', 'quantity': 91500}, {'name': 'Isogen', 'quantity': 21400},
         {'name': 'Nocxium', 'quantity': 4280}, {'name': 'Zydrine', 'quantity': 1070},
         {'name': 'Megacyte', 'quantity': 268}
     ]},
]

# Combine all databases for import
ALL_CAPITAL_DATABASE = CAPITAL_DATABASE + CAPITAL_MODULES + STRUCTURE_DATABASE

print(f"Capital database loaded: {len(CAPITAL_DATABASE)} capital ships")
print(f"Capital modules loaded: {len(CAPITAL_MODULES)} modules")
print(f"Structure database loaded: {len(STRUCTURE_DATABASE)} structures")
print(f"Total capital/structure blueprints: {len(ALL_CAPITAL_DATABASE)}")
