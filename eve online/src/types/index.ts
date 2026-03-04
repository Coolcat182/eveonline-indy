export interface JFContract {
  id?: number;
  discord_user_id: string;
  character_name: string;
  origin: string;
  destination: string;
  volume_m3: number;
  collateral: number;
  price: number;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  contract_id?: number;
  created_at?: string;
  completed_at?: string;
  notes?: string;
}

export interface IndustryJob {
  id?: number;
  discord_user_id: string;
  character_name: string;
  blueprint_type: string;
  blueprint_id?: number;
  product_type_id: number;
  product_name: string;
  quantity: number;
  material_cost: number;
  sell_price?: number;
  profit?: number;
  status: 'pending' | 'building' | 'completed' | 'sold';
  location?: string;
  started_at?: string;
  completed_at?: string;
  notes?: string;
}

export interface PIColony {
  id?: number;
  discord_user_id: string;
  character_name: string;
  planet_id: number;
  planet_name: string;
  planet_type: string;
  system: string;
  extraction_type?: string;
  production_type?: string;
  setup_cost: number;
  daily_profit: number;
  last_updated?: string;
  notes?: string;
}

export interface PISchematic {
  id?: number;
  colony_id: number;
  schematic_type: 'extraction' | 'basic' | 'advanced' | 'high_tech';
  output_type: string;
  cycle_time_hours: number;
  output_per_cycle: number;
}

export interface MarketOrder {
  id?: number;
  discord_user_id: string;
  type_id: number;
  type_name: string;
  location: string;
  buy_price?: number;
  sell_price?: number;
  volume: number;
  profit_margin?: number;
  status: 'active' | 'filled' | 'cancelled';
  created_at?: string;
  notes?: string;
}

export interface PriceCache {
  type_id: number;
  type_name: string;
  jita_buy: number;
  jita_sell: number;
  volume_30d: number;
  updated_at?: string;
}

export interface Location {
  id?: number;
  name: string;
  system: string;
  region: string;
  station_id?: number;
  is_jf_hub: boolean;
  is_common_destination: boolean;
}

export interface UserSettings {
  discord_user_id: string;
  default_location?: string;
  default_character?: string;
  notification_enabled: boolean;
  profit_threshold: number;
  created_at?: string;
}

export const JF_RATES = {
  jita_to_nullsec: 1500,
  nullsec_to_jita: 1200,
  nullsec_to_nullsec: 800,
  min_collateral: 500000000,
  min_volume: 5000,
};

export const PI_TIERS = {
  p0: { name: 'Raw Materials', tax_rate: 0.05 },
  p1: { name: 'Basic Commodities', tax_rate: 0.10 },
  p2: { name: 'Refined Commodities', tax_rate: 0.15 },
  p3: { name: 'Specialized Commodities', tax_rate: 0.20 },
  p4: { name: 'Advanced Commodities', tax_rate: 0.25 },
};

export interface TradeSettings {
  discord_user_id: string;
  nullsec_discount: number;
  jf_rate_per_m3: number;
  profit_threshold: number;
  preferred_hub: string;
}

export interface Character {
  id?: number;
  discord_user_id: string;
  name: string;
  character_id?: number;
  corporation?: string;
  skills?: string;
  manufacturing_bonus: number;
  research_bonus: number;
  pi_colonies: number;
  can_invent: boolean;
  can_build_capitals: boolean;
  notes?: string;
}

export interface Blueprint {
  id?: number;
  discord_user_id: string;
  name: string;
  type: 'BPO' | 'BPC';
  me: number;
  te: number;
  max_runs?: number;
  remaining_runs?: number;
  location?: string;
  notes?: string;
}

export interface MaterialInventory {
  id?: number;
  discord_user_id: string;
  item_name: string;
  quantity: number;
  original_quantity: number;
  buy_price: number;
  station: string;
  destination?: string;
  discount_applied: number;
}

export interface SellOrder {
  id?: number;
  discord_user_id: string;
  item_name: string;
  quantity: number;
  buy_price: number;
  sell_price: number;
  station: string;
  sold_quantity: number;
  status: 'active' | 'filled' | 'cancelled';
  notes?: string;
}

export const LOCATION_DISCOUNTS: Record<string, number> = {
  'RD-G2R': 0.05,
  'VA6-ED': 0.08,
  'D-PN': 0.10,
  'O-BKJY': 0.10,
  '7-60QB': 0.10,
  'PJ-LON': 0.12,
  'Z-7O': 0.12,
  'N-8YET': 0.10,
  'M-OEE8': 0.10,
};

export const PURE_BLIND_SYSTEMS = [
  'D-PN', 'VA6-ED', 'RD-G2R', 'O-BKJY', '7-60QB', 'X-7OMU',
  'E-YCML', 'H-PA29', 'F-9CZX', 'FDZ4-A', 'B-VIP9', 'V7-MID'
];
