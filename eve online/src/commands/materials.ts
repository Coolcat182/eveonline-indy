import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';

export const data = new SlashCommandBuilder()
  .setName('materials')
  .setDescription('Material buying and management')
  .addSubcommand(sub =>
    sub
      .setName('buy')
      .setDescription('Record a material purchase')
      .addStringOption(opt => opt.setName('item').setDescription('Material name').setRequired(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity').setRequired(true))
      .addNumberOption(opt => opt.setName('price').setDescription('Total price paid').setRequired(true))
      .addStringOption(opt => opt.setName('station').setDescription('Purchase station').setRequired(true))
      .addStringOption(opt => opt.setName('destination').setDescription('Where to use it').addChoices(
        { name: 'RD-G2R (5% discount)', value: 'RD-G2R' },
        { name: 'D-PN (10% discount)', value: 'D-PN' },
        { name: 'VA6-ED (8% discount)', value: 'VA6-ED' },
        { name: 'Local Use', value: 'local' }
      ).setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('inventory')
      .setDescription('View your material inventory')
      .addStringOption(opt => opt.setName('location').setDescription('Filter by location').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('value')
      .setDescription('Calculate total value of your materials'))
  .addSubcommand(sub =>
    sub
      .setName('sell')
      .setDescription('Sell materials from inventory')
      .addIntegerOption(opt => opt.setName('id').setDescription('Material ID').setRequired(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity to sell').setRequired(true))
      .addNumberOption(opt => opt.setName('price').setDescription('Sell price per unit').setRequired(true)))
  .addSubcommand(sub =>
    sub
      .setName('needed')
      .setDescription('List materials needed for pending jobs'))
  .addSubcommand(sub =>
    sub
      .setName('stations')
      .setDescription('Best stations to buy materials'))
  .addSubcommand(sub =>
    sub
      .setName('salvage')
      .setDescription('Buy salvage materials')
      .addStringOption(opt => opt.setName('type').setDescription('Salvage type').setRequired(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity').setRequired(true))
      .addNumberOption(opt => opt.setName('price').setDescription('Price per unit').setRequired(true))
      .addStringOption(opt => opt.setName('station').setDescription('Station').setRequired(true)));

const MATERIAL_STATIONS = [
  { name: 'RD-G2R', discount: 0.05, notes: 'Best for bulk materials, PI products' },
  { name: 'D-PN', discount: 0.10, notes: 'Primary hub, good variety' },
  { name: 'VA6-ED', discount: 0.08, notes: 'JF hub, imported goods' },
  { name: 'Jita', discount: 0, notes: 'Lowest prices, add JF cost' },
];

const SALVAGE_PRICES: Record<string, number> = {
  'Alloyed Tritanium Bar': 85000,
  'Armor Plates': 45000,
  'Broken Drone Transmitter': 15000,
  'Burned Logic Circuit': 5000,
  'Capacitor Console': 180000,
  'Charred Micro Circuit': 8000,
  'Conductive Polymer': 25000,
  'Contaminated Nanite Compound': 35000,
  'Current Pump': 15000,
  'Damaged Artificial Neural Network': 45000,
  'Defective Current Pump': 8000,
  'Drone Transceiver': 12000,
  'Fried Interface Circuit': 4000,
  'Input-Console': 22000,
  'Logic Circuit': 12000,
  'Melted Capacitor Console': 95000,
  'Power Circuit': 18000,
  'Power Conduit': 28000,
  'Processors': 55000,
  'Program/Database': 18000,
  'Scorched Telemetry Processor': 6000,
  'Silicon Glass': 12000,
  'Tangled Cybernetic Strand': 35000,
  'Telemetry Processor': 25000,
  'Temperature Sensor': 20000,
  'Thruster Console': 35000,
  'Tripped Power Circuit': 6000,
  'Tube Fitting': 10000,
  'Ward Console': 45000,
};

const INDUSTRY_MATERIALS: Record<string, { price: number; volume: number }> = {
  'Isogen': { price: 120, volume: 0.01 },
  'Mexallon': { price: 85, volume: 0.01 },
  'Nocxium': { price: 450, volume: 0.01 },
  'Pyerite': { price: 12, volume: 0.01 },
  'Tritanium': { price: 6, volume: 0.01 },
  'Zydrine': { price: 1200, volume: 0.01 },
  'Megacyte': { price: 2800, volume: 0.01 },
  'Morphite': { price: 8500, volume: 0.01 },
  'Construction Blocks': { price: 480, volume: 0.38 },
  'Nanotransistors': { price: 12000, volume: 0.1 },
  'Sylramic Fibers': { price: 2200, volume: 0.08 },
  'Fullerides': { price: 15000, volume: 0.08 },
  'Fermionic Condensates': { price: 350000, volume: 0.8 },
  'Hypersynaptic Fibers': { price: 55000, volume: 0.5 },
  'Phenolic Composites': { price: 18000, volume: 0.3 },
  'Tungsten Carbide': { price: 2800, volume: 0.04 },
  'Titanium Carbide': { price: 3200, volume: 0.04 },
  'Crystalline Carbonide': { price: 3500, volume: 0.04 },
  'Fernite Carbide': { price: 3000, volume: 0.04 },
  'Platinum Technite': { price: 8500, volume: 0.04 },
  'Caesarium Cadmide': { price: 9500, volume: 0.04 },
  'Solerium': { price: 11000, volume: 0.04 },
  'Dysporite': { price: 45000, volume: 0.04 },
  'Ferrofluid': { price: 28000, volume: 0.04 },
  'Hyperflurite': { price: 35000, volume: 0.04 },
  'Neo Mercurite': { price: 12000, volume: 0.04 },
  'Thulium Hafnite': { price: 18000, volume: 0.04 },
  'Promethium Mercurite': { price: 32000, volume: 0.04 },
  'Fermium Hafnite': { price: 22000, volume: 0.04 },
  'Dysprosium Cadmide': { price: 55000, volume: 0.04 },
};

db.exec(`
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

  CREATE TABLE IF NOT EXISTS material_sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    sell_price REAL NOT NULL,
    profit REAL,
    sold_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventory_id) REFERENCES material_inventory(id)
  );
`);

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'buy': await handleBuy(interaction); break;
    case 'inventory': await handleInventory(interaction); break;
    case 'value': await handleValue(interaction); break;
    case 'sell': await handleSell(interaction); break;
    case 'needed': await handleNeeded(interaction); break;
    case 'stations': await handleStations(interaction); break;
    case 'salvage': await handleSalvage(interaction); break;
  }
}

async function handleBuy(interaction: CommandInteraction) {
  const item = interaction.options.get('item')?.value as string;
  const quantity = interaction.options.get('quantity')?.value as number;
  const price = interaction.options.get('price')?.value as number;
  const station = interaction.options.get('station')?.value as string;
  const destination = (interaction.options.get('destination')?.value as string) || 'local';
  
  const discount = getDiscount(destination);
  const adjustedPrice = price * (1 - discount);
  
  const stmt = db.prepare(`
    INSERT INTO material_inventory 
    (discord_user_id, item_name, quantity, original_quantity, buy_price, station, destination, discount_applied)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(
    interaction.user.id,
    item,
    quantity,
    quantity,
    adjustedPrice,
    station,
    destination,
    discount
  );
  
  const pricePerUnit = adjustedPrice / quantity;
  
  const embed = new EmbedBuilder()
    .setTitle('Material Purchased')
    .setColor(0x00ff00)
    .addFields(
      { name: 'ID', value: result.lastInsertRowid.toString(), inline: true },
      { name: 'Item', value: `${item} x${quantity}`, inline: true },
      { name: 'Station', value: station, inline: true },
      { name: 'Original Price', value: `${price.toLocaleString()} ISK`, inline: true },
      { name: 'Discount', value: `${(discount * 100).toFixed(0)}%`, inline: true },
      { name: 'Adjusted Price', value: `${adjustedPrice.toLocaleString()} ISK`, inline: true },
      { name: 'Price/Unit', value: `${pricePerUnit.toLocaleString()} ISK`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleInventory(interaction: CommandInteraction) {
  const location = interaction.options.get('location')?.value as string | undefined;
  
  let query = 'SELECT * FROM material_inventory WHERE discord_user_id = ? AND quantity > 0';
  const params: string[] = [interaction.user.id];
  
  if (location) {
    query += ' AND (station = ? OR destination = ?)';
    params.push(location, location);
  }
  
  query += ' ORDER BY item_name';
  
  const materials = db.prepare(query).all(...params) as {
    id: number;
    item_name: string;
    quantity: number;
    buy_price: number;
    station: string;
    destination: string;
  }[];
  
  if (materials.length === 0) {
    await interaction.reply({ content: 'No materials in inventory.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Material Inventory')
    .setColor(0x3498db)
    .setDescription(
      materials.map(m => 
        `**#${m.id}** | ${m.item_name} x${m.quantity}\n` +
        `   Cost: ${(m.buy_price / m.quantity).toLocaleString()}/unit | Location: ${m.station}`
      ).join('\n')
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleValue(interaction: CommandInteraction) {
  const materials = db.prepare(`
    SELECT item_name, quantity, buy_price, station 
    FROM material_inventory 
    WHERE discord_user_id = ? AND quantity > 0
  `).all(interaction.user.id) as {
    item_name: string;
    quantity: number;
    buy_price: number;
    station: string;
  }[];
  
  if (materials.length === 0) {
    await interaction.reply({ content: 'No materials in inventory.', ephemeral: true });
    return;
  }
  
  const totalValue = materials.reduce((sum, m) => sum + m.buy_price, 0);
  const byStation: Record<string, { count: number; value: number }> = {};
  
  for (const m of materials) {
    if (!byStation[m.station]) {
      byStation[m.station] = { count: 0, value: 0 };
    }
    byStation[m.station].count += m.quantity;
    byStation[m.station].value += m.buy_price;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Material Inventory Value')
    .setColor(0xf1c40f)
    .addFields(
      { name: 'Total Items', value: materials.length.toString(), inline: true },
      { name: 'Total Units', value: materials.reduce((s, m) => s + m.quantity, 0).toLocaleString(), inline: true },
      { name: 'Total Value', value: `${totalValue.toLocaleString()} ISK`, inline: true }
    )
    .addFields({ name: 'By Station', value: Object.entries(byStation)
      .map(([station, data]) => `**${station}**: ${data.count.toLocaleString()} units (${data.value.toLocaleString()} ISK)`)
      .join('\n') });
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleSell(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  const quantity = interaction.options.get('quantity')?.value as number;
  const sellPrice = interaction.options.get('price')?.value as number;
  
  const material = db.prepare(`
    SELECT * FROM material_inventory 
    WHERE id = ? AND discord_user_id = ? AND quantity >= ?
  `).get(id, interaction.user.id, quantity) as {
    item_name: string;
    quantity: number;
    buy_price: number;
  } | undefined;
  
  if (!material) {
    await interaction.reply({ content: 'Material not found or insufficient quantity.', ephemeral: true });
    return;
  }
  
  const costBasis = (material.buy_price / material.quantity) * quantity;
  const totalRevenue = sellPrice * quantity;
  const profit = totalRevenue - costBasis;
  const margin = (profit / costBasis) * 100;
  
  db.prepare(`
    INSERT INTO material_sales (inventory_id, quantity, sell_price, profit)
    VALUES (?, ?, ?, ?)
  `).run(id, quantity, totalRevenue, profit);
  
  db.prepare(`
    UPDATE material_inventory SET quantity = quantity - ? WHERE id = ?
  `).run(quantity, id);
  
  const embed = new EmbedBuilder()
    .setTitle('Material Sold')
    .setColor(profit >= 0 ? 0x00ff00 : 0xff0000)
    .addFields(
      { name: 'Item', value: `${material.item_name} x${quantity}`, inline: true },
      { name: 'Cost Basis', value: `${costBasis.toLocaleString()} ISK`, inline: true },
      { name: 'Revenue', value: `${totalRevenue.toLocaleString()} ISK`, inline: true },
      { name: 'Profit', value: `${profit.toLocaleString()} ISK`, inline: true },
      { name: 'Margin', value: `${margin.toFixed(1)}%`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleNeeded(interaction: CommandInteraction) {
  const jobs = db.prepare(`
    SELECT product_name, quantity, material_cost 
    FROM industry_jobs 
    WHERE discord_user_id = ? AND status IN ('pending', 'building')
  `).all(interaction.user.id) as { product_name: string; quantity: number; material_cost: number }[];
  
  if (jobs.length === 0) {
    await interaction.reply({ content: 'No pending jobs requiring materials.', ephemeral: true });
    return;
  }
  
  const inventory = db.prepare(`
    SELECT item_name, quantity 
    FROM material_inventory 
    WHERE discord_user_id = ? AND quantity > 0
  `).all(interaction.user.id) as { item_name: string; quantity: number }[];
  
  const totalCost = jobs.reduce((sum, j) => sum + j.material_cost, 0);
  
  const embed = new EmbedBuilder()
    .setTitle('Materials Needed for Pending Jobs')
    .setColor(0xf1c40f)
    .setDescription(
      jobs.map(j => `**${j.product_name}** x${j.quantity}: ${j.material_cost.toLocaleString()} ISK`).join('\n')
    )
    .addFields(
      { name: 'Total Material Cost', value: `${totalCost.toLocaleString()} ISK`, inline: true },
      { name: 'Jobs Pending', value: jobs.length.toString(), inline: true }
    )
    .setFooter({ text: 'Buy materials at RD-G2R for 5% discount' });
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleStations(interaction: CommandInteraction) {
  const embed = new EmbedBuilder()
    .setTitle('Best Stations to Buy Materials')
    .setColor(0x3498db)
    .setDescription(
      MATERIAL_STATIONS.map(s => 
        `**${s.name}**${s.discount > 0 ? ` (${(s.discount * 100).toFixed(0)}% discount)` : ''}\n${s.notes}`
      ).join('\n\n')
    )
    .addFields({ 
      name: 'Recommendation', 
      value: '• Buy bulk at RD-G2R for cheapest materials\n• Import specialty items from Jita\n• Use local salvage for rig production' 
    });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleSalvage(interaction: CommandInteraction) {
  const type = interaction.options.get('type')?.value as string;
  const quantity = interaction.options.get('quantity')?.value as number;
  const price = interaction.options.get('price')?.value as number;
  const station = interaction.options.get('station')?.value as string;
  
  const marketPrice = SALVAGE_PRICES[type] || 0;
  const totalPrice = price * quantity;
  const discount = getDiscount(station);
  const adjustedPrice = totalPrice * (1 - discount);
  
  const isGoodDeal = marketPrice > 0 && price <= marketPrice * 1.1;
  
  const stmt = db.prepare(`
    INSERT INTO material_inventory 
    (discord_user_id, item_name, quantity, original_quantity, buy_price, station, destination, discount_applied)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(
    interaction.user.id,
    `Salvage: ${type}`,
    quantity,
    quantity,
    adjustedPrice,
    station,
    station,
    discount
  );
  
  const embed = new EmbedBuilder()
    .setTitle('Salvage Purchased')
    .setColor(isGoodDeal ? 0x00ff00 : 0xff0000)
    .addFields(
      { name: 'Type', value: type, inline: true },
      { name: 'Quantity', value: quantity.toString(), inline: true },
      { name: 'Station', value: station, inline: true },
      { name: 'Your Price', value: `${price.toLocaleString()} ISK/unit`, inline: true },
      { name: 'Market Price', value: marketPrice > 0 ? `${marketPrice.toLocaleString()} ISK/unit` : 'Unknown', inline: true },
      { name: 'Total', value: `${adjustedPrice.toLocaleString()} ISK`, inline: true }
    )
    .setFooter({ text: isGoodDeal ? '✓ Good deal!' : 'Check market price before buying more' });
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

function getDiscount(location: string): number {
  const station = MATERIAL_STATIONS.find(s => s.name === location);
  return station?.discount || 0;
}
