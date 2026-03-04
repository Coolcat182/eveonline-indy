import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import axios from 'axios';

const ESI_BASE = 'https://esi.evetech.net/latest';
const PLEX_TYPE_ID = 44992;

interface PlexData {
  jitaBuy: number;
  jitaSell: number;
  volume: number;
  updatedAt: string;
}

let cachedPlexData: PlexData | null = null;
let lastFetch: number = 0;
const CACHE_TTL = 300000;

const BROKER_FEE = 0.05;
const SALES_TAX = 0.04;

const PLEX_STORE_ITEMS = [
  { 
    name: 'Multiple Pilot Training (24x)', 
    plexCost: 4600, 
    quantity: 24,
    typeIds: [87216],
    typeName: 'Multiple Pilot Training Certificate',
    category: 'Account',
    dailyVolume: 500
  },
  { 
    name: 'Multiple Pilot Training (6x)', 
    plexCost: 1320, 
    quantity: 6,
    typeIds: [87216],
    typeName: 'Multiple Pilot Training Certificate',
    category: 'Account',
    dailyVolume: 500
  },
  { 
    name: 'Multiple Pilot Training (1x)', 
    plexCost: 240, 
    quantity: 1,
    typeIds: [87216],
    typeName: 'Multiple Pilot Training Certificate',
    category: 'Account',
    dailyVolume: 500
  },
  { 
    name: 'Skill Extractor (60x)', 
    plexCost: 4600, 
    quantity: 60,
    typeIds: [40520],
    typeName: 'Skill Extractor',
    category: 'Skills',
    dailyVolume: 2000
  },
  { 
    name: 'Skill Extractor (20x)', 
    plexCost: 1680, 
    quantity: 20,
    typeIds: [40520],
    typeName: 'Skill Extractor',
    category: 'Skills',
    dailyVolume: 2000
  },
  { 
    name: 'Skill Extractor (6x)', 
    plexCost: 540, 
    quantity: 6,
    typeIds: [40520],
    typeName: 'Skill Extractor',
    category: 'Skills',
    dailyVolume: 2000
  },
  { 
    name: 'Skill Extractor (1x)', 
    plexCost: 95, 
    quantity: 1,
    typeIds: [40520],
    typeName: 'Skill Extractor',
    category: 'Skills',
    dailyVolume: 2000
  },
  { 
    name: 'Large Skill Injector (110x)', 
    plexCost: 9900, 
    quantity: 110,
    typeIds: [40519],
    typeName: 'Large Skill Injector',
    category: 'Skills',
    dailyVolume: 1500
  },
  { 
    name: 'Large Skill Injector (24x)', 
    plexCost: 2400, 
    quantity: 24,
    typeIds: [40519],
    typeName: 'Large Skill Injector',
    category: 'Skills',
    dailyVolume: 1500
  },
  { 
    name: 'Large Skill Injector (6x)', 
    plexCost: 660, 
    quantity: 6,
    typeIds: [40519],
    typeName: 'Large Skill Injector',
    category: 'Skills',
    dailyVolume: 1500
  },
  { 
    name: 'Large Skill Injector (1x)', 
    plexCost: 120, 
    quantity: 1,
    typeIds: [40519],
    typeName: 'Large Skill Injector',
    category: 'Skills',
    dailyVolume: 1500
  },
  { 
    name: 'Dual Character Training (30 Days)', 
    plexCost: 500, 
    quantity: 1,
    typeIds: [9999],
    typeName: 'Dual Character Training',
    category: 'Account',
    dailyVolume: 200
  },
];

interface StoreItem {
  name: string;
  plexCost: number;
  quantity: number;
  typeIds: number[];
  typeName: string;
  category: string;
  dailyVolume: number;
}

interface ItemPrice {
  typeId: number;
  buy: number;
  sell: number;
}

async function fetchPlexPrices(): Promise<PlexData | null> {
  const now = Date.now();
  if (cachedPlexData && (now - lastFetch) < CACHE_TTL) {
    return cachedPlexData;
  }
  
  try {
    const response = await axios.get(`${ESI_BASE}/markets/10000002/orders/`, {
      params: { type_id: PLEX_TYPE_ID },
      headers: { 'User-Agent': 'eve-services-plex' },
      timeout: 10000
    });
    
    const orders = response.data;
    const buyOrders = orders.filter((o: { is_buy_order: boolean }) => o.is_buy_order);
    const sellOrders = orders.filter((o: { is_buy_order: boolean }) => !o.is_buy_order);
    
    const jitaBuy = buyOrders.length > 0 ? Math.max(...buyOrders.map((o: { price: number }) => o.price)) : 0;
    const jitaSell = sellOrders.length > 0 ? Math.min(...sellOrders.map((o: { price: number }) => o.price)) : 0;
    
    const historyResponse = await axios.get(`${ESI_BASE}/markets/10000002/history/`, {
      params: { type_id: PLEX_TYPE_ID },
      headers: { 'User-Agent': 'eve-services-plex' },
      timeout: 10000
    });
    
    const history = historyResponse.data.slice(-30);
    const volume = history.reduce((sum: number, day: { volume: number }) => sum + day.volume, 0);
    
    cachedPlexData = {
      jitaBuy,
      jitaSell,
      volume,
      updatedAt: new Date().toISOString()
    };
    lastFetch = now;
    
    return cachedPlexData;
  } catch (error) {
    console.error('Failed to fetch PLEX prices:', error);
    return cachedPlexData;
  }
}

async function fetchItemPrice(typeId: number): Promise<ItemPrice | null> {
  try {
    const response = await axios.get(`${ESI_BASE}/markets/10000002/orders/`, {
      params: { type_id: typeId },
      headers: { 'User-Agent': 'eve-services-plex' },
      timeout: 10000
    });
    
    const orders = response.data;
    const buyOrders = orders.filter((o: { is_buy_order: boolean }) => o.is_buy_order);
    const sellOrders = orders.filter((o: { is_buy_order: boolean }) => !o.is_buy_order);
    
    const buy = buyOrders.length > 0 ? Math.max(...buyOrders.map((o: { price: number }) => o.price)) : 0;
    const sell = sellOrders.length > 0 ? Math.min(...sellOrders.map((o: { price: number }) => o.price)) : 0;
    
    return { typeId, buy, sell };
  } catch {
    return null;
  }
}

export const data = new SlashCommandBuilder()
  .setName('plex')
  .setDescription('PLEX to ISK conversion and store arbitrage')
  .addSubcommand(sub =>
    sub
      .setName('store')
      .setDescription('PLEX store arbitrage - find profitable items to resell'))
  .addSubcommand(sub =>
    sub
      .setName('item')
      .setDescription('Analyze a specific store item')
      .addStringOption(opt => opt.setName('name').setDescription('Item name (e.g., "MCT 24")').setRequired(true)))
  .addSubcommand(sub =>
    sub
      .setName('cycle')
      .setDescription('PLEX→Store→Market→PLEX cycle analysis'))
  .addSubcommand(sub =>
    sub
      .setName('price')
      .setDescription('Current PLEX prices in Jita'))
  .addSubcommand(sub =>
    sub
      .setName('convert')
      .setDescription('Convert ISK to PLEX or PLEX to ISK')
      .addNumberOption(opt => opt.setName('amount').setDescription('Amount to convert').setRequired(true))
      .addStringOption(opt => opt.setName('direction').setDescription('Conversion direction').addChoices(
        { name: 'ISK → PLEX', value: 'isk_to_plex' },
        { name: 'PLEX → ISK', value: 'plex_to_isk' }
      ).setRequired(true)));

const PLEX_PER_OMEGA_DAY = 500;

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  await interaction.deferReply();
  
  switch (subcommand) {
    case 'store': await handleStore(interaction); break;
    case 'item': await handleItem(interaction); break;
    case 'cycle': await handleCycle(interaction); break;
    case 'price': await handlePrice(interaction); break;
    case 'convert': await handleConvert(interaction); break;
  }
}

async function handleStore(interaction: CommandInteraction) {
  const plexData = await fetchPlexPrices();
  
  if (!plexData || plexData.jitaSell === 0) {
    await interaction.editReply({ content: 'Unable to fetch PLEX prices.' });
    return;
  }
  
  const results: (StoreItem & { 
    marketSell: number; 
    plexPerUnit: number; 
    iskCostPerUnit: number; 
    grossProfit: number; 
    netProfit: number; 
    roi: number;
    profitable: boolean;
  })[] = [];
  
  for (const item of PLEX_STORE_ITEMS) {
    const priceData = await fetchItemPrice(item.typeIds[0]);
    if (!priceData || priceData.sell === 0) continue;
    
    const plexPerUnit = item.plexCost / item.quantity;
    const iskCostPerUnit = plexPerUnit * plexData.jitaSell;
    const marketSell = priceData.sell;
    const grossProfit = marketSell - iskCostPerUnit;
    const netProfit = marketSell * (1 - BROKER_FEE - SALES_TAX) - iskCostPerUnit;
    const roi = (netProfit / iskCostPerUnit) * 100;
    
    results.push({
      ...item,
      marketSell,
      plexPerUnit,
      iskCostPerUnit,
      grossProfit,
      netProfit,
      roi,
      profitable: netProfit > 0
    });
  }
  
  results.sort((a, b) => b.roi - a.roi);
  
  const profitableItems = results.filter(r => r.profitable);
  const unprofitableItems = results.filter(r => !r.profitable);
  
  let description = '**PLEX Store → Market Arbitrage**\n\n';
  
  if (profitableItems.length > 0) {
    description += '**✅ PROFITABLE Items:**\n';
    for (const item of profitableItems.slice(0, 5)) {
      description += `**${item.name}**: ${item.roi.toFixed(1)}% ROI (${item.netProfit.toLocaleString()} ISK/unit profit)\n`;
      description += `   PLEX/unit: ${item.plexPerUnit.toFixed(2)} | ISK cost: ${item.iskCostPerUnit.toLocaleString()} | Market: ${item.marketSell.toLocaleString()}\n\n`;
    }
  }
  
  if (unprofitableItems.length > 0 && profitableItems.length === 0) {
    description += '**⚠️ NO PROFITABLE ITEMS FOUND**\n';
    description += 'Current market prices don\'t support arbitrage.\n\n';
    description += '**Closest to profitable:**\n';
    for (const item of unprofitableItems.slice(0, 3)) {
      description += `${item.name}: ${item.roi.toFixed(1)}% (${item.netProfit.toLocaleString()} ISK loss)\n`;
    }
  }
  
  const embed = new EmbedBuilder()
    .setTitle('PLEX Store Arbitrage Analysis')
    .setColor(profitableItems.length > 0 ? 0x00ff00 : 0xff0000)
    .setDescription(description)
    .addFields(
      { name: 'PLEX Price (Jita Sell)', value: `${plexData.jitaSell.toLocaleString()} ISK`, inline: true },
      { name: 'Broker Fee', value: `${(BROKER_FEE * 100).toFixed(1)}%`, inline: true },
      { name: 'Sales Tax', value: `${(SALES_TAX * 100).toFixed(1)}%`, inline: true }
    )
    .addFields({ 
      name: 'Strategy', 
      value: profitableItems.length > 0 
        ? `1. Buy ${profitableItems[0].name} from PLEX store\n2. Sell on market for ${profitableItems[0].marketSell.toLocaleString()} ISK\n3. Profit: ${profitableItems[0].netProfit.toLocaleString()} ISK/unit (${profitableItems[0].roi.toFixed(1)}% ROI)`
        : 'Wait for market prices to increase or PLEX prices to decrease'
    })
    .setFooter({ text: 'Only PLEX store items that can be sold on market' });
  
  await interaction.editReply({ embeds: [embed] });
}

async function handleItem(interaction: CommandInteraction) {
  const nameInput = (interaction.options.get('name')?.value as string).toLowerCase();
  const plexData = await fetchPlexPrices();
  
  if (!plexData || plexData.jitaSell === 0) {
    await interaction.editReply({ content: 'Unable to fetch PLEX prices.' });
    return;
  }
  
  const item = PLEX_STORE_ITEMS.find(i => 
    i.name.toLowerCase().includes(nameInput) ||
    i.typeName.toLowerCase().includes(nameInput)
  );
  
  if (!item) {
    await interaction.editReply({ content: `Item not found. Try: ${PLEX_STORE_ITEMS.map(i => i.name).slice(0, 5).join(', ')}` });
    return;
  }
  
  const priceData = await fetchItemPrice(item.typeIds[0]);
  
  const plexPerUnit = item.plexCost / item.quantity;
  const iskCostPerUnit = plexPerUnit * plexData.jitaSell;
  const marketSell = priceData?.sell || 0;
  const grossProfit = marketSell - iskCostPerUnit;
  const netProfit = marketSell > 0 ? marketSell * (1 - BROKER_FEE - SALES_TAX) - iskCostPerUnit : -iskCostPerUnit;
  const roi = (netProfit / iskCostPerUnit) * 100;
  const breakEvenPrice = iskCostPerUnit / (1 - BROKER_FEE - SALES_TAX);
  
  const embed = new EmbedBuilder()
    .setTitle(`Store Item Analysis: ${item.name}`)
    .setColor(netProfit > 0 ? 0x00ff00 : 0xff0000)
    .addFields(
      { name: 'PLEX Cost', value: `${item.plexCost.toLocaleString()} PLEX`, inline: true },
      { name: 'Quantity', value: item.quantity.toString(), inline: true },
      { name: 'PLEX per Unit', value: plexPerUnit.toFixed(2), inline: true },
      { name: 'ISK Cost/Unit', value: `${iskCostPerUnit.toLocaleString()} ISK`, inline: true },
      { name: 'Market Sell Price', value: marketSell > 0 ? `${marketSell.toLocaleString()} ISK` : 'No data', inline: true },
      { name: 'Break-Even Price', value: `${breakEvenPrice.toLocaleString()} ISK`, inline: true }
    )
    .addFields({ name: '\u200B', value: '\u200B' })
    .addFields(
      { name: 'Gross Profit/Unit', value: `${grossProfit.toLocaleString()} ISK`, inline: true },
      { name: 'Net Profit/Unit', value: `${netProfit.toLocaleString()} ISK`, inline: true },
      { name: 'ROI', value: `${roi.toFixed(2)}%`, inline: true }
    );
  
  if (netProfit > 0) {
    const cycleExample = {
      plexInvested: item.plexCost * 10,
      unitsProduced: item.quantity * 10,
      totalIskRevenue: marketSell * item.quantity * 10 * (1 - BROKER_FEE - SALES_TAX),
      plexReturned: Math.floor(marketSell * item.quantity * 10 * (1 - BROKER_FEE - SALES_TAX) / plexData.jitaSell)
    };
    
    embed.addFields({
      name: 'Cycle Example (10x Purchase)',
      value: `Invest: ${cycleExample.plexInvested.toLocaleString()} PLEX\n` +
             `Sell: ${cycleExample.unitsProduced} units\n` +
             `Revenue: ${cycleExample.totalIskRevenue.toLocaleString()} ISK\n` +
             `Can Buy Back: ${cycleExample.plexReturned.toLocaleString()} PLEX\n` +
             `Net: ${cycleExample.plexReturned - cycleExample.plexInvested > 0 ? '+' : ''}${cycleExample.plexReturned - cycleExample.plexInvested} PLEX`
    });
  }
  
  embed.addFields({
    name: 'Verdict',
    value: netProfit > 0 ? '✅ PROFITABLE - Buy and resell!' : 
           netProfit > -100000 ? '⚠️ Close to break-even' : '❌ NOT PROFITABLE - Skip'
  });
  
  await interaction.editReply({ embeds: [embed] });
}

async function handleCycle(interaction: CommandInteraction) {
  const plexData = await fetchPlexPrices();
  
  if (!plexData || plexData.jitaSell === 0) {
    await interaction.editReply({ content: 'Unable to fetch PLEX prices.' });
    return;
  }
  
  let bestItem: (StoreItem & { 
    marketSell: number; 
    plexPerUnit: number; 
    iskCostPerUnit: number; 
    netProfit: number; 
    roi: number;
    plexGrowth: number;
  }) | null = null;
  
  for (const item of PLEX_STORE_ITEMS) {
    const priceData = await fetchItemPrice(item.typeIds[0]);
    if (!priceData || priceData.sell === 0) continue;
    
    const plexPerUnit = item.plexCost / item.quantity;
    const iskCostPerUnit = plexPerUnit * plexData.jitaSell;
    const marketSell = priceData.sell;
    const netRevenue = marketSell * (1 - BROKER_FEE - SALES_TAX);
    const plexReturned = netRevenue / plexData.jitaSell;
    const plexGrowth = plexReturned - plexPerUnit;
    
    if (!bestItem || plexGrowth > bestItem.plexGrowth) {
      bestItem = {
        ...item,
        marketSell,
        plexPerUnit,
        iskCostPerUnit,
        netProfit: netRevenue - iskCostPerUnit,
        roi: ((netRevenue - iskCostPerUnit) / iskCostPerUnit) * 100,
        plexGrowth
      };
    }
  }
  
  const buy500Plex = plexData.jitaSell * 500;
  const dailyIskNeeded = buy500Plex / 30;
  
  const embed = new EmbedBuilder()
    .setTitle('PLEX → ISK Cycle Analysis')
    .setColor(0x9B59B6)
    .setDescription('How to sustain/grow PLEX through store arbitrage');
  
  if (bestItem && bestItem.plexGrowth > 0) {
    const startingPlex = 5000;
    const cyclesPerMonth = 4;
    const plexPerCycle = bestItem.plexPerUnit * bestItem.quantity;
    const plexGrowthPerCycle = bestItem.plexGrowth * bestItem.quantity;
    
    const monthlyPlexGrowth = plexGrowthPerCycle * cyclesPerMonth;
    const monthlyIskValue = monthlyPlexGrowth * plexData.jitaSell;
    
    embed.addFields({
      name: `✅ Best Store Item: ${bestItem.name}`,
      value: `ROI: ${bestItem.roi.toFixed(1)}%\n` +
             `PLEX Growth: +${bestItem.plexGrowth.toFixed(2)} PLEX per unit\n` +
             `Net Profit: ${bestItem.netProfit.toLocaleString()} ISK/unit`,
      inline: false
    });
    
    embed.addFields({
      name: 'Monthly Cycle Potential',
      value: `Starting: ${startingPlex.toLocaleString()} PLEX\n` +
             `After 4 cycles: ${(startingPlex + monthlyPlexGrowth).toLocaleString()} PLEX\n` +
             `Monthly Growth: +${monthlyPlexGrowth.toFixed(0)} PLEX\n` +
             `ISK Value: +${monthlyIskValue.toLocaleString()} ISK`,
      inline: true
    });
    
    const omegaDaysProduced = monthlyPlexGrowth / PLEX_PER_OMEGA_DAY;
    embed.addFields({
      name: 'Omega Days Generated',
      value: `+${omegaDaysProduced.toFixed(1)} days/month\n` +
             `${(omegaDaysProduced / 30 * 100).toFixed(0)}% of Omega cost`,
      inline: true
    });
  } else {
    embed.addFields({
      name: '⚠️ No Profitable Store Arbitrage',
      value: 'Current market conditions don\'t support PLEX growth through store items.\n\n' +
             'Alternative ISK sources needed:',
      inline: false
    });
    
    embed.addFields({
      name: 'Daily ISK for Omega',
      value: `${dailyIskNeeded.toLocaleString()} ISK/day\n` +
             `${(dailyIskNeeded / 24).toLocaleString()} ISK/hour`,
      inline: true
    });
    
    embed.addFields({
      name: 'PI Requirements',
      value: `${(dailyIskNeeded / 500000).toFixed(1)} max-profit colonies`,
      inline: true
    });
  }
  
  embed.addFields({ name: '\u200B', value: '\u200B' });
  
  embed.addFields({
    name: 'Combined Strategy (Max Profit)',
    value: `1. **Store Arbitrage**: ${bestItem && bestItem.plexGrowth > 0 ? `${bestItem.name} for +${bestItem.roi.toFixed(0)}% ROI` : 'Wait for better prices'}\n` +
           `2. **PI**: 6 colonies @ 500K/day = ${(500000 * 6 * 30).toLocaleString()} ISK/month\n` +
           `3. **Trading**: JF imports = ~200M ISK/month\n` +
           `4. **Total**: Can pay Omega + grow PLEX reserves`
  });
  
  await interaction.editReply({ embeds: [embed] });
}

async function handlePrice(interaction: CommandInteraction) {
  const plexData = await fetchPlexPrices();
  
  if (!plexData || plexData.jitaSell === 0) {
    await interaction.editReply({ content: 'Unable to fetch PLEX prices.' });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('PLEX Prices - Jita')
    .setColor(0xF1C40F)
    .addFields(
      { name: 'Buy Orders', value: `${plexData.jitaBuy.toLocaleString()} ISK`, inline: true },
      { name: 'Sell Orders', value: `${plexData.jitaSell.toLocaleString()} ISK`, inline: true },
      { name: 'Spread', value: `${((plexData.jitaSell - plexData.jitaBuy) / plexData.jitaBuy * 100).toFixed(2)}%`, inline: true },
      { name: '500 PLEX (1 Month Sub)', value: `${(plexData.jitaSell * 500).toLocaleString()} ISK`, inline: true },
      { name: 'Daily Omega Cost', value: `${(plexData.jitaSell * 500 / 30).toLocaleString()} ISK`, inline: true },
      { name: 'Hourly Omega Cost', value: `${(plexData.jitaSell * 500 / 30 / 24).toLocaleString()} ISK`, inline: true }
    )
    .setFooter({ text: `Updated: ${new Date(plexData.updatedAt).toLocaleTimeString()}` });
  
  await interaction.editReply({ embeds: [embed] });
}

async function handleConvert(interaction: CommandInteraction) {
  const amount = interaction.options.get('amount')?.value as number;
  const direction = interaction.options.get('direction')?.value as string;
  
  const plexData = await fetchPlexPrices();
  
  if (!plexData || plexData.jitaSell === 0) {
    await interaction.editReply({ content: 'Unable to fetch PLEX prices.' });
    return;
  }
  
  let result: { plex: number; isk: number; rate: number };
  
  if (direction === 'isk_to_plex') {
    const plex = Math.floor(amount / plexData.jitaSell);
    result = { plex, isk: amount, rate: plexData.jitaSell };
  } else {
    const isk = amount * plexData.jitaBuy;
    result = { plex: amount, isk, rate: plexData.jitaBuy };
  }
  
  const omegaDays = Math.floor(result.plex / PLEX_PER_OMEGA_DAY);
  
  const embed = new EmbedBuilder()
    .setTitle('PLEX ↔ ISK Conversion')
    .setColor(0x3498DB)
    .addFields(
      { name: direction === 'isk_to_plex' ? 'ISK Input' : 'PLEX Input', 
        value: direction === 'isk_to_plex' ? `${result.isk.toLocaleString()} ISK` : `${result.plex.toLocaleString()} PLEX`, 
        inline: true },
      { name: direction === 'isk_to_plex' ? 'PLEX Received' : 'ISK Received', 
        value: direction === 'isk_to_plex' ? `${result.plex.toLocaleString()} PLEX` : `${result.isk.toLocaleString()} ISK`, 
        inline: true },
      { name: 'Rate', value: `${result.rate.toLocaleString()} ISK/PLEX`, inline: true },
      { name: 'Omega Days', value: `${omegaDays} days`, inline: true }
    );
  
  await interaction.editReply({ embeds: [embed] });
}
