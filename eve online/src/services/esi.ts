import axios from 'axios';
import 'dotenv/config';

const ESI_BASE = 'https://esi.evetech.net/latest';
const USER_AGENT = process.env.ESI_USER_AGENT || 'eve-services';

const esiClient = axios.create({
  baseURL: ESI_BASE,
  headers: { 'User-Agent': USER_AGENT },
  timeout: 10000,
});

interface MarketOrder {
  price: number;
  volume_remain: number;
  is_buy_order: boolean;
}

interface TypeData {
  type_id: number;
  name: string;
  volume: number;
  packaged_volume: number;
}

const THE_FORGE_REGION = 10000002;
const JITA_SYSTEM = 30000142;

export async function getTypeInfo(typeId: number): Promise<TypeData | null> {
  try {
    const response = await esiClient.get(`/universe/types/${typeId}/`);
    return {
      type_id: typeId,
      name: response.data.name,
      volume: response.data.volume,
      packaged_volume: response.data.packaged_volume,
    };
  } catch {
    return null;
  }
}

export async function searchType(query: string): Promise<{ id: number; name: string }[]> {
  try {
    const response = await esiClient.get('/search/', {
      params: { categories: 'inventory_type', search: query, strict: false },
    });
    const typeIds: number[] = response.data.inventory_type || [];
    const results: { id: number; name: string }[] = [];
    
    for (const id of typeIds.slice(0, 10)) {
      const typeInfo = await getTypeInfo(id);
      if (typeInfo) {
        results.push({ id: typeInfo.type_id, name: typeInfo.name });
      }
    }
    return results;
  } catch {
    return [];
  }
}

export async function getJitaPrices(typeId: number): Promise<{ buy: number; sell: number } | null> {
  try {
    const response = await esiClient.get(`/markets/${THE_FORGE_REGION}/orders/`, {
      params: { type_id: typeId },
    });
    const orders: MarketOrder[] = response.data;
    
    const jitaOrders = orders.filter(o => o.is_buy_order || true);
    
    const buyOrders = jitaOrders.filter(o => o.is_buy_order);
    const sellOrders = jitaOrders.filter(o => !o.is_buy_order);
    
    const buy = buyOrders.length > 0 ? Math.max(...buyOrders.map(o => o.price)) : 0;
    const sell = sellOrders.length > 0 ? Math.min(...sellOrders.map(o => o.price)) : 0;
    
    return { buy, sell };
  } catch {
    return null;
  }
}

export async function getMarketVolume(typeId: number, days: number = 30): Promise<number> {
  try {
    const response = await esiClient.get(`/markets/${THE_FORGE_REGION}/history/`, {
      params: { type_id: typeId },
    });
    const history = response.data.slice(-days);
    return history.reduce((sum: number, day: { volume: number }) => sum + day.volume, 0);
  } catch {
    return 0;
  }
}

export async function getSystemInfo(systemId: number): Promise<{ name: string; region_id: number } | null> {
  try {
    const response = await esiClient.get(`/universe/systems/${systemId}/`);
    return {
      name: response.data.name,
      region_id: response.data.constellation_id,
    };
  } catch {
    return null;
  }
}

export async function getRegionInfo(regionId: number): Promise<string | null> {
  try {
    const response = await esiClient.get(`/universe/regions/${regionId}/`);
    return response.data.name;
  } catch {
    return null;
  }
}

export async function getRoute(origin: number, destination: number, flag: string = 'secure'): Promise<number[]> {
  try {
    const response = await esiClient.get(`/route/${origin}/${destination}/`, {
      params: { flag },
    });
    return response.data;
  } catch {
    return [];
  }
}

export { JITA_SYSTEM, THE_FORGE_REGION };
