import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';
import { JFContract, JF_RATES } from '../types';
import { JITA_SYSTEM } from '../services/esi';

export const data = new SlashCommandBuilder()
  .setName('jf')
  .setDescription('Jump Freighter contract management')
  .addSubcommand(sub =>
    sub
      .setName('quote')
      .setDescription('Get a JF shipping quote')
      .addStringOption(opt => opt.setName('origin').setDescription('Origin station').setRequired(true))
      .addStringOption(opt => opt.setName('destination').setDescription('Destination station').setRequired(true))
      .addNumberOption(opt => opt.setName('volume').setDescription('Volume in m3').setRequired(true))
      .addNumberOption(opt => opt.setName('collateral').setDescription('Collateral value (ISK)').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('create')
      .setDescription('Create a JF contract request')
      .addStringOption(opt => opt.setName('origin').setDescription('Origin station').setRequired(true))
      .addStringOption(opt => opt.setName('destination').setDescription('Destination station').setRequired(true))
      .addNumberOption(opt => opt.setName('volume').setDescription('Volume in m3').setRequired(true))
      .addNumberOption(opt => opt.setName('collateral').setDescription('Collateral value (ISK)').setRequired(true))
      .addStringOption(opt => opt.setName('character').setDescription('Your character name').setRequired(true))
      .addStringOption(opt => opt.setName('notes').setDescription('Additional notes').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('list')
      .setDescription('List your JF contracts')
      .addStringOption(opt => opt.setName('status').setDescription('Filter by status').addChoices(
        { name: 'Pending', value: 'pending' },
        { name: 'In Progress', value: 'in_progress' },
        { name: 'Completed', value: 'completed' },
        { name: 'All', value: 'all' }
      ).setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('complete')
      .setDescription('Mark a contract as completed')
      .addIntegerOption(opt => opt.setName('id').setDescription('Contract ID').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('rates')
      .setDescription('Show current JF rates'))
  .addSubcommand(sub =>
    sub
      .setName('stats')
      .setDescription('Show your JF shipping statistics'));

function calculateRate(origin: string, destination: string, volume: number, collateral: number): number {
  const isJitaOrigin = origin.toLowerCase().includes('jita');
  const isJitaDest = destination.toLowerCase().includes('jita');
  
  let ratePerM3: number;
  if (isJitaOrigin || isJitaDest) {
    ratePerM3 = isJitaOrigin ? JF_RATES.jita_to_nullsec : JF_RATES.nullsec_to_jita;
  } else {
    ratePerM3 = JF_RATES.nullsec_to_nullsec;
  }
  
  let price = volume * ratePerM3;
  
  if (collateral > JF_RATES.min_collateral) {
    price += (collateral - JF_RATES.min_collateral) * 0.01;
  }
  
  return Math.max(price, JF_RATES.min_volume * ratePerM3);
}

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'quote':
      await handleQuote(interaction);
      break;
    case 'create':
      await handleCreate(interaction);
      break;
    case 'list':
      await handleList(interaction);
      break;
    case 'complete':
      await handleComplete(interaction);
      break;
    case 'rates':
      await handleRates(interaction);
      break;
    case 'stats':
      await handleStats(interaction);
      break;
  }
}

async function handleQuote(interaction: CommandInteraction) {
  const origin = interaction.options.get('origin')?.value as string;
  const destination = interaction.options.get('destination')?.value as string;
  const volume = interaction.options.get('volume')?.value as number;
  const collateral = interaction.options.get('collateral')?.value as number;
  
  const price = calculateRate(origin, destination, volume, collateral);
  
  const embed = new EmbedBuilder()
    .setTitle('Jump Freighter Quote')
    .setColor(0x00ff00)
    .addFields(
      { name: 'Route', value: `${origin} → ${destination}`, inline: false },
      { name: 'Volume', value: `${volume.toLocaleString()} m³`, inline: true },
      { name: 'Collateral', value: `${collateral.toLocaleString()} ISK`, inline: true },
      { name: 'Shipping Cost', value: `${price.toLocaleString()} ISK`, inline: true }
    )
    .setFooter({ text: 'Quote valid for 24 hours' });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleCreate(interaction: CommandInteraction) {
  const origin = interaction.options.get('origin')?.value as string;
  const destination = interaction.options.get('destination')?.value as string;
  const volume = interaction.options.get('volume')?.value as number;
  const collateral = interaction.options.get('collateral')?.value as number;
  const character = interaction.options.get('character')?.value as string;
  const notes = interaction.options.get('notes')?.value as string | undefined;
  
  const price = calculateRate(origin, destination, volume, collateral);
  
  const stmt = db.prepare(`
    INSERT INTO jf_contracts (discord_user_id, character_name, origin, destination, volume_m3, collateral, price, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(
    interaction.user.id,
    character,
    origin,
    destination,
    volume,
    collateral,
    price,
    notes || null
  );
  
  const embed = new EmbedBuilder()
    .setTitle('JF Contract Created')
    .setColor(0x00ff00)
    .addFields(
      { name: 'Contract ID', value: result.lastInsertRowid.toString(), inline: true },
      { name: 'Route', value: `${origin} → ${destination}`, inline: false },
      { name: 'Volume', value: `${volume.toLocaleString()} m³`, inline: true },
      { name: 'Collateral', value: `${collateral.toLocaleString()} ISK`, inline: true },
      { name: 'Cost', value: `${price.toLocaleString()} ISK`, inline: true },
      { name: 'Character', value: character, inline: true }
    )
    .setFooter({ text: 'Contract pending review' });
  
  await interaction.reply({ embeds: [embed] });
}

async function handleList(interaction: CommandInteraction) {
  const status = (interaction.options.get('status')?.value as string) || 'all';
  
  let query = 'SELECT * FROM jf_contracts WHERE discord_user_id = ?';
  const params: (string | number)[] = [interaction.user.id];
  
  if (status !== 'all') {
    query += ' AND status = ?';
    params.push(status);
  }
  
  query += ' ORDER BY created_at DESC LIMIT 10';
  
  const contracts = db.prepare(query).all(...params) as JFContract[];
  
  if (contracts.length === 0) {
    await interaction.reply({ content: 'No contracts found.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Your JF Contracts')
    .setColor(0x3498db)
    .setDescription(
      contracts.map(c => 
        `**#${c.id}** | ${c.origin} → ${c.destination} | ${c.volume_m3.toLocaleString()}m³ | ${c.status}`
      ).join('\n')
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleComplete(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  
  const stmt = db.prepare(`
    UPDATE jf_contracts 
    SET status = 'completed', completed_at = CURRENT_TIMESTAMP 
    WHERE id = ? AND discord_user_id = ?
  `);
  
  const result = stmt.run(id, interaction.user.id);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'Contract not found or not yours.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `Contract #${id} marked as completed.`, ephemeral: true });
}

async function handleRates(interaction: CommandInteraction) {
  const embed = new EmbedBuilder()
    .setTitle('Jump Freighter Rates')
    .setColor(0xf1c40f)
    .addFields(
      { name: 'Jita → Nullsec', value: `${JF_RATES.jita_to_nullsec} ISK/m³`, inline: true },
      { name: 'Nullsec → Jita', value: `${JF_RATES.nullsec_to_jita} ISK/m³`, inline: true },
      { name: 'Nullsec → Nullsec', value: `${JF_RATES.nullsec_to_nullsec} ISK/m³`, inline: true },
      { name: 'Min Volume', value: `${JF_RATES.min_volume.toLocaleString()} m³`, inline: true },
      { name: 'Collateral Fee', value: '1% over 500M ISK', inline: true }
    );
  
  await interaction.reply({ embeds: [embed] });
}

async function handleStats(interaction: CommandInteraction) {
  const stats = db.prepare(`
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
      SUM(CASE WHEN status = 'completed' THEN price ELSE 0 END) as total_spent,
      SUM(CASE WHEN status = 'completed' THEN volume_m3 ELSE 0 END) as total_volume
    FROM jf_contracts 
    WHERE discord_user_id = ?
  `).get(interaction.user.id) as { total: number; completed: number; total_spent: number; total_volume: number };
  
  const embed = new EmbedBuilder()
    .setTitle('Your JF Statistics')
    .setColor(0x9b59b6)
    .addFields(
      { name: 'Total Contracts', value: stats.total.toString(), inline: true },
      { name: 'Completed', value: stats.completed.toString(), inline: true },
      { name: 'Total Spent', value: `${(stats.total_spent || 0).toLocaleString()} ISK`, inline: true },
      { name: 'Total Volume', value: `${(stats.total_volume || 0).toLocaleString()} m³`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}
