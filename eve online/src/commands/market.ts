import { SlashCommandBuilder, CommandInteraction, EmbedBuilder, AutocompleteInteraction } from 'discord.js';
import db from '../database/setup';
import { MarketOrder } from '../types';
import { searchType, getJitaPrices } from '../services/esi';

export const data = new SlashCommandBuilder()
  .setName('market')
  .setDescription('Market tools and price checking')
  .addSubcommand(sub =>
    sub
      .setName('price')
      .setDescription('Check Jita prices for an item')
      .addStringOption(opt => opt.setName('item').setDescription('Item name or type ID').setRequired(true).setAutocomplete(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('add')
      .setDescription('Track a market order')
      .addStringOption(opt => opt.setName('item').setDescription('Item name').setRequired(true).setAutocomplete(true))
      .addStringOption(opt => opt.setName('location').setDescription('Location').setRequired(true))
      .addIntegerOption(opt => opt.setName('volume').setDescription('Volume').setRequired(true))
      .addNumberOption(opt => opt.setName('buy_price').setDescription('Buy price').setRequired(false))
      .addNumberOption(opt => opt.setName('sell_price').setDescription('Target sell price').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('orders')
      .setDescription('List your tracked orders')
      .addStringOption(opt => opt.setName('status').setDescription('Filter by status').addChoices(
        { name: 'Active', value: 'active' },
        { name: 'Filled', value: 'filled' },
        { name: 'All', value: 'all' }
      ).setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('margin')
      .setDescription('Calculate profit margin')
      .addNumberOption(opt => opt.setName('buy').setDescription('Buy price').setRequired(true))
      .addNumberOption(opt => opt.setName('sell').setDescription('Sell price').setRequired(true))
      .addIntegerOption(opt => opt.setName('volume').setDescription('Volume').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('compare')
      .setDescription('Compare prices for an item')
      .addStringOption(opt => opt.setName('item').setDescription('Item name').setRequired(true).setAutocomplete(true))
      .addNumberOption(opt => opt.setName('your_price').setDescription('Your buy price').setRequired(true)));

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'price':
      await handlePrice(interaction);
      break;
    case 'add':
      await handleAdd(interaction);
      break;
    case 'orders':
      await handleOrders(interaction);
      break;
    case 'margin':
      await handleMargin(interaction);
      break;
    case 'compare':
      await handleCompare(interaction);
      break;
  }
}

async function handlePrice(interaction: CommandInteraction) {
  const itemInput = interaction.options.get('item')?.value as string;
  
  await interaction.deferReply();
  
  const typeId = parseInt(itemInput);
  let itemName = itemInput;
  let productId = 0;
  
  if (!isNaN(typeId)) {
    const searchResults = await searchType(itemInput);
    if (searchResults.length > 0) {
      itemName = searchResults[0].name;
      productId = searchResults[0].id;
    }
  } else {
    const searchResults = await searchType(itemInput);
    if (searchResults.length > 0) {
      itemName = searchResults[0].name;
      productId = searchResults[0].id;
    }
  }
  
  if (productId === 0) {
    await interaction.editReply({ content: 'Item not found.' });
    return;
  }
  
  const prices = await getJitaPrices(productId);
  
  if (!prices || (prices.buy === 0 && prices.sell === 0)) {
    await interaction.editReply({ content: 'No market data available.' });
    return;
  }
  
  const spread = prices.sell > 0 && prices.buy > 0 ? prices.sell - prices.buy : 0;
  const spreadPercent = prices.buy > 0 ? ((spread / prices.buy) * 100).toFixed(2) : '0';
  
  const embed = new EmbedBuilder()
    .setTitle(`Jita Prices: ${itemName}`)
    .setColor(0x3498db)
    .addFields(
      { name: 'Buy Orders', value: prices.buy > 0 ? `${prices.buy.toLocaleString()} ISK` : 'No orders', inline: true },
      { name: 'Sell Orders', value: prices.sell > 0 ? `${prices.sell.toLocaleString()} ISK` : 'No orders', inline: true },
      { name: 'Spread', value: spread > 0 ? `${spread.toLocaleString()} ISK (${spreadPercent}%)` : 'N/A', inline: true }
    )
    .setFooter({ text: `Type ID: ${productId}` });
  
  await interaction.editReply({ embeds: [embed] });
}

async function handleAdd(interaction: CommandInteraction) {
  const itemInput = interaction.options.get('item')?.value as string;
  const location = interaction.options.get('location')?.value as string;
  const volume = interaction.options.get('volume')?.value as number;
  const buyPrice = interaction.options.get('buy_price')?.value as number | undefined;
  const sellPrice = interaction.options.get('sell_price')?.value as number | undefined;
  
  const typeId = parseInt(itemInput);
  let itemName = itemInput;
  let productId = 0;
  
  const searchResults = await searchType(itemInput);
  if (searchResults.length > 0) {
    itemName = searchResults[0].name;
    productId = searchResults[0].id;
  }
  
  let profitMargin = 0;
  if (buyPrice && sellPrice) {
    profitMargin = ((sellPrice - buyPrice) / buyPrice) * 100;
  }
  
  const stmt = db.prepare(`
    INSERT INTO market_orders (discord_user_id, type_id, type_name, location, buy_price, sell_price, volume, profit_margin)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(
    interaction.user.id,
    productId,
    itemName,
    location,
    buyPrice || null,
    sellPrice || null,
    volume,
    profitMargin || null
  );
  
  const embed = new EmbedBuilder()
    .setTitle('Market Order Tracked')
    .setColor(0x00ff00)
    .addFields(
      { name: 'Order ID', value: result.lastInsertRowid.toString(), inline: true },
      { name: 'Item', value: `${itemName} x${volume}`, inline: true },
      { name: 'Location', value: location, inline: true }
    );
  
  if (buyPrice) embed.addFields({ name: 'Buy Price', value: `${buyPrice.toLocaleString()} ISK`, inline: true });
  if (sellPrice) embed.addFields({ name: 'Sell Price', value: `${sellPrice.toLocaleString()} ISK`, inline: true });
  if (profitMargin > 0) embed.addFields({ name: 'Margin', value: `${profitMargin.toFixed(1)}%`, inline: true });
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleOrders(interaction: CommandInteraction) {
  const status = (interaction.options.get('status')?.value as string) || 'all';
  
  let query = 'SELECT * FROM market_orders WHERE discord_user_id = ?';
  const params: (string | number)[] = [interaction.user.id];
  
  if (status !== 'all') {
    query += ' AND status = ?';
    params.push(status);
  }
  
  query += ' ORDER BY created_at DESC LIMIT 15';
  
  const orders = db.prepare(query).all(...params) as MarketOrder[];
  
  if (orders.length === 0) {
    await interaction.reply({ content: 'No orders found.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Your Market Orders')
    .setColor(0x3498db)
    .setDescription(
      orders.map(o => 
        `**#${o.id}** | ${o.type_name} x${o.volume} | ${o.location} | ${o.status}`
      ).join('\n')
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleMargin(interaction: CommandInteraction) {
  const buy = interaction.options.get('buy')?.value as number;
  const sell = interaction.options.get('sell')?.value as number;
  const volume = interaction.options.get('volume')?.value as number;
  
  const totalCost = buy * volume;
  const totalRevenue = sell * volume;
  const profit = totalRevenue - totalCost;
  const margin = (profit / totalCost) * 100;
  
  const embed = new EmbedBuilder()
    .setTitle('Profit Margin Calculator')
    .setColor(profit >= 0 ? 0x00ff00 : 0xff0000)
    .addFields(
      { name: 'Buy Price', value: `${buy.toLocaleString()} ISK`, inline: true },
      { name: 'Sell Price', value: `${sell.toLocaleString()} ISK`, inline: true },
      { name: 'Volume', value: volume.toLocaleString(), inline: true },
      { name: 'Total Cost', value: `${totalCost.toLocaleString()} ISK`, inline: true },
      { name: 'Total Revenue', value: `${totalRevenue.toLocaleString()} ISK`, inline: true },
      { name: 'Profit', value: `${profit.toLocaleString()} ISK`, inline: true },
      { name: 'Margin', value: `${margin.toFixed(2)}%`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed] });
}

async function handleCompare(interaction: CommandInteraction) {
  const itemInput = interaction.options.get('item')?.value as string;
  const yourPrice = interaction.options.get('your_price')?.value as number;
  
  await interaction.deferReply();
  
  const searchResults = await searchType(itemInput);
  if (searchResults.length === 0) {
    await interaction.editReply({ content: 'Item not found.' });
    return;
  }
  
  const itemName = searchResults[0].name;
  const productId = searchResults[0].id;
  
  const jitaPrices = await getJitaPrices(productId);
  
  if (!jitaPrices) {
    await interaction.editReply({ content: 'No market data available.' });
    return;
  }
  
  const vsBuy = jitaPrices.buy > 0 ? ((yourPrice - jitaPrices.buy) / jitaPrices.buy * 100) : 0;
  const vsSell = jitaPrices.sell > 0 ? ((yourPrice - jitaPrices.sell) / jitaPrices.sell * 100) : 0;
  
  const embed = new EmbedBuilder()
    .setTitle(`Price Comparison: ${itemName}`)
    .setColor(0xf1c40f)
    .addFields(
      { name: 'Your Price', value: `${yourPrice.toLocaleString()} ISK`, inline: true },
      { name: 'Jita Buy', value: `${jitaPrices.buy.toLocaleString()} ISK`, inline: true },
      { name: 'Jita Sell', value: `${jitaPrices.sell.toLocaleString()} ISK`, inline: true },
      { name: 'vs Jita Buy', value: `${vsBuy > 0 ? '+' : ''}${vsBuy.toFixed(1)}%`, inline: true },
      { name: 'vs Jita Sell', value: `${vsSell > 0 ? '+' : ''}${vsSell.toFixed(1)}%`, inline: true }
    );
  
  await interaction.editReply({ embeds: [embed] });
}

export async function autocomplete(interaction: AutocompleteInteraction) {
  const focusedOption = interaction.options.getFocused(true);
  
  if (focusedOption.name === 'item') {
    const searchResults = await searchType(focusedOption.value);
    await interaction.respond(
      searchResults.slice(0, 25).map(r => ({ name: r.name, value: r.name }))
    );
  }
}
