import { SlashCommandBuilder, CommandInteraction, EmbedBuilder } from 'discord.js';
import db from '../database/setup';
import { PIColony, PISchematic, PI_TIERS } from '../types';

export const data = new SlashCommandBuilder()
  .setName('pi')
  .setDescription('Planetary Interaction management')
  .addSubcommand(sub =>
    sub
      .setName('add')
      .setDescription('Add a PI colony')
      .addStringOption(opt => opt.setName('character').setDescription('Character name').setRequired(true))
      .addStringOption(opt => opt.setName('planet').setDescription('Planet name (e.g., D-PN VII)').setRequired(true))
      .addStringOption(opt => opt.setName('type').setDescription('Planet type').addChoices(
        { name: 'Barren', value: 'barren' },
        { name: 'Gas', value: 'gas' },
        { name: 'Ice', value: 'ice' },
        { name: 'Lava', value: 'lava' },
        { name: 'Oceanic', value: 'oceanic' },
        { name: 'Plasma', value: 'plasma' },
        { name: 'Storm', value: 'storm' },
        { name: 'Temperate', value: 'temperate' }
      ).setRequired(true))
      .addStringOption(opt => opt.setName('system').setDescription('System name').setRequired(true))
      .addStringOption(opt => opt.setName('extraction').setDescription('Extraction type (P0/P1)').setRequired(false))
      .addStringOption(opt => opt.setName('production').setDescription('Production type (P1/P2/P3/P4)').setRequired(false))
      .addNumberOption(opt => opt.setName('setup_cost').setDescription('Setup cost (ISK)').setRequired(false))
      .addNumberOption(opt => opt.setName('daily_profit').setDescription('Expected daily profit (ISK)').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('list')
      .setDescription('List your PI colonies')
      .addStringOption(opt => opt.setName('character').setDescription('Filter by character').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('update')
      .setDescription('Update a colony')
      .addIntegerOption(opt => opt.setName('id').setDescription('Colony ID').setRequired(true))
      .addNumberOption(opt => opt.setName('daily_profit').setDescription('New daily profit').setRequired(false))
      .addStringOption(opt => opt.setName('extraction').setDescription('New extraction type').setRequired(false))
      .addStringOption(opt => opt.setName('production').setDescription('New production type').setRequired(false))
      .addStringOption(opt => opt.setName('notes').setDescription('Notes').setRequired(false))
  )
  .addSubcommand(sub =>
    sub
      .setName('delete')
      .setDescription('Delete a PI colony')
      .addIntegerOption(opt => opt.setName('id').setDescription('Colony ID').setRequired(true))
  )
  .addSubcommand(sub =>
    sub
      .setName('stats')
      .setDescription('Show your PI statistics'))
  .addSubcommand(sub =>
    sub
      .setName('profit')
      .setDescription('Calculate PI profit scenarios')
      .addStringOption(opt => opt.setName('tier').setDescription('PI Tier').addChoices(
        { name: 'P1 (Basic)', value: 'p1' },
        { name: 'P2 (Refined)', value: 'p2' },
        { name: 'P3 (Specialized)', value: 'p3' },
        { name: 'P4 (Advanced)', value: 'p4' }
      ).setRequired(true))
      .addIntegerOption(opt => opt.setName('colonies').setDescription('Number of colonies').setRequired(true))
      .addNumberOption(opt => opt.setName('price_per_unit').setDescription('Sell price per unit').setRequired(true)))
  .addSubcommand(sub =>
    sub
      .setName('schematic')
      .setDescription('Add a schematic to a colony')
      .addIntegerOption(opt => opt.setName('colony_id').setDescription('Colony ID').setRequired(true))
      .addStringOption(opt => opt.setName('type').setDescription('Schematic type').addChoices(
        { name: 'Extraction', value: 'extraction' },
        { name: 'Basic (P0→P1)', value: 'basic' },
        { name: 'Advanced (P1→P2)', value: 'advanced' },
        { name: 'High Tech (P2→P3/P4)', value: 'high_tech' }
      ).setRequired(true))
      .addStringOption(opt => opt.setName('output').setDescription('Output product name').setRequired(true))
      .addIntegerOption(opt => opt.setName('cycle_hours').setDescription('Cycle time in hours').setRequired(true))
      .addIntegerOption(opt => opt.setName('output_per_cycle').setDescription('Output per cycle').setRequired(true)));

export async function execute(interaction: CommandInteraction) {
  const subcommand = interaction.options.data[0].name;
  
  switch (subcommand) {
    case 'add':
      await handleAdd(interaction);
      break;
    case 'list':
      await handleList(interaction);
      break;
    case 'update':
      await handleUpdate(interaction);
      break;
    case 'delete':
      await handleDelete(interaction);
      break;
    case 'stats':
      await handleStats(interaction);
      break;
    case 'profit':
      await handleProfitCalc(interaction);
      break;
    case 'schematic':
      await handleSchematic(interaction);
      break;
  }
}

async function handleAdd(interaction: CommandInteraction) {
  const character = interaction.options.get('character')?.value as string;
  const planet = interaction.options.get('planet')?.value as string;
  const type = interaction.options.get('type')?.value as string;
  const system = interaction.options.get('system')?.value as string;
  const extraction = interaction.options.get('extraction')?.value as string | undefined;
  const production = interaction.options.get('production')?.value as string | undefined;
  const setupCost = (interaction.options.get('setup_cost')?.value as number) || 0;
  const dailyProfit = (interaction.options.get('daily_profit')?.value as number) || 0;
  
  const planetId = Math.floor(Math.random() * 1000000);
  
  const stmt = db.prepare(`
    INSERT INTO pi_colonies 
    (discord_user_id, character_name, planet_id, planet_name, planet_type, system, extraction_type, production_type, setup_cost, daily_profit)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(
    interaction.user.id,
    character,
    planetId,
    planet,
    type,
    system,
    extraction || null,
    production || null,
    setupCost,
    dailyProfit
  );
  
  const embed = new EmbedBuilder()
    .setTitle('PI Colony Added')
    .setColor(0x00ff00)
    .addFields(
      { name: 'Colony ID', value: result.lastInsertRowid.toString(), inline: true },
      { name: 'Planet', value: `${planet} (${type})`, inline: true },
      { name: 'System', value: system, inline: true },
      { name: 'Character', value: character, inline: true },
      { name: 'Setup Cost', value: `${setupCost.toLocaleString()} ISK`, inline: true },
      { name: 'Daily Profit', value: `${dailyProfit.toLocaleString()} ISK`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleList(interaction: CommandInteraction) {
  const character = interaction.options.get('character')?.value as string | undefined;
  
  let query = 'SELECT * FROM pi_colonies WHERE discord_user_id = ?';
  const params: (string)[] = [interaction.user.id];
  
  if (character) {
    query += ' AND character_name = ?';
    params.push(character);
  }
  
  query += ' ORDER BY daily_profit DESC';
  
  const colonies = db.prepare(query).all(...params) as PIColony[];
  
  if (colonies.length === 0) {
    await interaction.reply({ content: 'No PI colonies found.', ephemeral: true });
    return;
  }
  
  const embed = new EmbedBuilder()
    .setTitle('Your PI Colonies')
    .setColor(0x3498db)
    .setDescription(
      colonies.map(c => 
        `**#${c.id}** | ${c.planet_name} (${c.planet_type}) | ${c.system} | ${(c.daily_profit || 0).toLocaleString()} ISK/day`
      ).join('\n')
    );
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleUpdate(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  const dailyProfit = interaction.options.get('daily_profit')?.value as number | undefined;
  const extraction = interaction.options.get('extraction')?.value as string | undefined;
  const production = interaction.options.get('production')?.value as string | undefined;
  const notes = interaction.options.get('notes')?.value as string | undefined;
  
  const updates: string[] = [];
  const values: (number | string)[] = [];
  
  if (dailyProfit !== undefined) {
    updates.push('daily_profit = ?');
    values.push(dailyProfit);
  }
  if (extraction !== undefined) {
    updates.push('extraction_type = ?');
    values.push(extraction);
  }
  if (production !== undefined) {
    updates.push('production_type = ?');
    values.push(production);
  }
  if (notes !== undefined) {
    updates.push('notes = ?');
    values.push(notes);
  }
  
  if (updates.length === 0) {
    await interaction.reply({ content: 'No updates provided.', ephemeral: true });
    return;
  }
  
  updates.push('last_updated = CURRENT_TIMESTAMP');
  values.push(id, interaction.user.id);
  
  const stmt = db.prepare(`UPDATE pi_colonies SET ${updates.join(', ')} WHERE id = ? AND discord_user_id = ?`);
  const result = stmt.run(...values);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'Colony not found or not yours.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `Colony #${id} updated.`, ephemeral: true });
}

async function handleDelete(interaction: CommandInteraction) {
  const id = interaction.options.get('id')?.value as number;
  
  const result = db.prepare('DELETE FROM pi_colonies WHERE id = ? AND discord_user_id = ?')
    .run(id, interaction.user.id);
  
  if (result.changes === 0) {
    await interaction.reply({ content: 'Colony not found or not yours.', ephemeral: true });
    return;
  }
  
  await interaction.reply({ content: `Colony #${id} deleted.`, ephemeral: true });
}

async function handleStats(interaction: CommandInteraction) {
  const stats = db.prepare(`
    SELECT 
      COUNT(*) as total_colonies,
      COUNT(DISTINCT character_name) as characters,
      SUM(setup_cost) as total_setup,
      SUM(daily_profit) as daily_profit,
      COUNT(CASE WHEN planet_type = 'plasma' THEN 1 END) as plasma_count,
      COUNT(CASE WHEN planet_type = 'gas' THEN 1 END) as gas_count
    FROM pi_colonies 
    WHERE discord_user_id = ?
  `).get(interaction.user.id) as { 
    total_colonies: number; 
    characters: number; 
    total_setup: number; 
    daily_profit: number;
    plasma_count: number;
    gas_count: number;
  };
  
  const monthlyProfit = (stats.daily_profit || 0) * 30;
  const yearlyProfit = monthlyProfit * 12;
  
  const embed = new EmbedBuilder()
    .setTitle('Your PI Statistics')
    .setColor(0x9b59b6)
    .addFields(
      { name: 'Total Colonies', value: stats.total_colonies.toString(), inline: true },
      { name: 'Characters', value: stats.characters.toString(), inline: true },
      { name: 'Setup Investment', value: `${(stats.total_setup || 0).toLocaleString()} ISK`, inline: true },
      { name: 'Daily Profit', value: `${(stats.daily_profit || 0).toLocaleString()} ISK`, inline: true },
      { name: 'Monthly Profit', value: `${monthlyProfit.toLocaleString()} ISK`, inline: true },
      { name: 'Yearly Profit', value: `${yearlyProfit.toLocaleString()} ISK`, inline: true }
    );
  
  if (stats.total_colonies > 0) {
    embed.addFields(
      { name: 'Best Producers', value: `Plasma: ${stats.plasma_count}, Gas: ${stats.gas_count}`, inline: true }
    );
  }
  
  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleProfitCalc(interaction: CommandInteraction) {
  const tier = interaction.options.get('tier')?.value as string;
  const colonies = interaction.options.get('colonies')?.value as number;
  const pricePerUnit = interaction.options.get('price_per_unit')?.value as number;
  
  const tierInfo = PI_TIERS[tier as keyof typeof PI_TIERS];
  
  let cyclesPerDay: number;
  let unitsPerCycle: number;
  
  switch (tier) {
    case 'p1':
      cyclesPerDay = 24;
      unitsPerCycle = 20;
      break;
    case 'p2':
      cyclesPerDay = 6;
      unitsPerCycle = 5;
      break;
    case 'p3':
      cyclesPerDay = 1;
      unitsPerCycle = 3;
      break;
    case 'p4':
      cyclesPerDay = 0.5;
      unitsPerCycle = 1;
      break;
    default:
      cyclesPerDay = 1;
      unitsPerCycle = 1;
  }
  
  const dailyUnits = cyclesPerDay * unitsPerCycle * colonies;
  const dailyRevenue = dailyUnits * pricePerUnit;
  const monthlyRevenue = dailyRevenue * 30;
  
  const embed = new EmbedBuilder()
    .setTitle('PI Profit Calculator')
    .setColor(0xf1c40f)
    .addFields(
      { name: 'Tier', value: tierInfo.name, inline: true },
      { name: 'Colonies', value: colonies.toString(), inline: true },
      { name: 'Price/Unit', value: `${pricePerUnit.toLocaleString()} ISK`, inline: true },
      { name: 'Units/Day', value: dailyUnits.toLocaleString(), inline: true },
      { name: 'Daily Revenue', value: `${dailyRevenue.toLocaleString()} ISK`, inline: true },
      { name: 'Monthly Revenue', value: `${monthlyRevenue.toLocaleString()} ISK`, inline: true }
    );
  
  await interaction.reply({ embeds: [embed] });
}

async function handleSchematic(interaction: CommandInteraction) {
  const colonyId = interaction.options.get('colony_id')?.value as number;
  const type = interaction.options.get('type')?.value as string;
  const output = interaction.options.get('output')?.value as string;
  const cycleHours = interaction.options.get('cycle_hours')?.value as number;
  const outputPerCycle = interaction.options.get('output_per_cycle')?.value as number;
  
  const colony = db.prepare('SELECT * FROM pi_colonies WHERE id = ? AND discord_user_id = ?')
    .get(colonyId, interaction.user.id) as PIColony | undefined;
  
  if (!colony) {
    await interaction.reply({ content: 'Colony not found or not yours.', ephemeral: true });
    return;
  }
  
  const stmt = db.prepare(`
    INSERT INTO pi_schematics (colony_id, schematic_type, output_type, cycle_time_hours, output_per_cycle)
    VALUES (?, ?, ?, ?, ?)
  `);
  
  const result = stmt.run(colonyId, type, output, cycleHours, outputPerCycle);
  
  await interaction.reply({ 
    content: `Schematic added to colony #${colonyId}: ${type} → ${output} (${outputPerCycle}/cycle, ${cycleHours}h)`, 
    ephemeral: true 
  });
}
