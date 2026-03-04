import { SlashCommandBuilder, CommandInteraction, EmbedBuilder, AutocompleteInteraction } from 'discord.js';
import db from '../database/setup';
import { IndustryJob } from '../types';
import { getTypeInfo, searchType, getJitaPrices } from '../services/esi';

export const data = new SlashCommandBuilder()
  .setName('industry')
  .setDescription('Industry job tracking and profit calculation')
  .addSubcommand(sub =>
    sub
      .setName('add')
      .setDescription('Add an industry job')
      .addStringOption(opt => opt.setName('product').setDescription('Product name or type ID').setRequired(true).setAutocomplete(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity to build').setRequired(true))
      .addNumberOption(opt => opt.setName('material_cost').setDescription('Total material cost (ISK)').setRequired(true))
      .addStringOption(opt => opt.setName('character').setDescription('Character name').setRequired(true))
      .addStringOption(opt => opt.setName('blueprint').setDescription('Blueprint type (BPO/BPC)').addChoices(
        { name: 'BPO', value: 'BPO' },
        { name: 'BPC', value: 'BPC' }
      ).setRequired(false))
      .addStringOption(opt => opt.setName('location').setDescription('Manufacturing location').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('list')
      .setDescription('List your industry jobs')
      .addStringOption(opt => opt.setName('status').setDescription('Filter by status').addChoices(
        { name: 'Pending', value: 'pending' },
        { name: 'Building', value: 'building' },
        { name: 'Completed', value: 'completed' },
        { name: 'Sold', value: 'sold' },
        { name: 'All', value: 'all' }
      ).setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('complete')
      .setDescription('Mark a job as completed')
      .addIntegerOption(opt => opt.setName('id').setDescription('Job ID').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('sell')
      .setDescription('Mark a job as sold and record profit')
      .addIntegerOption(opt => opt.setName('id').setDescription('Job ID').setRequired(true))
      .addNumberOption(opt => opt.setName('price').setDescription('Total sale price (ISK)').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('profit')
      .setDescription('Calculate profit for a product')
      .addStringOption(opt => opt.setName('product').setDescription('Product name').setRequired(true).setAutocomplete(true))
      .addIntegerOption(opt => opt.setName('quantity').setDescription('Quantity').setRequired(true))
      .addNumberOption(opt => opt.setName('material_cost').setDescription('Material cost per unit').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('stats')
      .setDescription('Show your industry profit statistics'))
  .addSubcommand(sub =>
    sub
      .setName('delete')
      .setDescription('Delete an industry job')
      .addIntegerOption(opt => opt.setName('id').setDescription('Job ID').setRequired(true)));

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  if (subcommand === 'add') {
    await handleAdd(interaction);
  } else if (subcommand === 'list') {
    await handleList(interaction);
  } else if (subcommand === 'complete') {
    await handleComplete(interaction);
  } else if (subcommand === 'sell') {
    await handleSell(interaction);
  } else if (subcommand === 'profit') {
    await handleProfit(interaction);
  } else if (subcommand === 'stats') {
    await handleStats(interaction);
  } else if (subcommand === 'delete') {
    await handleDelete(interaction);
  }
}

async function handleAdd(interaction: CommandInteraction) {
  const productInput = interaction.options.get('product')?.value as string;
  const quantity = interaction.options.get('quantity')?.value as number;
  const materialCost = interaction.options.get('material_cost')?.value as number;
  const character = interaction.options.get('character')?.value as string;
  const blueprint = (interaction.options.get('blueprint')?.value as string) || 'BPC';
  const location = (interaction.options.get('location')?.value as string) || 'Unknown';
  
  const typeId = parseInt(productInput);
  let productName = productInput;
  let productId = 0;
  
  if (!isNaN(typeId)) {
    const typeInfo = await getTypeInfo(typeId);
    if (typeInfo) {
      productName = typeInfo.name;
      productId = typeId;
    }
  } else {
    const searchResults = await searchType(productInput);
    if (searchResults.length > 0) {
      productName = searchResults[0].name;
      productId = searchResults[0].id;
    }
  }
  
  const stmt = db.prepare(`
    INSERT INTO industry_jobs 
    (discord_user_id, character_name, blueprint_type, product_type_id, product_name, quantity, material_cost, location)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(
    interaction.user.id,
    character,
    blueprint,
    productId,
    productName,
    quantity,
    materialCost,
    location
  );
  
  const costPerUnit = materialCost / quantity;
  
  const embed = new EmbedBuilder()
    .setTitle('Industry Job Added')
    .setColor(0x3498db)
    .addFields(
      { name: 'Job ID', value: result.lastInsertRowid.toString(), inline: true },
      { name: 'Product', value: `${productName} x${quantity}`, inline: true },
      { name: 'Blueprint', value: blueprint, inline: true },
      { name: 'Material Cost', value: `${materialCost.toLocaleString()} ISK`, inline: true },
      { name: 'Cost/Unit', value: `${costPerUnit.toLocaleString()} ISK`, inline: true },
      { name: 'Location', value: location, inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleList(interaction: CommandInteraction) {
  const status = (interaction.options.get('status')?.value as string) || 'all';
  
  let query = 'SELECT * FROM industry_jobs WHERE discord_user_id = ?';
  const params: (string | number)[] = [interaction.user.id];
  
  if (status !== 'all') {
    query += ' AND status = ?';
    params.push(status);
  }
  
  query += ' ORDER BY started_at DESC LIMIT 15';
  
  const jobs = db.prepare(query).all(...params) as IndustryJob[];
  
  if (jobs.length === 0) {
    await interaction.reply({ content: 'No industry jobs found.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Your Industry Jobs')
    .setColor(0x3498db)
    .setDescription(
      jobs.map(j => 
        `**#${j.id}** | ${j.product_name} x${j.quantity} | ${(j.material_cost || 0).toLocaleString()} ISK | ${j.status}`
      ).join('\n')
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleComplete(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  
  const stmt = db.prepare(`
    UPDATE industry_jobs 
    SET status = 'completed', completed_at = CURRENT_TIMESTAMP 
    WHERE id = ? AND discord_user_id = ?
  `);
  
  const result = stmt.run(id, interaction.user.id);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'Job not found or not yours.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `Job #${id} marked as completed.`, ephemeral: true });
}

async function handleSell(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  const sellPrice = interaction.options.get('price')?.value as number;
  
  const job = db.prepare('SELECT * FROM industry_jobs WHERE id = ? AND discord_user_id = ?')
    .get(id, interaction.user.id) as IndustryJob | undefined;
  
  if (!job) {
    await interaction.reply({ content: 'Job not found or not yours.', ephemeral: true });
    return;
  }
  
  const profit = sellPrice - job.material_cost;
  
  const stmt = db.prepare(`
    UPDATE industry_jobs 
    SET status = 'sold', sell_price = ?, profit = ?, completed_at = CURRENT_TIMESTAMP 
    WHERE id = ?
  `);
  
  stmt.run(sellPrice, profit, id);
  
  const embed = new EmbedBuilder()
    .setTitle('Sale Recorded')
    .setColor(profit >= 0 ? 0x00ff00 : 0xff0000)
    .addFields(
      { name: 'Product', value: `${job.product_name} x${job.quantity}`, inline: true },
      { name: 'Material Cost', value: `${job.material_cost.toLocaleString()} ISK`, inline: true },
      { name: 'Sale Price', value: `${sellPrice.toLocaleString()} ISK`, inline: true },
      { name: 'Profit', value: `${profit.toLocaleString()} ISK`, inline: true },
      { name: 'Margin', value: `${((profit / job.material_cost) * 100).toFixed(1)}%`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleProfit(interaction: CommandInteraction) {
  const productInput = interaction.options.get('product')?.value as string;
  const quantity = interaction.options.get('quantity')?.value as number;
  const materialCost = interaction.options.get('material_cost')?.value as number;
  
  const typeId = parseInt(productInput);
  let productName = productInput;
  let productId = 0;
  
  if (!isNaN(typeId)) {
    const typeInfo = await getTypeInfo(typeId);
    if (typeInfo) {
      productName = typeInfo.name;
      productId = typeId;
    }
  } else {
    const searchResults = await searchType(productInput);
    if (searchResults.length > 0) {
      productName = searchResults[0].name;
      productId = searchResults[0].id;
    }
  }
  
  let jitaSell = 0;
  if (productId > 0) {
    const prices = await getJitaPrices(productId);
    if (prices) {
      jitaSell = prices.sell;
    }
  }
  
  const totalMaterialCost = materialCost * quantity;
  const estimatedRevenue = jitaSell > 0 ? jitaSell * quantity : null;
  const estimatedProfit = estimatedRevenue ? estimatedRevenue - totalMaterialCost : null;
  
  const embed = new EmbedBuilder()
    .setTitle('Profit Calculator')
    .setColor(0xf1c40f)
    .addFields(
      { name: 'Product', value: `${productName} x${quantity}`, inline: true },
      { name: 'Material Cost', value: `${totalMaterialCost.toLocaleString()} ISK`, inline: true },
      { name: 'Cost/Unit', value: `${materialCost.toLocaleString()} ISK`, inline: true }
    );
  
  if (estimatedRevenue && estimatedProfit) {
    embed.addFields(
      { name: 'Jita Sell Price', value: `${jitaSell.toLocaleString()} ISK/unit`, inline: true },
      { name: 'Est. Revenue', value: `${estimatedRevenue.toLocaleString()} ISK`, inline: true },
      { name: 'Est. Profit', value: `${estimatedProfit.toLocaleString()} ISK`, inline: true },
      { name: 'Est. Margin', value: `${((estimatedProfit / totalMaterialCost) * 100).toFixed(1)}%`, inline: true }
    );
  }
  
  await interaction.reply({ embeds: [embed] });
}

async function handleStats(interaction: CommandInteraction) {
  const stats = db.prepare(`
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN status = 'sold' THEN 1 ELSE 0 END) as sold,
      SUM(CASE WHEN status = 'sold' THEN material_cost ELSE 0 END) as total_cost,
      SUM(profit) as total_profit
    FROM industry_jobs 
    WHERE discord_user_id = ?
  `).get(interaction.user.id) as { total: number; sold: number; total_cost: number; total_profit: number };
  
  const embed = new EmbedBuilder()
    .setTitle('Your Industry Statistics')
    .setColor(0x9b59b6)
    .addFields(
      { name: 'Total Jobs', value: stats.total.toString(), inline: true },
      { name: 'Sold', value: (stats.sold || 0).toString(), inline: true },
      { name: 'Total Material Cost', value: `${(stats.total_cost || 0).toLocaleString()} ISK`, inline: true },
      { name: 'Total Profit', value: `${(stats.total_profit || 0).toLocaleString()} ISK`, inline: true },
      { name: 'Avg Margin', value: stats.total_cost > 0 ? 
        `${(((stats.total_profit || 0) / stats.total_cost) * 100).toFixed(1)}%` : 'N/A', inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleDelete(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  
  const result = db.prepare('DELETE FROM industry_jobs WHERE id = ? AND discord_user_id = ?')
    .run(id, interaction.user.id);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'Job not found or not yours.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `Job #${id} deleted.`, ephemeral: true });
}

export async function autocomplete(interaction: AutocompleteInteraction) {
  const focusedOption = interaction.options.getFocused(true);
  
  if (focusedOption.name === 'product') {
    const searchResults = await searchType(focusedOption.value);
    await interaction.respond(
      searchResults.slice(0, 25).map(r => ({ name: r.name, value: r.name }))
    );
  }
}
