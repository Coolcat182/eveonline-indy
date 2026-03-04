import Database from 'better-sqlite3';
import path from 'path';

const db = new Database(path.join(__dirname, '../../data/eve_services.db'));

db.pragma('journal_mode = WAL');

db.exec(`
  CREATE TABLE IF NOT EXISTS jf_contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    character_name TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    volume_m3 REAL NOT NULL,
    collateral REAL NOT NULL,
    price REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    contract_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    notes TEXT
  );

  CREATE TABLE IF NOT EXISTS industry_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    character_name TEXT NOT NULL,
    blueprint_type TEXT NOT NULL,
    blueprint_id INTEGER,
    product_type_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    material_cost REAL NOT NULL,
    sell_price REAL,
    profit REAL,
    status TEXT DEFAULT 'pending',
    location TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    notes TEXT
  );

  CREATE TABLE IF NOT EXISTS pi_colonies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    character_name TEXT NOT NULL,
    planet_id INTEGER NOT NULL,
    planet_name TEXT NOT NULL,
    planet_type TEXT NOT NULL,
    system TEXT NOT NULL,
    extraction_type TEXT,
    production_type TEXT,
    setup_cost REAL DEFAULT 0,
    daily_profit REAL DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
  );

  CREATE TABLE IF NOT EXISTS pi_schematics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    colony_id INTEGER NOT NULL,
    schematic_type TEXT NOT NULL,
    output_type TEXT NOT NULL,
    cycle_time_hours INTEGER NOT NULL,
    output_per_cycle INTEGER NOT NULL,
    FOREIGN KEY (colony_id) REFERENCES pi_colonies(id)
  );

  CREATE TABLE IF NOT EXISTS market_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    type_id INTEGER NOT NULL,
    type_name TEXT NOT NULL,
    location TEXT NOT NULL,
    buy_price REAL,
    sell_price REAL,
    volume INTEGER NOT NULL,
    profit_margin REAL,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
  );

  CREATE TABLE IF NOT EXISTS price_cache (
    type_id INTEGER PRIMARY KEY,
    type_name TEXT NOT NULL,
    jita_buy REAL,
    jita_sell REAL,
    volume_30d REAL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    system TEXT NOT NULL,
    region TEXT NOT NULL,
    station_id INTEGER,
    is_jf_hub BOOLEAN DEFAULT 0,
    is_common_destination BOOLEAN DEFAULT 0
  );

  CREATE TABLE IF NOT EXISTS user_settings (
    discord_user_id TEXT PRIMARY KEY,
    default_location TEXT,
    default_character TEXT,
    notification_enabled BOOLEAN DEFAULT 1,
    profit_threshold REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS trade_settings (
    discord_user_id TEXT PRIMARY KEY,
    nullsec_discount REAL DEFAULT 0.10,
    jf_rate_per_m3 REAL DEFAULT 1500,
    profit_threshold REAL DEFAULT 10000000,
    preferred_hub TEXT DEFAULT 'D-PN',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    character_id INTEGER,
    corporation TEXT,
    skills TEXT,
    manufacturing_bonus REAL DEFAULT 0,
    research_bonus REAL DEFAULT 0,
    pi_colonies INTEGER DEFAULT 6,
    can_invent INTEGER DEFAULT 0,
    can_build_capitals INTEGER DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(discord_user_id, name)
  );

  CREATE TABLE IF NOT EXISTS blueprints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    me INTEGER DEFAULT 0,
    te INTEGER DEFAULT 0,
    max_runs INTEGER,
    remaining_runs INTEGER,
    location TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
  );

  CREATE TABLE IF NOT EXISTS material_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    original_quantity INTEGER NOT NULL,
    buy_price REAL NOT NULL,
    station TEXT NOT NULL,
    destination TEXT,
    discount_applied REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS sell_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    buy_price REAL NOT NULL,
    sell_price REAL NOT NULL,
    station TEXT NOT NULL,
    sold_quantity INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
  );
`);

const wintercoStations = [
  { name: 'D-PN Solar Fleet', system: 'D-PN', region: 'Pure Blind', is_jf_hub: true },
  { name: 'VA6-ED Keepstar', system: 'VA6-ED', region: 'Pure Blind', is_jf_hub: true },
  { name: 'RD-G2R Industry Hub', system: 'RD-G2R', region: 'Pure Blind', is_jf_hub: false },
  { name: 'O-BKJY', system: 'O-BKJY', region: 'Pure Blind', is_jf_hub: false },
  { name: '7-60QB', system: '7-60QB', region: 'Pure Blind', is_jf_hub: false },
  { name: 'X-7OMU', system: 'X-7OMU', region: 'Pure Blind', is_jf_hub: false },
  { name: 'E-YCML', system: 'E-YCML', region: 'Pure Blind', is_jf_hub: false },
  { name: 'H-PA29', system: 'H-PA29', region: 'Pure Blind', is_jf_hub: false },
  { name: 'F-9CZX', system: 'F-9CZX', region: 'Pure Blind', is_jf_hub: false },
  { name: 'FDZ4-A', system: 'FDZ4-A', region: 'Pure Blind', is_jf_hub: false },
  { name: 'B-VIP9', system: 'B-VIP9', region: 'Pure Blind', is_jf_hub: false },
  { name: 'V7-MID', system: 'V7-MID', region: 'Pure Blind', is_jf_hub: false },
  { name: 'PJ-LON', system: 'PJ-LON', region: 'Tenal', is_jf_hub: false },
  { name: 'Z-7O', system: 'Z-7O', region: 'Tenal', is_jf_hub: false },
  { name: 'N-8YET', system: 'N-8YET', region: 'Tribute', is_jf_hub: false },
  { name: 'M-OEE8', system: 'M-OEE8', region: 'Tribute', is_jf_hub: false },
  { name: 'Jita IV - Moon 4 - Caldari Navy Assembly Plant', system: 'Jita', region: 'The Forge', is_jf_hub: true },
];

const insertLocation = db.prepare(`
  INSERT OR IGNORE INTO locations (name, system, region, is_jf_hub)
  VALUES (@name, @system, @region, @is_jf_hub)
`);

for (const station of wintercoStations) {
  insertLocation.run(station);
}

export default db;
