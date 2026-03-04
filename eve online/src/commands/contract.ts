import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';

export const data = new SlashCommandBuilder()
  .setName('contract')
  .setDescription('Create and manage buy/sell contracts')
  .addSubcommand(sub =>
    sub
      .setName('buy')
      .setDescription('Create a buy contract (you want to buy something)')
      .addStringOption(opt => opt.setName('item').setDescription('Item name').setRequired(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity wanted').setRequired(true))
      .addNumberOption(opt => opt.setName('price').setDescription('Price per unit (ISK)').setRequired(true))
      .addStringOption(opt => opt.setName('station').setDescription('Delivery station').setRequired(true))
      .addStringOption(opt => opt.setName('notes').setDescription('Additional notes').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('sell')
      .setDescription('Create a sell contract (you want to sell something)')
      .addStringOption(opt => opt.setName('item').setDescription('Item name').setRequired(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity available').setRequired(true))
      .addNumberOption(opt => opt.setName('price').setDescription('Price per unit (ISK)').setRequired(true))
      .addStringOption(opt => opt.setName('station').setDescription('Pickup station').setRequired(true))
      .addStringOption(opt => opt.setName('notes').setDescription('Additional notes').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('list')
      .setDescription('List active contracts')
      .addStringOption(opt => opt.setName('type').setDescription('Contract type').addChoices(
        { name: 'Buy Contracts', value: 'buy' },
        { name: 'Sell Contracts', value: 'sell' },
        { name: 'All', value: 'all' }
      ).setRequired(false))
      .addStringOption(opt => opt.setName('station').setDescription('Filter by station').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('my')
      .setDescription('View your contracts'))
  .addSubcommand(sub =>
    sub
      .setName('fulfill')
      .setDescription('Mark a contract as fulfilled/complete')
      .addIntegerOption(opt => opt.setName('id').setDescription('Contract ID').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('cancel')
      .setDescription('Cancel your contract')
      .addIntegerOption(opt => opt.setName('id').setDescription('Contract ID').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('search')
      .setDescription('Search for contracts by item')
      .addStringOption(opt => opt.setName('item').setDescription('Item name to search').setRequired(true)));

interface Contract {
  id?: number;
  discord_user_id: string;
  character_name: string;
  contract_type: 'buy' | 'sell';
  item_name: string;
  quantity: number;
  price_per_unit: number;
  total_value: number;
  station: string;
  status: 'active' | 'fulfilled' | 'cancelled';
  created_at?: string;
  fulfilled_at?: string;
  notes?: string;
}

db.exec(`
  CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id TEXT NOT NULL,
    character_name TEXT,
    contract_type TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price_per_unit REAL NOT NULL,
    total_value REAL NOT NULL,
    station TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    fulfilled_at DATETIME,
    notes TEXT
  );
`);

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'buy': await handleBuy(interaction); break;
    case 'sell': await handleSell(interaction); break;
    case 'list': await handleList(interaction); break;
    case 'my': await handleMy(interaction); break;
    case 'fulfill': await handleFulfill(interaction); break;
    case 'cancel': await handleCancel(interaction); break;
    case 'search': await handleSearch(interaction); break;
  }
}

async function handleBuy(interaction: CommandInteraction) {
  const item = interaction.options.get('item')?.value as string;
  const quantity = interaction.options.get('quantity')?.value as number;
  const price = interaction.options.get('price')?.value as number;
  const station = interaction.options.get('station')?.value as string;
  const notes = (interaction.options.get('notes')?.value as string) || '';
  
  const totalValue = price * quantity;
  
  const stmt = db.prepare(`
    INSERT INTO contracts 
    (discord_user_id, contract_type, item_name, quantity, price_per_unit, total_value, station, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(
    interaction.user.id,
    'buy',
    item,
    quantity,
    price,
    totalValue,
    station,
    notes
  );
  
  const embed = new EmbedBuilder()
    .setTitle('Buy Contract Created')
    .setColor(0x00ff00)
    .addFields(
      { name: 'Contract ID', value: result.lastInsertRowid.toString(), inline: true },
      { name: 'Type', value: 'BUY', inline: true },
      { name: 'Status', value: 'Active', inline: true },
      { name: 'Item', value: item, inline: true },
      { name: 'Quantity', value: quantity.toLocaleString(), inline: true },
      { name: 'Price/Unit', value: `${price.toLocaleString()} ISK`, inline: true },
      { name: 'Total Value', value: `${totalValue.toLocaleString()} ISK`, inline: true },
      { name: 'Delivery Station', value: station, inline: true }
    );
  
  if (notes) embed.addFields({ name: 'Notes', value: notes, inline: false });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleSell(interaction: CommandInteraction) {
  const item = interaction.options.get('item')?.value as string;
  const quantity = interaction.options.get('quantity')?.value as number;
  const price = interaction.options.get('price')?.value as number;
  const station = interaction.options.get('station')?.value as string;
  const notes = (interaction.options.get('notes')?.value as string) || '';
  
  const totalValue = price * quantity;
  
  const stmt = db.prepare(`
    INSERT INTO contracts 
    (discord_user_id, contract_type, item_name, quantity, price_per_unit, total_value, station, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(
    interaction.user.id,
    'sell',
    item,
    quantity,
    price,
    totalValue,
    station,
    notes
  );
  
  const embed = new EmbedBuilder()
    .setTitle('Sell Contract Created')
    .setColor(0x3498db)
    .addFields(
      { name: 'Contract ID', value: result.lastInsertRowid.toString(), inline: true },
      { name: 'Type', value: 'SELL', inline: true },
      { name: 'Status', value: 'Active', inline: true },
      { name: 'Item', value: item, inline: true },
      { name: 'Quantity', value: quantity.toLocaleString(), inline: true },
      { name: 'Price/Unit', value: `${price.toLocaleString()} ISK`, inline: true },
      { name: 'Total Value', value: `${totalValue.toLocaleString()} ISK`, inline: true },
      { name: 'Pickup Station', value: station, inline: true }
    );
  
  if (notes) embed.addFields({ name: 'Notes', value: notes, inline: false });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleList(interaction: CommandInteraction) {
  const type = (interaction.options.get('type')?.value as string) || 'all';
  const station = interaction.options.get('station')?.value as string | undefined;
  
  let query = 'SELECT * FROM contracts WHERE status = ?';
  const params: (string | number)[] = ['active'];
  
  if (type !== 'all') {
    query += ' AND contract_type = ?';
    params.push(type);
  }
  
  if (station) {
    query += ' AND station = ?';
    params.push(station);
  }
  
  query += ' ORDER BY created_at DESC LIMIT 20';
  
  const contracts = db.prepare(query).all(...params) as Contract[];
  
  if (contracts.length === 0) {
    await interaction.reply({ content: 'No active contracts found.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Active Contracts')
    .setColor(0xf1c40f)
    .setDescription(
      contracts.map(c => 
        `**#${c.id}** | ${c.contract_type.toUpperCase()} | ${c.item_name} x${c.quantity.toLocaleString()}\n` +
        `   ${c.price_per_unit.toLocaleString()} ISK/unit | ${c.station} | Total: ${c.total_value.toLocaleString()} ISK`
      ).join('\n\n')
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleMy(interaction: CommandInteraction) {
  const contracts = db.prepare(`
    SELECT * FROM contracts 
    WHERE discord_user_id = ? 
    ORDER BY created_at DESC 
    LIMIT 15
  `).all(interaction.user.id) as Contract[];
  
  if (contracts.length === 0) {
    await interaction.reply({ content: 'You have no contracts.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Your Contracts')
    .setColor(0x9b59b6)
    .setDescription(
      contracts.map(c => 
        `**#${c.id}** | ${c.contract_type.toUpperCase()} | **${c.status.toUpperCase()}**\n` +
        `${c.item_name} x${c.quantity.toLocaleString()} @ ${c.price_per_unit.toLocaleString()} ISK | ${c.station}`
      ).join('\n\n')
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleFulfill(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  
  const stmt = db.prepare(`
    UPDATE contracts 
    SET status = 'fulfilled', fulfilled_at = CURRENT_TIMESTAMP 
    WHERE id = ? AND discord_user_id = ? AND status = 'active'
  `);
  
  const result = stmt.run(id, interaction.user.id);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'Contract not found, not yours, or already fulfilled.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `Contract #${id} marked as fulfilled.`, ephemeral: true });
}

async function handleCancel(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  
  const stmt = db.prepare(`
    UPDATE contracts 
    SET status = 'cancelled' 
    WHERE id = ? AND discord_user_id = ? AND status = 'active'
  `);
  
  const result = stmt.run(id, interaction.user.id);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'Contract not found, not yours, or already cancelled.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `Contract #${id} cancelled.`, ephemeral: true });
}

async function handleSearch(interaction: CommandInteraction) {
  const item = interaction.options.get('item')?.value as string;
  
  const contracts = db.prepare(`
    SELECT * FROM contracts 
    WHERE item_name LIKE ? AND status = 'active'
    ORDER BY price_per_unit ASC
    LIMIT 20
  `).all(`%${item}%`) as Contract[];
  
  if (contracts.length === 0) {
    await interaction.reply({ content: `No contracts found for "${item}".`, ephemeral: true });
    return;
  }
  
  const buyContracts = contracts.filter(c => c.contract_type === 'buy');
  const sellContracts = contracts.filter(c => c.contract_type === 'sell');
  
  let description = '';
  
  if (sellContracts.length > 0) {
    description += '**SELL CONTRACTS:**\n';
    description += sellContracts.map(c => 
      `#${c.id}: ${c.item_name} x${c.quantity.toLocaleString()} @ ${c.price_per_unit.toLocaleString()} ISK | ${c.station}`
    ).join('\n');
    description += '\n\n';
  }
  
  if (buyContracts.length > 0) {
    description += '**BUY CONTRACTS:**\n';
    description += buyContracts.map(c => 
      `#${c.id}: ${c.item_name} x${c.quantity.toLocaleString()} @ ${c.price_per_unit.toLocaleString()} ISK | ${c.station}`
    ).join('\n');
  }
  
  const embed = new EmbedBuilder()
    .setTitle(`Search Results: "${item}"`)
    .setColor(0x2ecc71)
    .setDescription(description);
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}
