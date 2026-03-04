import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';

export const data = new SlashCommandBuilder()
  .setName('trading')
  .setDescription('Jita to WinterCo trading and import')
  .addSubcommand(sub =>
    sub
      .setName('import')
      .setDescription('Calculate import profit from Jita to WinterCo')
      .addStringOption(opt => opt.setName('item').setDescription('Item name').setRequired(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity').setRequired(true))
      .addNumberOption(opt => opt.setName('jita_buy').setDescription('Jita buy price per unit').setRequired(true))
      .addNumberOption(opt => opt.setName('local_sell').setDescription('Local sell price per unit').setRequired(true))
      .addNumberOption(opt => opt.setName('volume').setDescription('Volume per unit (m3)').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('stations')
      .setDescription('Recommended stations for buying/selling in WinterCo'))
  .addSubcommand(sub =>
    sub
      .setName('bestimports')
      .setDescription('Show best items to import from Jita'))
  .addSubcommand(sub =>
    sub
      .setName('sellorders')
      .setDescription('Create a sell order tracking')
      .addStringOption(opt => opt.setName('item').setDescription('Item name').setRequired(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity').setRequired(true))
      .addNumberOption(opt => opt.setName('buy_price').setDescription('Your buy price total').setRequired(true))
      .addNumberOption(opt => opt.setName('sell_price').setDescription('Sell price per unit').setRequired(true))
      .addStringOption(opt => opt.setName('station').setDescription('Selling station').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('orders')
      .setDescription('List your active sell orders'))
  .addSubcommand(sub =>
    sub
      .setName('flip')
      .setDescription('Calculate station flip profit')
      .addStringOption(opt => opt.setName('item').setDescription('Item name').setRequired(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity').setRequired(true))
      .addNumberOption(opt => opt.setName('buy_price').setDescription('Buy price per unit').setRequired(true))
      .addNumberOption(opt => opt.setName('sell_price').setDescription('Sell price per unit').setRequired(true)));

const WINTERCO_HUBS = [
  { name: 'D-PN Solar Fleet', system: 'D-PN', region: 'Pure Blind', type: 'Primary Hub', discount: 0.10 },
  { name: 'VA6-ED Keepstar', system: 'VA6-ED', region: 'Pure Blind', type: 'JF Hub', discount: 0.08 },
  { name: 'RD-G2R', system: 'RD-G2R', region: 'Pure Blind', type: 'Industry Hub', discount: 0.05 },
  { name: 'O-BKJY', system: 'O-BKJY', region: 'Pure Blind', type: 'Regional', discount: 0.10 },
  { name: '7-60QB', system: '7-60QB', region: 'Pure Blind', type: 'Regional', discount: 0.10 },
  { name: 'PJ-LON', system: 'PJ-LON', region: 'Tenal', type: 'Regional', discount: 0.12 },
  { name: 'Z-7O', system: 'Z-7O', region: 'Tenal', type: 'Regional', discount: 0.12 },
  { name: 'N-8YET', system: 'N-8YET', region: 'Tribute', type: 'Regional', discount: 0.10 },
  { name: 'M-OEE8', system: 'M-OEE8', region: 'Tribute', type: 'Regional', discount: 0.10 },
];

const BEST_IMPORTS = [
  { name: 'Ishtar', category: 'Ships', jitaPrice: 175000000, localMultiplier: 1.15, volume: 15000 },
  { name: 'Stratios', category: 'Ships', jitaPrice: 280000000, localMultiplier: 1.12, volume: 25000 },
  { name: 'Capacitor Recharger II', category: 'Modules', jitaPrice: 1200000, localMultiplier: 1.20, volume: 5 },
  { name: '10MN Afterburner II', category: 'Modules', jitaPrice: 2800000, localMultiplier: 1.18, volume: 25 },
  { name: 'Drone Damage Amplifier II', category: 'Modules', jitaPrice: 850000, localMultiplier: 1.22, volume: 5 },
  { name: 'Large Shield Extender II', category: 'Modules', jitaPrice: 450000, localMultiplier: 1.25, volume: 25 },
  { name: 'Ogre II', category: 'Drones', jitaPrice: 1800000, localMultiplier: 1.18, volume: 25 },
  { name: 'Vespa II', category: 'Drones', jitaPrice: 450000, localMultiplier: 1.20, volume: 25 },
  { name: 'Hammerhead II', category: 'Drones', jitaPrice: 650000, localMultiplier: 1.18, volume: 25 },
  { name: 'Curator II', category: 'Drones', jitaPrice: 800000, localMultiplier: 1.15, volume: 25 },
  { name: 'Nanite Repair Paste', category: 'Consumables', jitaPrice: 18000, localMultiplier: 1.30, volume: 0.01 },
  { name: 'Synth Mindflood', category: 'Boosters', jitaPrice: 500000, localMultiplier: 1.50, volume: 1 },
  { name: 'Standard Mindflood', category: 'Boosters', jitaPrice: 2500000, localMultiplier: 1.40, volume: 1 },
  { name: 'Isotopes (Any)', category: 'Fuel', jitaPrice: 18000, localMultiplier: 1.25, volume: 0.15 },
  { name: 'Strontium Clathrates', category: 'Fuel', jitaPrice: 1200, localMultiplier: 1.30, volume: 3 },
];

db.exec(`
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

  CREATE TABLE IF NOT EXISTS trade_settings (
    discord_user_id TEXT PRIMARY KEY,
    nullsec_discount REAL DEFAULT 0.10,
    jf_rate_per_m3 REAL DEFAULT 1500,
    profit_threshold REAL DEFAULT 10000000,
    preferred_hub TEXT DEFAULT 'D-PN',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'import': await handleImport(interaction); break;
    case 'stations': await handleStations(interaction); break;
    case 'bestimports': await handleBestImports(interaction); break;
    case 'sellorders': await handleSellOrders(interaction); break;
    case 'orders': await handleOrders(interaction); break;
    case 'flip': await handleFlip(interaction); break;
  }
}

async function handleImport(interaction: CommandInteraction) {
  const item = interaction.options.get('item')?.value as string;
  const quantity = interaction.options.get('quantity')?.value as number;
  const jitaBuy = interaction.options.get('jita_buy')?.value as number;
  const localSell = interaction.options.get('local_sell')?.value as number;
  const volume = interaction.options.get('volume')?.value as number;
  
  const settings = getSettings(interaction.user.id);
  const totalVolume = volume * quantity;
  const jfCost = totalVolume * settings.jf_rate_per_m3;
  const totalBuyCost = jitaBuy * quantity;
  const totalRevenue = localSell * quantity * (1 - settings.nullsec_discount);
  const profit = totalRevenue - totalBuyCost - jfCost;
  const margin = (profit / totalBuyCost) * 100;
  
  const isProfitable = profit > settings.profit_threshold;
  
  const embed = new EmbedBuilder()
    .setTitle(`Import Analysis: ${item}`)
    .setColor(isProfitable ? 0x00ff00 : 0xff0000)
    .addFields(
      { name: 'Quantity', value: quantity.toLocaleString(), inline: true },
      { name: 'Volume', value: `${totalVolume.toLocaleString()} m³`, inline: true },
      { name: 'JF Cost', value: `${jfCost.toLocaleString()} ISK`, inline: true },
      { name: 'Jita Buy (Total)', value: `${totalBuyCost.toLocaleString()} ISK`, inline: true },
      { name: 'Jita Buy (Unit)', value: `${jitaBuy.toLocaleString()} ISK`, inline: true },
      { name: 'Local Sell (Unit)', value: `${localSell.toLocaleString()} ISK`, inline: true },
      { name: 'Nullsec Discount', value: `${(settings.nullsec_discount * 100).toFixed(0)}%`, inline: true },
      { name: 'Revenue After Discount', value: `${totalRevenue.toLocaleString()} ISK`, inline: true },
      { name: 'Total Cost', value: `${(totalBuyCost + jfCost).toLocaleString()} ISK`, inline: true }
    )
    .addFields({ name: 'PROFIT', value: `${profit.toLocaleString()} ISK (${margin.toFixed(1)}%)`, inline: false })
    .setFooter({ text: isProfitable ? '✓ PROFITABLE - Good import!' : '✗ NOT PROFITABLE - Skip this' });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleStations(interaction: CommandInteraction) {
  const embed = new EmbedBuilder()
    .setTitle('WinterCo Trading Hubs')
    .setColor(0x3498db)
    .setDescription('Recommended stations for buying/selling')
    .addFields(
      { 
        name: 'Primary Hubs', 
        value: WINTERCO_HUBS.filter(h => h.type === 'Primary Hub' || h.type === 'JF Hub')
          .map(h => `**${h.name}** (${h.system})\nDiscount: ${(h.discount * 100).toFixed(0)}%`)
          .join('\n\n'),
        inline: false 
      },
      { 
        name: 'Industry Hub', 
        value: '**RD-G2R**\nBest for: Materials, PI products\nDiscount: 5% (materials moved here)',
        inline: true 
      },
      { 
        name: 'Regional Markets', 
        value: WINTERCO_HUBS.filter(h => h.type === 'Regional')
          .map(h => `${h.system} (${(h.discount * 100).toFixed(0)}% discount)`)
          .join('\n'),
        inline: true 
      }
    )
    .addFields({ 
      name: 'Buying Strategy', 
      value: '• Buy materials at RD-G2R (5% discount)\n• Buy ships/modules at D-PN or VA6-ED\n• Import from Jita for 15%+ margins' 
    });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleBestImports(interaction: CommandInteraction) {
  const settings = getSettings(interaction.user.id);
  
  const analyzed = BEST_IMPORTS.map(item => {
    const localPrice = item.jitaPrice * item.localMultiplier;
    const profit = (localPrice * (1 - settings.nullsec_discount)) - item.jitaPrice - (item.volume * settings.jf_rate_per_m3);
    const margin = (profit / item.jitaPrice) * 100;
    return { ...item, localPrice, profit, margin };
  }).sort((a, b) => b.margin - a.margin);
  
  const embed = new EmbedBuilder()
    .setTitle('Best Items to Import from Jita')
    .setColor(0x00ff00)
    .setDescription(
      analyzed.slice(0, 15).map((item, i) => 
        `**${i + 1}. ${item.name}** (${item.category})\n` +
        `   Jita: ${item.jitaPrice.toLocaleString()} → Local: ${item.localPrice.toLocaleString()}\n` +
        `   Profit/unit: ${item.profit.toLocaleString()} ISK (${item.margin.toFixed(1)}%)`
      ).join('\n\n')
    )
    .setFooter({ text: `Based on ${settings.nullsec_discount * 100}% nullsec discount` });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleSellOrders(interaction: CommandInteraction) {
  const item = interaction.options.get('item')?.value as string;
  const quantity = interaction.options.get('quantity')?.value as number;
  const buyPrice = interaction.options.get('buy_price')?.value as number;
  const sellPrice = interaction.options.get('sell_price')?.value as number;
  const station = interaction.options.get('station')?.value as string;
  
  const stmt = db.prepare(`
    INSERT INTO sell_orders (discord_user_id, item_name, quantity, buy_price, sell_price, station)
    VALUES (?, ?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(interaction.user.id, item, quantity, buyPrice, sellPrice, station);
  
  const potentialProfit = (sellPrice * quantity) - buyPrice;
  
  const embed = new EmbedBuilder()
    .setTitle('Sell Order Tracked')
    .setColor(0x00ff00)
    .addFields(
      { name: 'ID', value: result.lastInsertRowid.toString(), inline: true },
      { name: 'Item', value: `${item} x${quantity}`, inline: true },
      { name: 'Station', value: station, inline: true },
      { name: 'Total Invested', value: `${buyPrice.toLocaleString()} ISK`, inline: true },
      { name: 'Sell Price/Unit', value: `${sellPrice.toLocaleString()} ISK`, inline: true },
      { name: 'Potential Profit', value: `${potentialProfit.toLocaleString()} ISK`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleOrders(interaction: CommandInteraction) {
  const orders = db.prepare(`
    SELECT * FROM sell_orders 
    WHERE discord_user_id = ? AND status = 'active'
    ORDER BY created_at DESC
  `).all(interaction.user.id) as {
    id: number;
    item_name: string;
    quantity: number;
    buy_price: number;
    sell_price: number;
    station: string;
    sold_quantity: number;
  }[];
  
  if (orders.length === 0) {
    await interaction.reply({ content: 'No active sell orders.', ephemeral: true });
    return;
  }
  
  let totalInvested = 0;
  let totalValue = 0;
  
  const embed = new EmbedBuilder()
    .setTitle('Your Active Sell Orders')
    .setColor(0x3498db)
    .setDescription(
      orders.map(o => {
        const invested = o.buy_price;
        const value = o.sell_price * o.quantity;
        totalInvested += invested;
        totalValue += value;
        return `**#${o.id}** | ${o.item_name} x${o.quantity} @ ${o.station}\n` +
               `   Invested: ${invested.toLocaleString()} | Value: ${value.toLocaleString()}`;
      }).join('\n\n')
    )
    .addFields(
      { name: 'Total Invested', value: `${totalInvested.toLocaleString()} ISK`, inline: true },
      { name: 'Total Value', value: `${totalValue.toLocaleString()} ISK`, inline: true },
      { name: 'Potential Profit', value: `${(totalValue - totalInvested).toLocaleString()} ISK`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleFlip(interaction: CommandInteraction) {
  const item = interaction.options.get('item')?.value as string;
  const quantity = interaction.options.get('quantity')?.value as number;
  const buyPrice = interaction.options.get('buy_price')?.value as number;
  const sellPrice = interaction.options.get('sell_price')?.value as number;
  
  const totalCost = buyPrice * quantity;
  const totalRevenue = sellPrice * quantity;
  const profit = totalRevenue - totalCost;
  const margin = (profit / totalCost) * 100;
  
  const embed = new EmbedBuilder()
    .setTitle(`Station Flip Analysis: ${item}`)
    .setColor(profit > 0 ? 0x00ff00 : 0xff0000)
    .addFields(
      { name: 'Buy Price/Unit', value: `${buyPrice.toLocaleString()} ISK`, inline: true },
      { name: 'Sell Price/Unit', value: `${sellPrice.toLocaleString()} ISK`, inline: true },
      { name: 'Spread', value: `${((sellPrice - buyPrice) / buyPrice * 100).toFixed(1)}%`, inline: true },
      { name: 'Total Cost', value: `${totalCost.toLocaleString()} ISK`, inline: true },
      { name: 'Total Revenue', value: `${totalRevenue.toLocaleString()} ISK`, inline: true },
      { name: 'PROFIT', value: `${profit.toLocaleString()} ISK (${margin.toFixed(1)}%)`, inline: true }
    )
    .setFooter({ text: profit > 0 ? '✓ Good flip opportunity!' : '✗ Margins too tight' });
  
  await interaction.reply({ embeds: [embed] });
}

function getSettings(userId: string): { nullsec_discount: number; jf_rate_per_m3: number; profit_threshold: number; preferred_hub: string } {
  const settings = db.prepare('SELECT * FROM trade_settings WHERE discord_user_id = ?')
    .get(userId) as { 
      nullsec_discount: number; 
      jf_rate_per_m3: number; 
      profit_threshold: number; 
      preferred_hub: string;
    } | undefined;
  
  if (settings) {
    return settings;
  }
  
  db.prepare(`
    INSERT INTO trade_settings (discord_user_id)
    VALUES (?)
  `).run(userId);
  
  return {
    nullsec_discount: 0.10,
    jf_rate_per_m3: 1500,
    profit_threshold: 10000000,
    preferred_hub: 'D-PN'
  };
}
