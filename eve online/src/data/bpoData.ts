export interface Material {
  name: string;
  quantity: number;
}

export interface BPOEntry {
  id: number;
  name: string;
  category: string;
  type_id: number;
  image_url: string;
  base_cost: number;
  build_time: number;
  volume: number;
  materials: Material[];
}

export const BPO_DATABASE: BPOEntry[] = [
  // T1 Ships
  {
    id: 1,
    name: 'Iteron Mark V Blueprint',
    category: 't1_ships',
    type_id: 12743,
    image_url: 'https://images.evetech.net/types/650/render?size=128',
    base_cost: 25000000,
    build_time: 72000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 450000 },
      { name: 'Pyerite', quantity: 150000 },
      { name: 'Mexallon', quantity: 35000 },
      { name: 'Isogen', quantity: 8000 },
      { name: 'Nocxium', quantity: 1200 },
      { name: 'Zydrine', quantity: 400 }
    ]
  },
  {
    id: 2,
    name: 'Badger Blueprint',
    category: 't1_ships',
    type_id: 12741,
    image_url: 'https://images.evetech.net/types/648/render?size=128',
    base_cost: 15000000,
    build_time: 54000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 280000 },
      { name: 'Pyerite', quantity: 95000 },
      { name: 'Mexallon', quantity: 22000 },
      { name: 'Isogen', quantity: 5000 },
      { name: 'Nocxium', quantity: 800 },
      { name: 'Zydrine', quantity: 250 }
    ]
  },
  {
    id: 3,
    name: 'Tayra Blueprint',
    category: 't1_ships',
    type_id: 12745,
    image_url: 'https://images.evetech.net/types/649/render?size=128',
    base_cost: 20000000,
    build_time: 60000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 380000 },
      { name: 'Pyerite', quantity: 125000 },
      { name: 'Mexallon', quantity: 30000 },
      { name: 'Isogen', quantity: 7000 },
      { name: 'Nocxium', quantity: 1000 },
      { name: 'Zydrine', quantity: 350 }
    ]
  },
  {
    id: 4,
    name: 'Bestower Blueprint',
    category: 't1_ships',
    type_id: 12739,
    image_url: 'https://images.evetech.net/types/651/render?size=128',
    base_cost: 18000000,
    build_time: 58000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 320000 },
      { name: 'Pyerite', quantity: 110000 },
      { name: 'Mexallon', quantity: 26000 },
      { name: 'Isogen', quantity: 6000 },
      { name: 'Nocxium', quantity: 900 },
      { name: 'Zydrine', quantity: 300 }
    ]
  },
  {
    id: 5,
    name: 'Catalyst Blueprint',
    category: 't1_ships',
    type_id: 12737,
    image_url: 'https://images.evetech.net/types/32811/render?size=128',
    base_cost: 12000000,
    build_time: 42000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 180000 },
      { name: 'Pyerite', quantity: 60000 },
      { name: 'Mexallon', quantity: 15000 },
      { name: 'Isogen', quantity: 3500 },
      { name: 'Nocxium', quantity: 500 },
      { name: 'Zydrine', quantity: 180 }
    ]
  },
  {
    id: 6,
    name: 'Thrasher Blueprint',
    category: 't1_ships',
    type_id: 12738,
    image_url: 'https://images.evetech.net/types/32810/render?size=128',
    base_cost: 12000000,
    build_time: 42000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 180000 },
      { name: 'Pyerite', quantity: 60000 },
      { name: 'Mexallon', quantity: 15000 },
      { name: 'Isogen', quantity: 3500 },
      { name: 'Nocxium', quantity: 500 },
      { name: 'Zydrine', quantity: 180 }
    ]
  },
  {
    id: 7,
    name: 'Cormorant Blueprint',
    category: 't1_ships',
    type_id: 12736,
    image_url: 'https://images.evetech.net/types/32812/render?size=128',
    base_cost: 12000000,
    build_time: 42000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 180000 },
      { name: 'Pyerite', quantity: 60000 },
      { name: 'Mexallon', quantity: 15000 },
      { name: 'Isogen', quantity: 3500 },
      { name: 'Nocxium', quantity: 500 },
      { name: 'Zydrine', quantity: 180 }
    ]
  },
  {
    id: 8,
    name: 'Coercer Blueprint',
    category: 't1_ships',
    type_id: 12735,
    image_url: 'https://images.evetech.net/types/32809/render?size=128',
    base_cost: 12000000,
    build_time: 42000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 180000 },
      { name: 'Pyerite', quantity: 60000 },
      { name: 'Mexallon', quantity: 15000 },
      { name: 'Isogen', quantity: 3500 },
      { name: 'Nocxium', quantity: 500 },
      { name: 'Zydrine', quantity: 180 }
    ]
  },
  {
    id: 9,
    name: 'Executioner Blueprint',
    category: 't1_ships',
    type_id: 12732,
    image_url: 'https://images.evetech.net/types/591/render?size=128',
    base_cost: 8000000,
    build_time: 30000,
    volume: 2500,
    materials: [
      { name: 'Tritanium', quantity: 25000 },
      { name: 'Pyerite', quantity: 8500 },
      { name: 'Mexallon', quantity: 2200 },
      { name: 'Isogen', quantity: 500 },
      { name: 'Nocxium', quantity: 75 },
      { name: 'Zydrine', quantity: 25 }
    ]
  },
  {
    id: 10,
    name: 'Atron Blueprint',
    category: 't1_ships',
    type_id: 12730,
    image_url: 'https://images.evetech.net/types/589/render?size=128',
    base_cost: 8000000,
    build_time: 30000,
    volume: 2500,
    materials: [
      { name: 'Tritanium', quantity: 25000 },
      { name: 'Pyerite', quantity: 8500 },
      { name: 'Mexallon', quantity: 2200 },
      { name: 'Isogen', quantity: 500 },
      { name: 'Nocxium', quantity: 75 },
      { name: 'Zydrine', quantity: 25 }
    ]
  },
  {
    id: 11,
    name: 'Condor Blueprint',
    category: 't1_ships',
    type_id: 12731,
    image_url: 'https://images.evetech.net/types/587/render?size=128',
    base_cost: 8000000,
    build_time: 30000,
    volume: 2500,
    materials: [
      { name: 'Tritanium', quantity: 25000 },
      { name: 'Pyerite', quantity: 8500 },
      { name: 'Mexallon', quantity: 2200 },
      { name: 'Isogen', quantity: 500 },
      { name: 'Nocxium', quantity: 75 },
      { name: 'Zydrine', quantity: 25 }
    ]
  },
  {
    id: 12,
    name: 'Slasher Blueprint',
    category: 't1_ships',
    type_id: 12733,
    image_url: 'https://images.evetech.net/types/585/render?size=128',
    base_cost: 8000000,
    build_time: 30000,
    volume: 2500,
    materials: [
      { name: 'Tritanium', quantity: 25000 },
      { name: 'Pyerite', quantity: 8500 },
      { name: 'Mexallon', quantity: 2200 },
      { name: 'Isogen', quantity: 500 },
      { name: 'Nocxium', quantity: 75 },
      { name: 'Zydrine', quantity: 25 }
    ]
  },
  {
    id: 13,
    name: 'Vexor Blueprint',
    category: 't1_ships',
    type_id: 12747,
    image_url: 'https://images.evetech.net/types/626/render?size=128',
    base_cost: 35000000,
    build_time: 72000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 550000 },
      { name: 'Pyerite', quantity: 185000 },
      { name: 'Mexallon', quantity: 45000 },
      { name: 'Isogen', quantity: 11000 },
      { name: 'Nocxium', quantity: 1600 },
      { name: 'Zydrine', quantity: 500 },
      { name: 'Megacyte', quantity: 100 }
    ]
  },
  {
    id: 14,
    name: 'Thorax Blueprint',
    category: 't1_ships',
    type_id: 12748,
    image_url: 'https://images.evetech.net/types/624/render?size=128',
    base_cost: 35000000,
    build_time: 72000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 550000 },
      { name: 'Pyerite', quantity: 185000 },
      { name: 'Mexallon', quantity: 45000 },
      { name: 'Isogen', quantity: 11000 },
      { name: 'Nocxium', quantity: 1600 },
      { name: 'Zydrine', quantity: 500 },
      { name: 'Megacyte', quantity: 100 }
    ]
  },
  {
    id: 15,
    name: 'Moa Blueprint',
    category: 't1_ships',
    type_id: 12749,
    image_url: 'https://images.evetech.net/types/622/render?size=128',
    base_cost: 35000000,
    build_time: 72000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 550000 },
      { name: 'Pyerite', quantity: 185000 },
      { name: 'Mexallon', quantity: 45000 },
      { name: 'Isogen', quantity: 11000 },
      { name: 'Nocxium', quantity: 1600 },
      { name: 'Zydrine', quantity: 500 },
      { name: 'Megacyte', quantity: 100 }
    ]
  },
  {
    id: 16,
    name: 'Omen Blueprint',
    category: 't1_ships',
    type_id: 12750,
    image_url: 'https://images.evetech.net/types/620/render?size=128',
    base_cost: 35000000,
    build_time: 72000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 550000 },
      { name: 'Pyerite', quantity: 185000 },
      { name: 'Mexallon', quantity: 45000 },
      { name: 'Isogen', quantity: 11000 },
      { name: 'Nocxium', quantity: 1600 },
      { name: 'Zydrine', quantity: 500 },
      { name: 'Megacyte', quantity: 100 }
    ]
  },
  {
    id: 17,
    name: 'Drake Blueprint',
    category: 't1_ships',
    type_id: 12761,
    image_url: 'https://images.evetech.net/types/24698/render?size=128',
    base_cost: 95000000,
    build_time: 144000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 1200000 },
      { name: 'Pyerite', quantity: 400000 },
      { name: 'Mexallon', quantity: 100000 },
      { name: 'Isogen', quantity: 25000 },
      { name: 'Nocxium', quantity: 4000 },
      { name: 'Zydrine', quantity: 1200 },
      { name: 'Megacyte', quantity: 250 }
    ]
  },
  {
    id: 18,
    name: 'Hurricane Blueprint',
    category: 't1_ships',
    type_id: 12762,
    image_url: 'https://images.evetech.net/types/24702/render?size=128',
    base_cost: 95000000,
    build_time: 144000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 1200000 },
      { name: 'Pyerite', quantity: 400000 },
      { name: 'Mexallon', quantity: 100000 },
      { name: 'Isogen', quantity: 25000 },
      { name: 'Nocxium', quantity: 4000 },
      { name: 'Zydrine', quantity: 1200 },
      { name: 'Megacyte', quantity: 250 }
    ]
  },
  {
    id: 19,
    name: 'Brutix Blueprint',
    category: 't1_ships',
    type_id: 12763,
    image_url: 'https://images.evetech.net/types/24694/render?size=128',
    base_cost: 95000000,
    build_time: 144000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 1200000 },
      { name: 'Pyerite', quantity: 400000 },
      { name: 'Mexallon', quantity: 100000 },
      { name: 'Isogen', quantity: 25000 },
      { name: 'Nocxium', quantity: 4000 },
      { name: 'Zydrine', quantity: 1200 },
      { name: 'Megacyte', quantity: 250 }
    ]
  },
  {
    id: 20,
    name: 'Harbinger Blueprint',
    category: 't1_ships',
    type_id: 12764,
    image_url: 'https://images.evetech.net/types/24696/render?size=128',
    base_cost: 95000000,
    build_time: 144000,
    volume: 15000,
    materials: [
      { name: 'Tritanium', quantity: 1200000 },
      { name: 'Pyerite', quantity: 400000 },
      { name: 'Mexallon', quantity: 100000 },
      { name: 'Isogen', quantity: 25000 },
      { name: 'Nocxium', quantity: 4000 },
      { name: 'Zydrine', quantity: 1200 },
      { name: 'Megacyte', quantity: 250 }
    ]
  },
  
  // T1 Modules
  {
    id: 100,
    name: '10MN Afterburner I Blueprint',
    category: 't1_modules',
    type_id: 12785,
    image_url: 'https://images.evetech.net/types/12058/icon?size=64',
    base_cost: 15000,
    build_time: 3000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 15000 },
      { name: 'Pyerite', quantity: 3500 },
      { name: 'Mexallon', quantity: 800 },
      { name: 'Isogen', quantity: 200 },
      { name: 'Nocxium', quantity: 40 },
      { name: 'Construction Blocks', quantity: 5 }
    ]
  },
  {
    id: 101,
    name: '10MN Monopropellant Enduring Afterburner Blueprint',
    category: 't1_modules',
    type_id: 24313,
    image_url: 'https://images.evetech.net/types/24313/icon?size=64',
    base_cost: 25000,
    build_time: 4000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 18000 },
      { name: 'Pyerite', quantity: 4200 },
      { name: 'Mexallon', quantity: 950 },
      { name: 'Isogen', quantity: 240 },
      { name: 'Nocxium', quantity: 48 },
      { name: 'Construction Blocks', quantity: 6 }
    ]
  },
  {
    id: 102,
    name: '50MN Microwarpdrive I Blueprint',
    category: 't1_modules',
    type_id: 12786,
    image_url: 'https://images.evetech.net/types/12076/icon?size=64',
    base_cost: 30000,
    build_time: 5000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 25000 },
      { name: 'Pyerite', quantity: 6000 },
      { name: 'Mexallon', quantity: 1400 },
      { name: 'Isogen', quantity: 350 },
      { name: 'Nocxium', quantity: 70 },
      { name: 'Construction Blocks', quantity: 8 }
    ]
  },
  {
    id: 103,
    name: '50MN Quad LiF Restrained Microwarpdrive Blueprint',
    category: 't1_modules',
    type_id: 24315,
    image_url: 'https://images.evetech.net/types/24315/icon?size=64',
    base_cost: 45000,
    build_time: 6000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 30000 },
      { name: 'Pyerite', quantity: 7200 },
      { name: 'Mexallon', quantity: 1680 },
      { name: 'Isogen', quantity: 420 },
      { name: 'Nocxium', quantity: 84 },
      { name: 'Construction Blocks', quantity: 10 }
    ]
  },
  {
    id: 104,
    name: 'Adaptive Invulnerability Field I Blueprint',
    category: 't1_modules',
    type_id: 12787,
    image_url: 'https://images.evetech.net/types/962/icon?size=64',
    base_cost: 25000,
    build_time: 4000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 18000 },
      { name: 'Pyerite', quantity: 4200 },
      { name: 'Mexallon', quantity: 950 },
      { name: 'Isogen', quantity: 240 },
      { name: 'Nocxium', quantity: 48 },
      { name: 'Construction Blocks', quantity: 6 }
    ]
  },
  {
    id: 105,
    name: 'Adaptive Invulnerability Field II Blueprint',
    category: 't2_modules',
    type_id: 12823,
    image_url: 'https://images.evetech.net/types/2281/icon?size=64',
    base_cost: 180000,
    build_time: 12000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 75000 },
      { name: 'Pyerite', quantity: 18000 },
      { name: 'Mexallon', quantity: 4000 },
      { name: 'Isogen', quantity: 1000 },
      { name: 'Nocxium', quantity: 200 },
      { name: 'Zydrine', quantity: 50 },
      { name: 'Megacyte', quantity: 10 },
      { name: 'Nanotransistors', quantity: 15 },
      { name: 'Superconductors', quantity: 8 }
    ]
  },
  {
    id: 106,
    name: 'EM Ward Field I Blueprint',
    category: 't1_modules',
    type_id: 12788,
    image_url: 'https://images.evetech.net/types/956/icon?size=64',
    base_cost: 15000,
    build_time: 3000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 12000 },
      { name: 'Pyerite', quantity: 2800 },
      { name: 'Mexallon', quantity: 650 },
      { name: 'Isogen', quantity: 160 },
      { name: 'Nocxium', quantity: 32 },
      { name: 'Construction Blocks', quantity: 4 }
    ]
  },
  {
    id: 107,
    name: 'EM Ward Field II Blueprint',
    category: 't2_modules',
    type_id: 12824,
    image_url: 'https://images.evetech.net/types/2281/icon?size=64',
    base_cost: 120000,
    build_time: 10000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 50000 },
      { name: 'Pyerite', quantity: 12000 },
      { name: 'Mexallon', quantity: 2800 },
      { name: 'Isogen', quantity: 700 },
      { name: 'Nocxium', quantity: 140 },
      { name: 'Zydrine', quantity: 35 },
      { name: 'Megacyte', quantity: 7 },
      { name: 'Nanotransistors', quantity: 10 },
      { name: 'Superconductors', quantity: 5 }
    ]
  },
  {
    id: 108,
    name: 'Thermal Dissipation Field I Blueprint',
    category: 't1_modules',
    type_id: 12789,
    image_url: 'https://images.evetech.net/types/955/icon?size=64',
    base_cost: 15000,
    build_time: 3000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 12000 },
      { name: 'Pyerite', quantity: 2800 },
      { name: 'Mexallon', quantity: 650 },
      { name: 'Isogen', quantity: 160 },
      { name: 'Nocxium', quantity: 32 },
      { name: 'Construction Blocks', quantity: 4 }
    ]
  },
  {
    id: 109,
    name: 'Thermal Dissipation Field II Blueprint',
    category: 't2_modules',
    type_id: 12825,
    image_url: 'https://images.evetech.net/types/2281/icon?size=64',
    base_cost: 120000,
    build_time: 10000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 50000 },
      { name: 'Pyerite', quantity: 12000 },
      { name: 'Mexallon', quantity: 2800 },
      { name: 'Isogen', quantity: 700 },
      { name: 'Nocxium', quantity: 140 },
      { name: 'Zydrine', quantity: 35 },
      { name: 'Megacyte', quantity: 7 },
      { name: 'Nanotransistors', quantity: 10 },
      { name: 'Superconductors', quantity: 5 }
    ]
  },
  {
    id: 110,
    name: 'Kinetic Deflection Field I Blueprint',
    category: 't1_modules',
    type_id: 12790,
    image_url: 'https://images.evetech.net/types/954/icon?size=64',
    base_cost: 15000,
    build_time: 3000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 12000 },
      { name: 'Pyerite', quantity: 2800 },
      { name: 'Mexallon', quantity: 650 },
      { name: 'Isogen', quantity: 160 },
      { name: 'Nocxium', quantity: 32 },
      { name: 'Construction Blocks', quantity: 4 }
    ]
  },
  {
    id: 111,
    name: 'Kinetic Deflection Field II Blueprint',
    category: 't2_modules',
    type_id: 12826,
    image_url: 'https://images.evetech.net/types/2281/icon?size=64',
    base_cost: 120000,
    build_time: 10000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 50000 },
      { name: 'Pyerite', quantity: 12000 },
      { name: 'Mexallon', quantity: 2800 },
      { name: 'Isogen', quantity: 700 },
      { name: 'Nocxium', quantity: 140 },
      { name: 'Zydrine', quantity: 35 },
      { name: 'Megacyte', quantity: 7 },
      { name: 'Nanotransistors', quantity: 10 },
      { name: 'Superconductors', quantity: 5 }
    ]
  },
  {
    id: 112,
    name: 'Explosive Deflection Field I Blueprint',
    category: 't1_modules',
    type_id: 12791,
    image_url: 'https://images.evetech.net/types/957/icon?size=64',
    base_cost: 15000,
    build_time: 3000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 12000 },
      { name: 'Pyerite', quantity: 2800 },
      { name: 'Mexallon', quantity: 650 },
      { name: 'Isogen', quantity: 160 },
      { name: 'Nocxium', quantity: 32 },
      { name: 'Construction Blocks', quantity: 4 }
    ]
  },
  {
    id: 113,
    name: 'Explosive Deflection Field II Blueprint',
    category: 't2_modules',
    type_id: 12827,
    image_url: 'https://images.evetech.net/types/2281/icon?size=64',
    base_cost: 120000,
    build_time: 10000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 50000 },
      { name: 'Pyerite', quantity: 12000 },
      { name: 'Mexallon', quantity: 2800 },
      { name: 'Isogen', quantity: 700 },
      { name: 'Nocxium', quantity: 140 },
      { name: 'Zydrine', quantity: 35 },
      { name: 'Megacyte', quantity: 7 },
      { name: 'Nanotransistors', quantity: 10 },
      { name: 'Superconductors', quantity: 5 }
    ]
  },
  {
    id: 114,
    name: 'Large Shield Extender I Blueprint',
    category: 't1_modules',
    type_id: 12792,
    image_url: 'https://images.evetech.net/types/3841/icon?size=64',
    base_cost: 20000,
    build_time: 4000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 20000 },
      { name: 'Pyerite', quantity: 4800 },
      { name: 'Mexallon', quantity: 1100 },
      { name: 'Isogen', quantity: 280 },
      { name: 'Nocxium', quantity: 56 },
      { name: 'Construction Blocks', quantity: 7 }
    ]
  },
  {
    id: 115,
    name: 'Large Shield Extender II Blueprint',
    category: 't2_modules',
    type_id: 12828,
    image_url: 'https://images.evetech.net/types/3841/icon?size=64',
    base_cost: 150000,
    build_time: 12000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 65000 },
      { name: 'Pyerite', quantity: 15600 },
      { name: 'Mexallon', quantity: 3600 },
      { name: 'Isogen', quantity: 900 },
      { name: 'Nocxium', quantity: 180 },
      { name: 'Zydrine', quantity: 45 },
      { name: 'Megacyte', quantity: 9 },
      { name: 'Nanotransistors', quantity: 12 },
      { name: 'Superconductors', quantity: 6 }
    ]
  },
  {
    id: 116,
    name: 'Capacitor Recharger I Blueprint',
    category: 't1_modules',
    type_id: 12793,
    image_url: 'https://images.evetech.net/types/1182/icon?size=64',
    base_cost: 12000,
    build_time: 3000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 10000 },
      { name: 'Pyerite', quantity: 2400 },
      { name: 'Mexallon', quantity: 550 },
      { name: 'Isogen', quantity: 140 },
      { name: 'Nocxium', quantity: 28 },
      { name: 'Construction Blocks', quantity: 3 }
    ]
  },
  {
    id: 117,
    name: 'Capacitor Recharger II Blueprint',
    category: 't2_modules',
    type_id: 12829,
    image_url: 'https://images.evetech.net/types/1182/icon?size=64',
    base_cost: 95000,
    build_time: 9000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 42000 },
      { name: 'Pyerite', quantity: 10000 },
      { name: 'Mexallon', quantity: 2300 },
      { name: 'Isogen', quantity: 580 },
      { name: 'Nocxium', quantity: 116 },
      { name: 'Zydrine', quantity: 29 },
      { name: 'Megacyte', quantity: 6 },
      { name: 'Nanotransistors', quantity: 8 },
      { name: 'Superconductors', quantity: 4 }
    ]
  },
  {
    id: 118,
    name: 'Drone Damage Amplifier I Blueprint',
    category: 't1_modules',
    type_id: 12794,
    image_url: 'https://images.evetech.net/types/4393/icon?size=64',
    base_cost: 18000,
    build_time: 4500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 14000 },
      { name: 'Pyerite', quantity: 3300 },
      { name: 'Mexallon', quantity: 750 },
      { name: 'Isogen', quantity: 190 },
      { name: 'Nocxium', quantity: 38 },
      { name: 'Construction Blocks', quantity: 5 }
    ]
  },
  {
    id: 119,
    name: 'Drone Damage Amplifier II Blueprint',
    category: 't2_modules',
    type_id: 12830,
    image_url: 'https://images.evetech.net/types/4393/icon?size=64',
    base_cost: 140000,
    build_time: 11000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 58000 },
      { name: 'Pyerite', quantity: 13800 },
      { name: 'Mexallon', quantity: 3200 },
      { name: 'Isogen', quantity: 800 },
      { name: 'Nocxium', quantity: 160 },
      { name: 'Zydrine', quantity: 40 },
      { name: 'Megacyte', quantity: 8 },
      { name: 'Nanotransistors', quantity: 11 },
      { name: 'Sylramic Fibers', quantity: 6 }
    ]
  },
  {
    id: 120,
    name: 'Magnetic Field Stabilizer I Blueprint',
    category: 't1_modules',
    type_id: 12795,
    image_url: 'https://images.evetech.net/types/1163/icon?size=64',
    base_cost: 15000,
    build_time: 3500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 12000 },
      { name: 'Pyerite', quantity: 2800 },
      { name: 'Mexallon', quantity: 650 },
      { name: 'Isogen', quantity: 160 },
      { name: 'Nocxium', quantity: 32 },
      { name: 'Construction Blocks', quantity: 4 }
    ]
  },
  {
    id: 121,
    name: 'Magnetic Field Stabilizer II Blueprint',
    category: 't2_modules',
    type_id: 12831,
    image_url: 'https://images.evetech.net/types/1163/icon?size=64',
    base_cost: 110000,
    build_time: 9500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 48000 },
      { name: 'Pyerite', quantity: 11500 },
      { name: 'Mexallon', quantity: 2700 },
      { name: 'Isogen', quantity: 675 },
      { name: 'Nocxium', quantity: 135 },
      { name: 'Zydrine', quantity: 34 },
      { name: 'Megacyte', quantity: 7 },
      { name: 'Nanotransistors', quantity: 9 },
      { name: 'Sylramic Fibers', quantity: 5 }
    ]
  },
  {
    id: 122,
    name: 'Gyrostabilizer I Blueprint',
    category: 't1_modules',
    type_id: 12796,
    image_url: 'https://images.evetech.net/types/1162/icon?size=64',
    base_cost: 15000,
    build_time: 3500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 12000 },
      { name: 'Pyerite', quantity: 2800 },
      { name: 'Mexallon', quantity: 650 },
      { name: 'Isogen', quantity: 160 },
      { name: 'Nocxium', quantity: 32 },
      { name: 'Construction Blocks', quantity: 4 }
    ]
  },
  {
    id: 123,
    name: 'Gyrostabilizer II Blueprint',
    category: 't2_modules',
    type_id: 12832,
    image_url: 'https://images.evetech.net/types/1162/icon?size=64',
    base_cost: 110000,
    build_time: 9500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 48000 },
      { name: 'Pyerite', quantity: 11500 },
      { name: 'Mexallon', quantity: 2700 },
      { name: 'Isogen', quantity: 675 },
      { name: 'Nocxium', quantity: 135 },
      { name: 'Zydrine', quantity: 34 },
      { name: 'Megacyte', quantity: 7 },
      { name: 'Nanotransistors', quantity: 9 },
      { name: 'Sylramic Fibers', quantity: 5 }
    ]
  },
  {
    id: 124,
    name: 'Heat Sink I Blueprint',
    category: 't1_modules',
    type_id: 12797,
    image_url: 'https://images.evetech.net/types/1164/icon?size=64',
    base_cost: 15000,
    build_time: 3500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 12000 },
      { name: 'Pyerite', quantity: 2800 },
      { name: 'Mexallon', quantity: 650 },
      { name: 'Isogen', quantity: 160 },
      { name: 'Nocxium', quantity: 32 },
      { name: 'Construction Blocks', quantity: 4 }
    ]
  },
  {
    id: 125,
    name: 'Heat Sink II Blueprint',
    category: 't2_modules',
    type_id: 12833,
    image_url: 'https://images.evetech.net/types/1164/icon?size=64',
    base_cost: 110000,
    build_time: 9500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 48000 },
      { name: 'Pyerite', quantity: 11500 },
      { name: 'Mexallon', quantity: 2700 },
      { name: 'Isogen', quantity: 675 },
      { name: 'Nocxium', quantity: 135 },
      { name: 'Zydrine', quantity: 34 },
      { name: 'Megacyte', quantity: 7 },
      { name: 'Nanotransistors', quantity: 9 },
      { name: 'Sylramic Fibers', quantity: 5 }
    ]
  },
  {
    id: 126,
    name: 'Ballistic Control System I Blueprint',
    category: 't1_modules',
    type_id: 12798,
    image_url: 'https://images.evetech.net/types/1160/icon?size=64',
    base_cost: 15000,
    build_time: 3500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 12000 },
      { name: 'Pyerite', quantity: 2800 },
      { name: 'Mexallon', quantity: 650 },
      { name: 'Isogen', quantity: 160 },
      { name: 'Nocxium', quantity: 32 },
      { name: 'Construction Blocks', quantity: 4 }
    ]
  },
  {
    id: 127,
    name: 'Ballistic Control System II Blueprint',
    category: 't2_modules',
    type_id: 12834,
    image_url: 'https://images.evetech.net/types/1160/icon?size=64',
    base_cost: 110000,
    build_time: 9500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 48000 },
      { name: 'Pyerite', quantity: 11500 },
      { name: 'Mexallon', quantity: 2700 },
      { name: 'Isogen', quantity: 675 },
      { name: 'Nocxium', quantity: 135 },
      { name: 'Zydrine', quantity: 34 },
      { name: 'Megacyte', quantity: 7 },
      { name: 'Nanotransistors', quantity: 9 },
      { name: 'Sylramic Fibers', quantity: 5 }
    ]
  },
  {
    id: 128,
    name: 'Tracking Enhancer I Blueprint',
    category: 't1_modules',
    type_id: 12799,
    image_url: 'https://images.evetech.net/types/1180/icon?size=64',
    base_cost: 15000,
    build_time: 3500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 12000 },
      { name: 'Pyerite', quantity: 2800 },
      { name: 'Mexallon', quantity: 650 },
      { name: 'Isogen', quantity: 160 },
      { name: 'Nocxium', quantity: 32 },
      { name: 'Construction Blocks', quantity: 4 }
    ]
  },
  {
    id: 129,
    name: 'Tracking Enhancer II Blueprint',
    category: 't2_modules',
    type_id: 12835,
    image_url: 'https://images.evetech.net/types/1180/icon?size=64',
    base_cost: 110000,
    build_time: 9500,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 48000 },
      { name: 'Pyerite', quantity: 11500 },
      { name: 'Mexallon', quantity: 2700 },
      { name: 'Isogen', quantity: 675 },
      { name: 'Nocxium', quantity: 135 },
      { name: 'Zydrine', quantity: 34 },
      { name: 'Megacyte', quantity: 7 },
      { name: 'Nanotransistors', quantity: 9 },
      { name: 'Sylramic Fibers', quantity: 5 }
    ]
  },
  {
    id: 130,
    name: 'Damage Control I Blueprint',
    category: 't1_modules',
    type_id: 12800,
    image_url: 'https://images.evetech.net/types/4399/icon?size=64',
    base_cost: 20000,
    build_time: 4000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 16000 },
      { name: 'Pyerite', quantity: 3800 },
      { name: 'Mexallon', quantity: 850 },
      { name: 'Isogen', quantity: 220 },
      { name: 'Nocxium', quantity: 44 },
      { name: 'Construction Blocks', quantity: 6 }
    ]
  },
  {
    id: 131,
    name: 'Damage Control II Blueprint',
    category: 't2_modules',
    type_id: 12836,
    image_url: 'https://images.evetech.net/types/4399/icon?size=64',
    base_cost: 150000,
    build_time: 12000,
    volume: 1,
    materials: [
      { name: 'Tritanium', quantity: 68000 },
      { name: 'Pyerite', quantity: 16200 },
      { name: 'Mexallon', quantity: 3800 },
      { name: 'Isogen', quantity: 950 },
      { name: 'Nocxium', quantity: 190 },
      { name: 'Zydrine', quantity: 48 },
      { name: 'Megacyte', quantity: 10 },
      { name: 'Nanotransistors', quantity: 13 },
      { name: 'Fermionic Condensates', quantity: 3 }
    ]
  }
];

// Additional BPOs would be added here for Ammo, Rigs, Capital Ships, Components, Structures
// Each with their full material requirements
